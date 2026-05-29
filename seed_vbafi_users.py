import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.movies.models import Movie, UserInteraction

User = get_user_model()

# Lấy 5 movie bất kỳ
movies = list(Movie.objects.all()[:5])
if not movies:
    print('No movies found!')
    exit(1)

# Tạo 20 user mới, mỗi user có tối đa 10 hành động với 10 movie khác nhau
for i in range(1, 21):
    username = f'vbauser_{i:03d}'
    email = f'{username}@test.local'
    password = '123456'  # Đặt password đơn giản, có thể hash lại nếu cần
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password, role='STUDENT')
        print(f'Created user: {username}')
    else:
        user = User.objects.get(username=username)

    # Lấy tối đa 10 movie random, không trùng lặp
    movie_sample = random.sample(movies, min(10, len(movies)))
    for movie in movie_sample:
        # Chỉ tạo nếu chưa có interaction này
        if not UserInteraction.objects.filter(user_id=user.id, movie_id=movie.id).exists():
            rating = random.randint(5, 10)
            comment = random.choice([
                'Great movie!', 'Pretty good.', 'Not my type.', 'Loved the visuals.', 'Boring plot.',
                'Nice soundtrack.', 'Would recommend.', 'Average.', 'Amazing acting.', 'Not impressed.',
                'Good pacing.', 'Enjoyed it.', 'Could be better.', 'Fantastic!', 'So-so.',
                'Solid film.', 'Liked the ending.', 'Forgettable.', 'Great cast.', 'Meh.'
            ])
            sentiment_score = round(random.uniform(0.2, 1.0), 3)
            watched = True
            watch_time_pct = round(random.uniform(0.5, 1.0), 2)
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))

            UserInteraction.objects.create(
                user_id=user.id,
                movie_id=movie.id,
                rating=rating,
                comment=comment,
                sentiment_score=sentiment_score,
                watched=watched,
                watch_time_pct=watch_time_pct,
                created_at=created_at
            )
            print(f'User {username} interacted with movie {movie.id}')
        else:
            print(f'User {username} already has interaction with movie {movie.id}, skipping.')
