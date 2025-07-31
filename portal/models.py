# portal/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ... (State, Contribution, Comment, UserProfile models remain the same) ...
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Contribution(models.Model):
    CATEGORY_CHOICES = [
        ('PLACES', 'Places'),
        ('DANCE', 'Dance'),
        ('FOOD', 'Food'),
        ('TRADITION', 'Tradition'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='images/', blank=True, null=True)
    audio_content = models.FileField(upload_to='audio/', blank=True, null=True)
    video_content = models.FileField(upload_to='videos/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_contributions', blank=True)

    def __str__(self):
        return f'{self.author.username} - {self.category} for {self.state.name}'

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.contribution}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)
    followed_categories = models.TextField(blank=True, help_text="Comma-separated list of categories")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


# --- NEW Notification Model ---
class Notification(models.Model):
    # The user who should receive the notification
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # The user who triggered the notification (can be null for system messages)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='+')
    # The type of notification
    verb = models.CharField(max_length=255)
    # A link to the relevant object (e.g., the post that was liked)
    target = models.ForeignKey(Contribution, on_delete=models.CASCADE, null=True, blank=True)
    # Read/unread status
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.recipient}: {self.verb}'

    class Meta:
        ordering = ['-timestamp']
