# portal/forms.py
import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contribution

def validate_telugu(value):
    telugu_pattern = re.compile(r'^[\u0C00-\u0C7F\s\d.,!?-]+$')
    if not telugu_pattern.match(value):
        raise ValidationError(
            'దయచేసి తెలుగులో మాత్రమే వ్రాయండి. (Please write in Telugu only.)',
            code='invalid_language'
        )

class ContributionForm(forms.ModelForm):
    text_content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        validators=[validate_telugu],
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
