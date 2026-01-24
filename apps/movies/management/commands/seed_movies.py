from django.core.management.base import BaseCommand
from apps.movies.models import Genre, Movie, Review
from django.utils.text import slugify
from datetime import date
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial movie data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # 1. Genres
        genres_data = ['Action', 'Sci-Fi', 'Drama', 'Comedy', 'Thriller', 'Romance', 'Horror', 'Adventure']
        genres = {}
        for name in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)}
            )
            genres[name] = genre
        self.stdout.write(f'Created {len(genres)} genres')
        
        # 2. Movies
        movies_data = [
            {
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'release_date': date(2010, 7, 16),
                'duration': 148,
                'rating': 8.8,
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SY1000_CR0,0,675,1000_AL_.jpg',
                'genres': ['Action', 'Sci-Fi', 'Thriller'],
                'ai_metadata': 'Dream manipulation, heist, complex plot, mind-bending, surreal visual effects',
            },
            {
                'title': 'The Dark Knight',
                'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
                'release_date': date(2008, 7, 18),
                'duration': 152,
                'rating': 9.0,
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SY1000_CR0,0,675,1000_AL_.jpg',
                'genres': ['Action', 'Drama', 'Thriller'],
                'ai_metadata': 'Superhero, gritty, crime, chaos, psychological thriller, vigilante',
            },
            {
                'title': 'Interstellar',
                'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
                'release_date': date(2014, 11, 7),
                'duration': 169,
                'rating': 8.6,
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SY1000_CR0,0,675,1000_AL_.jpg',
                'genres': ['Adventure', 'Drama', 'Sci-Fi'],
                'ai_metadata': 'Space exploration, time dilation, black hole, father-daughter relationship, loop quantum gravity',
            },
            {
                'title': 'Parasite',
                'description': 'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.',
                'release_date': date(2019, 5, 30),
                'duration': 132,
                'rating': 8.6,
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_SY1000_CR0,0,675,1000_AL_.jpg',
                'genres': ['Drama', 'Thriller', 'Comedy'],
                'ai_metadata': 'Class struggle, social commentary, dark comedy, twist ending, architectural symbolism',
            },
            {
                'title': 'Avengers: Endgame',
                'description': 'After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos\' actions and restore balance to the universe.',
                'release_date': date(2019, 4, 26),
                'duration': 181,
                'rating': 8.4,
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SY1000_CR0,0,674,1000_AL_.jpg',
                'genres': ['Action', 'Adventure', 'Sci-Fi'],
                'ai_metadata': 'Superheroes, time travel, epic battle, team ensemble, emotional closure',
            }
        ]
        
        for m_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=m_data['title'],
                defaults={
                    'slug': slugify(m_data['title']),
                    'description': m_data['description'],
                    'release_date': m_data['release_date'],
                    'duration': m_data['duration'],
                    'rating': m_data['rating'],
                    'poster_url': m_data['poster_url'],
                    'ai_metadata': m_data['ai_metadata']
                }
            )
            
            # Add genres
            for g_name in m_data['genres']:
                if g_name in genres:
                    movie.genres.add(genres[g_name])
            
            self.stdout.write(f'Processed movie: {movie.title}')
            
            # Add some dummy reviews
            if created:
                Review.objects.create(
                    movie=movie,
                    user_name='User123',
                    comment='This is an absolute masterpiece! Highly recommended.',
                    rating=9,
                    sentiment_label='Positive'
                )
                Review.objects.create(
                    movie=movie,
                    user_name='CriticChoice',
                    comment='Good visuals but the pacing was a bit off.',
                    rating=7,
                    sentiment_label='Neutral'
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
