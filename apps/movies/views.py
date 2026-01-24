from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Movie, Review, Genre
from .services import analyze_sentiment, get_recommendations

from django.db.models import Q

def home(request):
    """
    Home page displaying movies and genres.
    """
    movies = Movie.objects.all().order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        movies = movies.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(ai_metadata__icontains=query)
        )

    # Filter by genre if provided
    genre_slug = request.GET.get('genre')
    if genre_slug:
        movies = movies.filter(genres__slug=genre_slug)
        
    genres = Genre.objects.all()
    
    context = {
        'movies': movies,
        'genres': genres,
        'current_genre': genre_slug
    }
    return render(request, 'movies/home.html', context)

def movie_detail(request, slug):
    """
    Display movie details, reviews, and AI recommendations.
    """
    movie = get_object_or_404(Movie, slug=slug)
    reviews = movie.reviews.all().order_by('-created_at')
    
    # Get AI Recommendations
    recommendations = get_recommendations(movie.id, top_n=4)
    
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
        
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        
        if comment and rating:
            # AI Logic: Analyze sentiment
            sentiment = analyze_sentiment(comment)
            
            Review.objects.create(
                movie=movie,
                user_name=user_name,
                comment=comment,
                rating=rating,
                sentiment_label=sentiment
            )
            messages.success(request, f'Review added! AI Sentiment Analysis: {sentiment}')
        else:
            messages.error(request, 'Please provide both a comment and a rating.')
            
        return redirect('movie_detail', slug=slug)
    
    return redirect('home')
