from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import ConferenceRoom, Reservation

User = get_user_model()

class ReservationForm(forms.ModelForm):
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
        self.fields['username'].help_text = '150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters and can\'t be too common or entirely numeric.'
        )
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
        
        # Add form-control class to all fields
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'autocomplete': 'off',
            'value': '',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'value': '',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for fieldname in ['username', 'password']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})