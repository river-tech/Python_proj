import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist
from django.db import models
from django.db.models import Q
from .models import Movie
import re
import random

# Global variables for caching model and embeddings
_semantic_model = None
_movie_embeddings = None
_movie_ids = None
_faiss_index = None
_max_rating = None

def get_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _semantic_model

def load_embeddings():
    global _movie_embeddings, _movie_ids, _faiss_index, _max_rating
    if _movie_embeddings is None or _movie_ids is None:
        filepath = os.path.join('data', 'movie_embeddings.pkl')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                _movie_ids = data['movie_ids']
                _movie_embeddings = data['embeddings']
                _max_rating = data.get('max_rating', 10.0)
        else:
            _movie_ids = []
            _movie_embeddings = np.array([])

    # Build FAISS index if not already built
    if _faiss_index is None and len(_movie_ids) > 0:
        try:
            import faiss
            emb = np.array(_movie_embeddings).astype('float32')
            faiss.normalize_L2(emb)
            index = faiss.IndexFlatIP(emb.shape[1])
            index.add(emb)
            _faiss_index = index
            # store normalized embeddings for lookup
            _movie_embeddings = emb
        except ImportError:
            pass  # faiss not installed, fall back gracefully

    return _movie_ids, _movie_embeddings, _faiss_index, _max_rating

def semantic_search(query, top_k=20):
    if not query:
        return Movie.objects.none()

    # --- 1. Keyword matches: always include movies whose title contains the query ---
    keyword_qs = Movie.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(ai_metadata__icontains=query)
    )
    keyword_ids = list(keyword_qs.values_list('id', flat=True))

    model = get_semantic_model()
    ids, embeddings, _, __ = load_embeddings()

    if len(ids) == 0:
        # No embeddings available — return keyword results only
        return keyword_qs

    # --- 2. Semantic matches ---
    query_embedding = model.encode([query])
    distances = cdist(query_embedding, embeddings, metric='cosine')[0]
    top_indices = np.argsort(distances)[:top_k]
    semantic_ids = [ids[idx] for idx in top_indices]

    # --- 3. Merge: keyword matches first, then semantic (deduplicated) ---
    seen = set(keyword_ids)
    merged_ids = list(keyword_ids)
    for mid in semantic_ids:
        if mid not in seen:
            seen.add(mid)
            merged_ids.append(mid)

    preserved_order = models.Case(
        *[models.When(pk=pk, then=pos) for pos, pk in enumerate(merged_ids)]
    )
    return Movie.objects.filter(id__in=merged_ids).order_by(preserved_order)

def analyze_sentiment(text):
    """
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    if not text:
        return 'Neutral'
    
    # Simple rule-based fallback if no ML library
    text_lower = text.lower()
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'fantastic', 'sublime', 'cool', 'nice', 'masterpiece', 'wonderful']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'boring', 'slow', 'waste', 'stupid', 'horrible', 'trash', 'disappointing']
    
    pos_score = sum(1 for word in positive_words if word in text_lower)
    neg_score = sum(1 for word in negative_words if word in text_lower)
    
    if pos_score > neg_score:
        return 'Positive'
    elif neg_score > pos_score:
        return 'Negative'
    else:
        return 'Neutral'

def calculate_similarity(text1, text2):
    """
    Calculate Jaccard similarity between two texts.
    """
    if not text1 or not text2:
        return 0.0
        
    def tokenize(text):
        return set(re.findall(r'\w+', text.lower()))
    
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    return intersection / union if union > 0 else 0.0

def get_recommendations(movie_id=None, top_n=5):
    """
    Get movie recommendations using FAISS vector search (from recommendation.ipynb).
    Finds nearest neighbors by cosine similarity, then re-ranks with:
        final_score = 0.7 * cosine_similarity + 0.3 * (rating / max_rating)
    Falls back to genre+Jaccard if FAISS is unavailable.
    """
    if not movie_id:
        return list(Movie.objects.order_by('?')[:top_n])

    try:
        target_movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return []

    ids, embeddings, index, max_rating = load_embeddings()

    # --- FAISS path ---
    if index is not None and movie_id in ids:
        import faiss

        idx = ids.index(movie_id)
        query_vec = embeddings[idx].reshape(1, -1).copy()
        faiss.normalize_L2(query_vec)

        # Fetch top_n + 1 to skip self
        n_search = top_n + 1
        similarity_scores, faiss_indices = index.search(query_vec, n_search)
        similarity_scores = similarity_scores[0]
        faiss_indices = faiss_indices[0]

        max_rating = max_rating or 10.0

        weighted = []
        for faiss_idx, sim_score in zip(faiss_indices, similarity_scores):
            if faiss_idx < 0 or faiss_idx >= len(ids):
                continue
            candidate_id = ids[faiss_idx]
            if candidate_id == movie_id:
                continue
            try:
                candidate = Movie.objects.get(id=candidate_id)
            except Movie.DoesNotExist:
                continue
            rating_score = float(candidate.rating or 0) / float(max_rating)
            final_score = 0.7 * float(sim_score) + 0.3 * rating_score
            weighted.append((candidate, final_score))

        weighted.sort(key=lambda x: x[1], reverse=True)
        recommendations = [item[0] for item in weighted[:top_n]]

        # Fill any gaps with high-rated movies
        if len(recommendations) < top_n:
            exclude_ids = [m.id for m in recommendations] + [movie_id]
            others = Movie.objects.exclude(id__in=exclude_ids).order_by('-rating')[:top_n - len(recommendations)]
            recommendations.extend(others)

        return recommendations

    # --- Fallback: Genre + Jaccard similarity ---
    target_genres = target_movie.genres.all()
    candidates = Movie.objects.filter(genres__in=target_genres).exclude(id=movie_id).distinct()

    scored_candidates = []
    target_meta = f"{target_movie.title} {target_movie.ai_metadata or ''}"

    for candidate in candidates:
        candidate_meta = f"{candidate.title} {candidate.ai_metadata or ''}"
        similarity = calculate_similarity(target_meta, candidate_meta)
        score = similarity * (float(candidate.rating) or 5.0)
        scored_candidates.append((candidate, score))

    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    recommendations = [item[0] for item in scored_candidates[:top_n]]

    if len(recommendations) < top_n:
        exclude_ids = [m.id for m in recommendations] + [movie_id]
        others = Movie.objects.exclude(id__in=exclude_ids).order_by('-rating')[:top_n - len(recommendations)]
        recommendations.extend(others)

    return recommendations
