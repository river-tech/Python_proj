from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        db_table = 'genres'

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    poster_url = models.CharField(max_length=500, null=True, blank=True)
    trailer_url = models.CharField(max_length=500, null=True, blank=True)
    
    # AI Metadata for filtering/recommendation
    ai_metadata = models.TextField(null=True, blank=True, help_text="AI generated tags and features")
    
    genres = models.ManyToManyField(Genre, related_name='movies', db_table='movie_genres')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movies'

    def __str__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)
    comment = models.TextField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    # AI Sentiment Analysis Result
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=10),
                name='rating_range'
            )
        ]

    def __str__(self):
        return f"{self.user_name} on {self.movie.title}"
