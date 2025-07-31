# portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('create/', views.create_post, name='create_post'), # The new URL for creating posts
    path('', views.home, name='home'), # This is now the main feed
    
    # Social URLs
    path('like/<int:contribution_id>/', views.like_contribution, name='like_contribution'),
    path('comment/<int:contribution_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
]
