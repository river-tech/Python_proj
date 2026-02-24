import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.movies.models import Genre, Movie
from django.db import transaction

class Command(BaseCommand):
    help = 'Imports movies from a CSV file into the PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Absolute or relative path to the CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        
        self.stdout.write(self.style.NOTICE(f'Starting data import from {csv_path}...'))
        
        try:
            self.stdout.write(self.style.NOTICE('Clearing old data...'))
            Movie.objects.all().delete()
            Genre.objects.all().delete()
            
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.stdout.write(self.style.NOTICE('1. Scanning and importing Genres...'))
                all_genre_names = set()
                
                # Fetch all existing genres first to avoid DB hits
                for row in reader:
                    raw_genres = row.get('genres', '').strip()
                    if raw_genres:
                        genre_names = [g.strip().replace('"', '') for g in raw_genres.split(',') if g.strip()]
                        for name in genre_names:
                            all_genre_names.add(name)
                
                # Bulk create Genres
                genres_to_create = [
                    Genre(name=name, slug=slugify(name)[:120])
                    for name in all_genre_names
                ]
                Genre.objects.bulk_create(genres_to_create, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(f'Imported {len(all_genre_names)} distinct genres.'))
                
                # Fetch back all genres into a dictionary cache
                genre_cache = {g.name: g for g in Genre.objects.all()}
                
                # Reset file pointer for the second pass (Movies)
                file.seek(0)
                reader = csv.DictReader(file)
                self.stdout.write(self.style.NOTICE('2. Importing Movies and mapping M2M...'))
                
                movies_to_create = []

                BatchSize = 1000
                total_processed = 0
                
                for row in reader:
                    title = row.get('title', '').strip()
                    if not title:
                        continue
                        
                    tmdb_id_str = row.get('id', '').strip()
                    tmdb_id = int(tmdb_id_str) if tmdb_id_str.isdigit() else None
                    
                    slug_base = f"{title}-{tmdb_id_str}" if tmdb_id_str else f"{title}-{total_processed}"
                    slug = slugify(slug_base)[:255]

                    description = row.get('description', '').strip()
                    original_language = row.get('original_language', '').strip()
                    
                    release_date = None
                    raw_date = row.get('release_date', '').strip()
                    if raw_date:
                        try:
                            release_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                            
                    duration = None
                    raw_duration = row.get('duration', '').strip()
                    if raw_duration:
                        try:
                            duration = int(float(raw_duration))
                        except ValueError:
                            pass
                            
                    rating = 0.0
                    raw_rating = row.get('rating', '').strip()
                    if raw_rating:
                        try:
                            rating = round(float(raw_rating), 1)
                        except ValueError:
                            pass
                            
                    poster_path = ''
                    raw_poster = row.get('poster_path', '').strip()
                    if raw_poster:
                        poster_path = f"https://image.tmdb.org/t/p/w500{raw_poster}"
                        
                    movie_obj = Movie(
                        slug=slug,
                        tmdb_id=tmdb_id,
                        title=title,
                        original_language=original_language,
                        description=description,
                        release_date=release_date,
                        duration=duration,
                        rating=rating,
                        poster_path=poster_path
                    )
                    
                    # Store for bulk create
                    movies_to_create.append(movie_obj)
                    
                    # Prep genres (to be linked after Movie creation)
                    raw_genres = row.get('genres', '').strip()
                    temp_genres = []
                    if raw_genres:
                        genre_names = [g.strip().replace('"', '') for g in raw_genres.split(',') if g.strip()]
                        for name in genre_names:
                            if name in genre_cache:
                                temp_genres.append(genre_cache[name])
                    
                    movie_obj._temp_genres = temp_genres
                    total_processed += 1
                    
                    if len(movies_to_create) >= BatchSize:
                        with transaction.atomic():
                            # 1. Bulk create movies
                            Movie.objects.bulk_create(movies_to_create, ignore_conflicts=True)
                            
                            # 2. Re-fetch saved movies
                            slugs_in_batch = [m.slug for m in movies_to_create]
                            saved_movies = Movie.objects.filter(slug__in=slugs_in_batch)
                            
                            # Update dict map_slug_to_genres
                            map_slug_to_genres = {m.slug: m._temp_genres for m in movies_to_create}
                            
                            # 3. Create relations using db cursor to avoid any missing 'id' errors on db-first tables
                            from django.db import connection
                            with connection.cursor() as cursor:
                                insert_query = "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
                                rels_data = []
                                for m in saved_movies:
                                    g_objects = map_slug_to_genres.get(m.slug, [])
                                    for g in g_objects:
                                        rels_data.append((m.id, g.id))
                                
                                if rels_data:
                                    cursor.executemany(insert_query, rels_data)
                            
                        self.stdout.write(f'Processed {total_processed} rows...')
                        movies_to_create = []

                # Xử lý nốt phần dư
                if movies_to_create:
                    with transaction.atomic():
                        Movie.objects.bulk_create(movies_to_create, ignore_conflicts=True)
                        
                        slugs_in_batch = [m.slug for m in movies_to_create]
                        saved_movies = Movie.objects.filter(slug__in=slugs_in_batch)
                        map_slug_to_genres = {m.slug: m._temp_genres for m in movies_to_create}
                            
                        from django.db import connection
                        with connection.cursor() as cursor:
                            insert_query = "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
                            rels_data = []
                            for m in saved_movies:
                                g_objects = map_slug_to_genres.get(m.slug, [])
                                for g in g_objects:
                                    rels_data.append((m.id, g.id))
                            
                            if rels_data:
                                cursor.executemany(insert_query, rels_data)
                        
                    self.stdout.write(f'Processed {total_processed} rows (Final).')

            self.stdout.write(self.style.SUCCESS(
                f'Successfully completed! Extracted {len(all_genre_names)} genres and imported {total_processed} new movies.'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
