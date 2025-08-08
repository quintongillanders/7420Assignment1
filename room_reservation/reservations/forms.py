from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ConferenceRoom, Reservation

User = get_user_model()

class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial time to the next half hour
        now = timezone.now()
        next_half_hour = (now + timezone.timedelta(minutes=30 - now.minute % 30)).replace(second=0, microsecond=0)
        self.fields['start_time'].initial = next_half_hour.time()
        self.fields['end_time'].initial = (next_half_hour + timezone.timedelta(hours=1)).time()
        
        # shows 30 minute intervals
        self.fields['start_time'].widget.attrs['step'] = '1800'
        self.fields['end_time'].widget.attrs['step'] = '1800'
        
    class Meta:
        model = Reservation
        fields = ['room', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
        }

class ConferenceRoomForm(forms.ModelForm):
    class Meta:
        model = ConferenceRoom
        fields = ['name', 'location', 'capacity']
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise forms.ValidationError('Room name must be at least 3 characters long.')
        return name.strip()
        
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity < 1:
            raise forms.ValidationError('Capacity must be at least 1.')
        return capacity

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom help text
        self.fields['username'].help_text = 'Your username can only be a max of 150 characters. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters. You cannot have a password that is only numbers. eg: 12345678.'
        )
        self.fields['password2'].help_text = 'Please enter the same password again to verify'
        
        # Add form-control class to all fields
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'The username or password you entered is incorrect. Please try again.',
        'inactive': 'This account is inactive.',
    }
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'autocomplete': 'off',
            'value': '',
            'class': 'form-control',
            'placeholder': 'Enter your username',
        }),
        label='Username',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'value': '',
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
        label='Password',
        strip=False,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for fieldname in ['username', 'password']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})