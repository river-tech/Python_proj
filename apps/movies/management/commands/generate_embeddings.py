import os
import pickle
from django.core.management.base import BaseCommand
from apps.movies.models import Movie
from sentence_transformers import SentenceTransformer

class Command(BaseCommand):
    help = 'Generate semantic embeddings for all movies and save them to a file.'

    def handle(self, *args, **options):
        self.stdout.write("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
        # Load a pre-trained model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        movies = Movie.objects.all()
        if not movies.exists():
            self.stdout.write(self.style.WARNING("No movies found in the database."))
            return

        self.stdout.write(f"Found {movies.count()} movies. Generating embeddings...")
        
        movie_ids = []
        texts = []
        
        for movie in movies:
            movie_ids.append(movie.id)
            # Combine relevant fields to form a rich text description
            title = movie.title or ""
            desc = movie.description or ""
            ai_meta = movie.ai_metadata or ""
            
            # Form a single chunk of text for this movie
            text = f"{title}. {desc} {ai_meta}".strip()
            texts.append(text)
            
        # Generate embeddings
        # This will return a numpy matrix of shape (num_movies, embedding_dim)
        self.stdout.write("Encoding texts (this may take a few minutes)...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Save to disk
        data_dir = os.path.join('data')
        os.makedirs(data_dir, exist_ok=True)
        out_path = os.path.join(data_dir, 'movie_embeddings.pkl')
        
        with open(out_path, 'wb') as f:
            pickle.dump({
                'movie_ids': movie_ids,
                'embeddings': embeddings
            }, f)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully saved embeddings to {out_path}"))
