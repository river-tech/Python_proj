import random
from django.db.models import Q
from .models import Movie
import re

def analyze_sentiment(text):
    """
    Analyze sentiment of the text.
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
    Get movie recommendations.
    If movie_id is provided, find similar movies using Hybrid Filtering (Genre + Content-based AI Metadata).
    """
    if not movie_id:
        # Default: Return random movies or top rated
        return list(Movie.objects.order_by('?')[:top_n])

    try:
        target_movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return []

    # 1. Candidate Generation: Movies with same genres
    target_genres = target_movie.genres.all()
    candidates = Movie.objects.filter(genres__in=target_genres).exclude(id=movie_id).distinct()
    
    # 2. Ranking: Use AI Metadata similarity
    scored_candidates = []
    
    target_meta = f"{target_movie.title} {target_movie.ai_metadata or ''}"
    
    for candidate in candidates:
        candidate_meta = f"{candidate.title} {candidate.ai_metadata or ''}"
        
        # Calculate similarity score
        similarity = calculate_similarity(target_meta, candidate_meta)
        
        # Boost score if rating is high
        score = similarity * (float(candidate.rating) or 5.0)
        
        scored_candidates.append((candidate, score))
    
    # Sort by score descending
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N movies
    recommendations = [item[0] for item in scored_candidates[:top_n]]
    
    # If not enough recommendations, fill with other high-rated movies
    if len(recommendations) < top_n:
        img_ids = [m.id for m in recommendations] + [movie_id]
        others = Movie.objects.exclude(id__in=img_ids).order_by('-rating')[:top_n - len(recommendations)]
        recommendations.extend(others)
        
    return recommendations
