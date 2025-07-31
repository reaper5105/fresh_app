# portal/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import State, Contribution, Comment, UserProfile 
from .forms import (
    ContributionForm, 
    CustomUserCreationForm, 
    ProfileEditForm, 
    CustomAuthenticationForm
)

# --- Authentication Views ---

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Core User-facing Views ---

@login_required
def home(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    followed_users = profile.follows.all()
    followed_categories = profile.followed_categories.split(',')
    query = Q(author__userprofile__in=followed_users) | Q(category__in=followed_categories)
    feed_items = Contribution.objects.filter(query).distinct().order_by('-submitted_at')
    context = {
        'contributions': feed_items,
        'is_personal_feed': True 
    }
    return render(request, 'home.html', context)

@login_required
def explore(request):
    all_contributions = Contribution.objects.all().order_by('-submitted_at')
    context = {
        'contributions': all_contributions
    }
    return render(request, 'home.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST, request.FILES)
        if form.is_valid():
            new_contribution = form.save(commit=False)
            new_contribution.author = request.user
            new_contribution.save()
            return redirect('profile') 
    else:
        form = ContributionForm()
    context = { 'form': form }
    return render(request, 'create_post.html', context)

@login_required
def profile(request):
    UserProfile.objects.get_or_create(user=request.user)
    user_contributions = Contribution.objects.filter(author=request.user).order_by('-submitted_at')
    context = {
        'user_contributions': user_contributions
    }
    return render(request, 'profile.html', context)

def public_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    user_contributions = Contribution.objects.filter(author=user_obj).order_by('-submitted_at')
    context = {
        'profile_user': user_obj,
        'user_contributions': user_contributions
    }
    return render(request, 'public_profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        initial_data = {'followed_categories': profile.followed_categories.split(',')}
        form = ProfileEditForm(instance=profile, initial=initial_data)
    return render(request, 'edit_profile.html', {'form': form})

# --- Social Feature Views ---

@login_required
def like_contribution(request, contribution_id):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    if request.method == 'POST':
        if contribution.likes.filter(id=request.user.id).exists():
            contribution.likes.remove(request.user)
            liked = False
        else:
            contribution.likes.add(request.user)
            liked = True
            if request.user != contribution.author:
                Notification.objects.create(recipient=contribution.author, sender=request.user, verb='liked your post', target=contribution)
        return JsonResponse({'liked': liked, 'likes_count': contribution.total_likes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, contribution_id):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(contribution=contribution, author=request.user, text=comment_text)
            if request.user != contribution.author:
                Notification.objects.create(recipient=contribution.author, sender=request.user, verb='commented on your post', target=contribution)
    return redirect('home')

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if user_to_follow.userprofile in profile.follows.all():
        profile.follows.remove(user_to_follow.userprofile)
    else:
        profile.follows.add(user_to_follow.userprofile)
        Notification.objects.create(recipient=user_to_follow, sender=request.user, verb='started following you')
    return redirect('home')

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    context = {
        'notifications': user_notifications
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.target:
        return redirect('home')
    return redirect('notifications')

# --- Admin-facing View ---

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_users_count = 0
    for session in active_sessions:
        if session.get_decoded().get('_auth_user_id'):
            active_users_count += 1
    
    total_contributions = Contribution.objects.count()
    states = State.objects.prefetch_related('contribution_set').all()
    contributions_by_state = {
        state: state.contribution_set.all().order_by('-submitted_at') for state in states
    }

    context = {
        'total_users': total_users,
        'active_users': active_users_count,
        'total_contributions': total_contributions,
        'contributions_by_state': contributions_by_state,
        'title': 'Dashboard'
    }
    return render(request, 'admin/custom_index.html', context)
