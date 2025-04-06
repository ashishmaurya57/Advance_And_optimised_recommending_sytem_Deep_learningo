from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alt'),
    path('index/', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('contactus/', views.contactus, name='contactus'),
    path('services/', views.services, name='services'),
    path('myorders/', views.myorders, name='myorders'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('products/', views.prod, name='products'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('viewdetails/', views.viewdetails, name='viewdetails'),
    path('process/', views.process, name='process'),
    path('logout/', views.logout, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('search/', views.search_view, name='search_view'),
    path('product/<int:product_id>/like/', views.like_product, name='like_product'),
    path('product/<int:product_id>/dislike/', views.dislike_product, name='dislike_product'),
    # path('/', views.recommended_books, name='recommendations'),
    # path('api/recommendations/', views.get_recommendations, name='api_recommendations'),
]