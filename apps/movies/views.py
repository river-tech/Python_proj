from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Movie, Review, Genre, UserInteraction
from .services import analyze_sentiment, get_recommendations, get_user_feed, semantic_search
from .forms import MovieForm
from django.utils.text import slugify

def home(request):
    """
    Home page. Shows personalized feed for logged-in users with interaction history,
    falls back to newest movies otherwise. Search/genre filters take precedence.
    """
    query = request.GET.get('q')
    vibe = request.GET.get('vibe')
    genre_slug = request.GET.get('genre')

    is_personalized = False

    # 1. TỐI ƯU CƠ BẢN: Chuẩn bị QuerySet gốc có sẵn prefetch_related
    # Việc này chặn đứng hàng trăm câu SQL khi render {{ movie.genres.all }} ở HTML
    base_qs = Movie.objects.prefetch_related('genres')

    if vibe:
        movies = semantic_search(vibe, top_k=24)
        query = vibe
    elif query:
        movies = semantic_search(query, top_k=24)
    elif genre_slug:
        movies = base_qs.filter(genres__slug=genre_slug).order_by('-rating')[:24] # Tối ưu: Thêm Limit 24
    elif request.user.is_authenticated:
        feed = get_user_feed(request.user.id, top_n=24)
        if feed:
            # Lưu ý: Nếu feed trả về List object thường, bạn cần kiểm tra hàm get_user_feed
            # Nếu nó trả về QuerySet, hãy chắc chắn trong đó có gọi .prefetch_related('genres')
            movies = feed
            is_personalized = True
        else:
            # 2. TỐI ƯU N+1 & TRÀN RAM: Thêm prefetch_related và GIỚI HẠN số lượng [:24]
            movies = base_qs.order_by('-created_at')[:24] 
    else:
        # Tương tự như trên
        movies = base_qs.order_by('-created_at')[:24]

    if genre_slug and (vibe or query):
        # Lưu ý: Đoạn này có thể lỗi nếu movies là kết quả từ semantic_search (List) chứ không phải QuerySet
        # Hãy chắc chắn semantic_search trả về QuerySet hoặc bạn xử lý filter bằng Python list.
        if isinstance(movies, list):
            movies = [m for m in movies if any(g.slug == genre_slug for g in m.genres.all())]
        else:
            movies = movies.filter(genres__slug=genre_slug)

    # 3. TỐI ƯU TRUY VẤN AI_PICK:
    # Dùng order_by('?') trên bảng lớn rất chậm. 
    # Nhưng vì là bản demo, tạm chấp nhận nếu bảng nhỏ. Nếu bảng lớn, nên bốc ngẫu nhiên id ở tầng Python.
    ai_pick = base_qs.filter(rating__gte=8.0).order_by('?').first()
    
    genres = Genre.objects.all()

    context = {
        'movies': movies,
        'genres': genres,
        'current_genre': genre_slug,
        'ai_pick': ai_pick,
        'current_vibe': vibe,
        'is_personalized': is_personalized,
    }
    return render(request, 'movies/home.html', context)

def movie_detail(request, slug):
    """
    Display movie details, reviews, and AI recommendations.
    """
    movie = get_object_or_404(Movie, slug=slug)
    reviews = movie.reviews.all().order_by('-created_at')

    user_id = request.user.id if request.user.is_authenticated else None

    # Record a lightweight "viewed" interaction so the feed can personalize from clicks,
    # not just ratings. Uses get_or_create so existing rating/comment rows aren't disturbed.
    if request.user.is_authenticated:
        UserInteraction.objects.get_or_create(
            user=request.user,
            movie=movie,
            defaults={'watched': True, 'watch_time_pct': 0.1},
        )

    recommendations = get_recommendations(movie_id=movie.id, user_id=user_id, top_n=4)

    context = {
        'movie': movie,
        'reviews': reviews,
        'recommendations': recommendations
    }
    return render(request, 'movies/movie_detail.html', context)

def add_review(request, slug):
    """
    Handle review submission with AI sentiment analysis.
    """
    if request.method == 'POST':
        movie = get_object_or_404(Movie, slug=slug)
        user_name = request.POST.get('user_name')
        if not user_name and request.user.is_authenticated:
            user_name = request.user.username

        comment = (request.POST.get('comment') or '').strip()
        rating_raw = request.POST.get('rating')

        try:
            rating_val = int(rating_raw) if rating_raw else None
        except (TypeError, ValueError):
            rating_val = None

        if not comment and rating_val is None:
            messages.error(request, 'Please provide a comment or a rating.')
            return redirect('movie_detail', slug=slug)

        sentiment = analyze_sentiment(comment) if comment else None

        Review.objects.create(
            movie=movie,
            user_name=user_name,
            comment=comment or None,
            rating=rating_val,
            sentiment_label=sentiment["label"] if sentiment else None,
        )

        if request.user.is_authenticated:
            UserInteraction.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={
                    'rating': float(rating_val) if rating_val is not None else None,
                    'comment': comment or None,
                    'sentiment_score': sentiment["score"] if sentiment else None,
                },
            )

        messages.success(request, 'Review added!')
        return redirect('movie_detail', slug=slug)

    return redirect('home')

def upload_movie(request):
    """
    Handle new movie uploads and generate AI metadata.
    """
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = form.save(commit=False)
            # Automatic Slug
            movie.slug = slugify(movie.title)
            
            # Simple AI Metadata Generation
            if movie.description:
                vibe_keywords = ['action', 'drama', 'sci-fi', 'romance', 'thriller', 'horror', 'funny', 'sad', 'intense']
                tags = [w for w in vibe_keywords if w in movie.description.lower()]
                movie.ai_metadata = f"Generated tags: {', '.join(tags)}. High-quality submission."
            
            movie.save()
            form.save_m2m() # Save genres
            messages.success(request, f'Movie "{movie.title}" uploaded successfully! AI analyzed the content.')
            return redirect('movie_detail', slug=movie.slug)
    else:
        form = MovieForm()
    
    return render(request, 'movies/upload_movie.html', {'form': form})
