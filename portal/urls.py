# portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('create/', views.create_post, name='create_post'), # The new URL for creating posts
    path('', views.home, name='home'), # This is now the main feed
    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('explore/', views.explore, name='explore'),
    # portal/urls.py
# ...

    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),


    # Social URLs
    path('like/<int:contribution_id>/', views.like_contribution, name='like_contribution'),
    path('comment/<int:contribution_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
]
