import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def generate_user_embeddings(user_data, search_data):
    # Combine user interests and search queries
    user_data['combined'] = user_data['interests'] + ' ' + search_data.groupby('user_id')['query'].apply(' '.join)
    vectorizer = TfidfVectorizer(max_features=100)
    user_embeddings = vectorizer.fit_transform(user_data['combined']).toarray()
    return user_embeddings

def generate_product_embeddings(product_data):
    # Use product descriptions and sentiment for embeddings
    vectorizer = TfidfVectorizer(max_features=100)
    product_embeddings = vectorizer.fit_transform(product_data['pdes'] + ' ' + product_data['sentiment']).toarray()
    return product_embeddings