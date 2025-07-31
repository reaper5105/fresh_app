# portal/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import State, Contribution, Comment, UserProfile
from .forms import ContributionForm, CustomUserCreationForm 

# --- User-facing Views ---

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    UserProfile.objects.get_or_create(user=request.user)
    user_contributions = Contribution.objects.filter(author=request.user).order_by('-submitted_at')
    context = {
        'user_contributions': user_contributions
    }
    return render(request, 'profile.html', context)

# --- NEW: View specifically for creating posts ---
@login_required
def create_post(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST, request.FILES)
        if form.is_valid():
            new_contribution = form.save(commit=False)
            new_contribution.author = request.user
            new_contribution.save()
            return redirect('profile') # Redirect to profile after posting
    else:
        form = ContributionForm()
    
    context = {
        'form': form,
    }
    return render(request, 'create_post.html', context)

# --- UPDATED: Home view now ONLY shows the feed ---
@login_required
def home(request):
    UserProfile.objects.get_or_create(user=request.user)
    contributions = Contribution.objects.all().order_by('-submitted_at')
    context = {
        'contributions': contributions,
    }
    return render(request, 'home.html', context)

# --- Social feature and admin views remain the same ---
@login_required
def like_contribution(request, contribution_id):
    if request.method == 'POST':
        contribution = get_object_or_404(Contribution, id=contribution_id)
        if contribution.likes.filter(id=request.user.id).exists():
            contribution.likes.remove(request.user)
            liked = False
        else:
            contribution.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'likes_count': contribution.total_likes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, contribution_id):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(contribution=contribution, author=request.user, text=comment_text)
    return redirect('home')

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if user_to_follow in profile.follows.all():
        profile.follows.remove(user_to_follow)
    else:
        profile.follows.add(user_to_follow)
    return redirect('home')

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
