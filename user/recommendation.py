import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from django.db.models import Count, Avg, Q
from django.core.cache import cache
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from collections import Counter
import json
import re
from .models import *
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

class BookRecommender:
    def __init__(self, user):
        self.user = user
        self.cache_key = f'recs_{user.email}'
        
    def get_recommendations(self, num_recs=10):
        """Main method to get hybrid recommendations"""
        cached = cache.get(self.cache_key)
        if cached:
            return cached[:num_recs]
            
        # Get all recommendation types
        content_recs = self.content_based_recs()
        collab_recs = self.collaborative_recs()
        popular_recs = self.popularity_recs()
        
        # Combine and rank
        hybrid_recs = self.combine_recs(
            content_recs, 
            collab_recs, 
            popular_recs
        )
        
        # Cache for 1 hour
        cache.set(self.cache_key, hybrid_recs, 3600)
        return hybrid_recs[:num_recs]
    
    def content_based_recs(self, num_recs=20):
        """Recommend books based on user interests and book content"""
        from .models import product, UserBookInteraction
        
        # Get user interests from profile and search history
        user_interests = self.get_user_interests()
        
        # Get all books not interacted with by user
        interacted_books = UserBookInteraction.objects.filter(
            user=self.user
        ).values_list('book_id', flat=True)
        
        books = product.objects.exclude(id__in=interacted_books)
        
        if not books.exists() or not user_interests:
            return []
            
        # Prepare book data for vectorization
        book_data = []
        for book in books:
            # Combine all textual data
            text_data = " ".join([
                book.name,
                book.language,
                book.publisher,
                book.pdes,
                book.category.cname if book.category else ""
            ])
            book_data.append({
                'id': book.id,
                'text': text_data,
                'book_obj': book
            })
        
        # Vectorize books and user interests
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        book_vectors = tfidf.fit_transform([b['text'] for b in book_data])
        user_vector = tfidf.transform([" ".join(user_interests)])
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, book_vectors).flatten()
        book_indices = np.argsort(similarities)[::-1][:num_recs]
        
        return [{
            'book': book_data[idx]['book_obj'],
            'score': float(similarities[idx]),
            'type': 'content'
        } for idx in book_indices]
    
    def collaborative_recs(self, num_recs=20):
        """User-user and item-item collaborative filtering"""
        from .models import UserBookInteraction, Review, product
        
        # User-User CF
        # Create user-book rating matrix (using reviews and interactions)
        reviews = Review.objects.values('user', 'book', 'rating')
        interactions = UserBookInteraction.objects.filter(
            interaction_type__in=['purchase', 'like']
        ).annotate(
            rating=Count('id')  # Simple weighting for interactions
        ).values('user', 'book', 'rating')
        
        if not reviews and not interactions:
            return []
            
        # Create DataFrame
        ratings_data = []
        for review in reviews:
            ratings_data.append({
                'user_id': review['user'],
                'book_id': review['book'],
                'rating': review['rating']
            })
            
        for interaction in interactions:
            ratings_data.append({
                'user_id': interaction['user'],
                'book_id': interaction['book'],
                'rating': interaction['rating']
            })
            
        df = pd.DataFrame(ratings_data)
        
        if df.empty:
            return []
            
        # Pivot to user-book matrix
        user_book_matrix = df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        
        if self.user.id not in user_book_matrix.index:
            return []
            
        # Find similar users
        model = NearestNeighbors(metric='cosine', algorithm='brute')
        model.fit(user_book_matrix)
        
        distances, indices = model.kneighbors(
            user_book_matrix.loc[self.user.id].values.reshape(1, -1),
            n_neighbors=5
        )
        
        # Get books liked by similar users
        similar_users = user_book_matrix.iloc[indices[0]].index
        similar_users_ratings = user_book_matrix.loc[similar_users]
        avg_ratings = similar_users_ratings.mean(axis=0)
        
        # Filter out books user has already interacted with
        user_interactions = UserBookInteraction.objects.filter(
            user=self.user
        ).values_list('book_id', flat=True)
        
        # Get top recommended books
        recommendations = []
        for book_id, score in avg_ratings.items():
            if book_id not in user_interactions and score > 0:
                book = product.objects.get(id=book_id)
                recommendations.append({
                    'book': book,
                    'score': float(score),
                    'type': 'collaborative'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:num_recs]
    
    def popularity_recs(self, num_recs=20):
        """Popular books weighted by sentiment and recent activity"""
        from .models import product, Review, UserBookInteraction
        
        # Get books with highest engagement (purchases, likes, reviews)
        books = product.objects.annotate(
            popularity_score=Count('interactions') + 
                            Count('reviews') * 0.5
        ).order_by('-popularity_score')[:100]  # Get top 100 for sentiment analysis
        
        if not books.exists():
            return []
            
        # Calculate sentiment scores for each book
        recommendations = []
        for book in books:
            # Get average sentiment of reviews
            reviews = Review.objects.filter(book=book)
            sentiment_score = 0
            if reviews.exists():
                sentiments = []
                for review in reviews:
                    sentiment = sia.polarity_scores(review.comment)
                    sentiments.append(sentiment['compound'])
                sentiment_score = np.mean(sentiments) if sentiments else 0
            
            # Calculate final score (popularity + sentiment boost)
            score = book.popularity_score * (1 + sentiment_score * 0.3)
            recommendations.append({
                'book': book,
                'score': float(score),
                'type': 'popularity'
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:num_recs]
    
    def combine_recs(self, *rec_types):
        """Combine all recommendation types with weighting"""
        from .models import UserBookInteraction
        
        combined = {}
        weights = {
            'content': 0.4,
            'collaborative': 0.4,
            'popularity': 0.2
        }
        
        # Get books user has already interacted with
        interacted_books = set(UserBookInteraction.objects.filter(
            user=self.user
        ).values_list('book_id', flat=True))
        
        # Combine all recommendations with weights
        for rec_type in rec_types:
            for rec in rec_type:
                book_id = rec['book'].id
                if book_id in interacted_books:
                    continue
                    
                if book_id not in combined:
                    combined[book_id] = {
                        'book': rec['book'],
                        'score': rec['score'] * weights.get(rec['type'], 0.3),
                        'types': [rec['type']]
                    }
                else:
                    combined[book_id]['score'] += rec['score'] * weights.get(rec['type'], 0.3)
                    combined[book_id]['types'].append(rec['type'])
        
        # Convert to list and sort
        sorted_recs = sorted(
            combined.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_recs
    
    def get_user_interests(self):
        """Extract user interests from profile and search history"""
        interests = []
        
        # Get from profile interests field
        if self.user.interests:
            interests.extend(self.user.interests.split(','))
            
        # Get from search history (last 10 searches)
        searches = SearchLog.objects.filter(
            user=self.user
        ).order_by('-timestamp').values_list('query', flat=True)[:10]
        
        # Extract keywords from searches
        for search in searches:
            # Simple keyword extraction (improve with NLP if needed)
            words = re.findall(r'\w+', search.lower())
            interests.extend(words)
            
        # Remove duplicates and empty strings
        interests = list(set([i.strip() for i in interests if i.strip()]))
        return interests