import pandas as pd
from user.models import profile, product, Review, SearchLog

def prepare_data():
    # Fetch user data
    users = profile.objects.all()
    user_data = pd.DataFrame(list(users.values('id', 'name', 'interests')))

    # Fetch product data
    products = product.objects.all()
    product_data = pd.DataFrame(list(products.values('id', 'name', 'pdes', 'category', 'tprice', 'disprice')))

    # Fetch reviews
    reviews = Review.objects.all()
    review_data = pd.DataFrame(list(reviews.values('user_id', 'product_id', 'rating', 'comment')))

    # Fetch search logs
    search_logs = SearchLog.objects.all()
    search_data = pd.DataFrame(list(search_logs.values('user_id', 'query')))

    return user_data, product_data, review_data, search_data