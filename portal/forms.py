# portal/forms.py
import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Contribution, UserProfile

# The form for submitting cultural content
class ContributionForm(forms.ModelForm):
    # The custom validator has been removed from this field
    text_content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True,
        label='వివరణ (Description)'
    )

    class Meta:
        model = Contribution
        fields = ['state', 'category', 'text_content', 'image_content', 'audio_content', 'video_content']
        labels = {
            'state': 'రాష్ట్రం (State)',
            'category': 'వర్గం (Category)',
            'image_content': 'చిత్రం (Image)',
            'audio_content': 'ఆడియో (Audio)',
            'video_content': 'వీడియో (Video)',
        }

# --- (The rest of the file remains the same) ---

# Custom Registration Form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text='అవసరం. దయచేసి సరైన ఇమెయిల్ చిరునామాను ఇవ్వండి.'
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-style', 'placeholder': 'ఉదా: తెలుగు_గర్వం'})
        self.fields['email'].widget.attrs.update({'class': 'input-style', 'placeholder': 'మీరు@ఉదాహరణ.com'})
        self.fields['password1'].widget.attrs.update({'class': 'input-style', 'placeholder': 'ఒక బలమైన పాస్‌వర్డ్‌ను నమోదు చేయండి'})
        self.fields['password2'].widget.attrs.update({'class': 'input-style', 'placeholder': 'మీ పాస్‌వర్డ్‌ను నిర్ధారించండి'})

# Form for Editing User Profile
class ProfileEditForm(forms.ModelForm):
    CATEGORY_CHOICES = Contribution.CATEGORY_CHOICES
    
    followed_categories = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Your Favorite Categories"
    )

    class Meta:
        model = UserProfile
        fields = ['followed_categories']

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.followed_categories = ",".join(self.cleaned_data.get('followed_categories', []))
        if commit:
            profile.save()
        return profile

# Custom Login Form with "Remember Me"
class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-secondary focus:ring-secondary'}))
