from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('search/', views.SearchPostsView.as_view(), name='search'),
]