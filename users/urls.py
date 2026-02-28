from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    # login returns access + refresh tokens
    # refresh swaps an old refresh token for a new access token
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('follow/<str:username>/', views.FollowUserView.as_view(), name='follow'),
    path('therapists/', views.TherapistListView.as_view(), name='therapists'),
    path('<str:username>/followers/', views.UserFollowersView.as_view(), name='followers'),
    path('<str:username>/following/', views.UserFollowingView.as_view(), name='following'),
]