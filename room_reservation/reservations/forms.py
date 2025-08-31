from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ConferenceRoom, Reservation

# Get the active user model
User = get_user_model()

class AdminReservationForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    room = forms.ModelChoiceField(
        queryset=ConferenceRoom.objects.all().order_by('name'),
        label="Select Room",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
        })
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Reservation
        fields = ['user', 'room', 'date', 'start_time', 'end_time']

# This whole section is the reservation form
class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial time to the next half hour
        now = timezone.now()
        next_half_hour = (now + timezone.timedelta(minutes=30 - now.minute % 30)).replace(second=0, microsecond=0)
        # Default start time to the next half hour
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

        # Admin reservation form
class AdminReservationForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="User"
    )
    
    class Meta:
        model = Reservation
        fields = ['user', 'room', 'date', 'start_time', 'end_time']
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

# Conference room form
class ConferenceRoomForm(forms.ModelForm):
    class Meta:
        model = ConferenceRoom
        fields = ['name', 'location', 'capacity']
        
    def clean_name(self):
        # Validate that room name is at least 3 characters long
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise forms.ValidationError('Please enter a name with at least 3 characters.')
        return name.strip()
        
    def clean_capacity(self):
        # Ensure capacity is at least 1
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity < 1:
            raise forms.ValidationError('Please enter a capacity higher than 0.')
        return capacity


# Custom user creation form for creating accounts
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email","password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default help text
        for fieldname in self.fields:
            self.fields[fieldname].help_text = None
        
      # Add bootstrap form control styling
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

# Custom login form
class CustomLoginForm(AuthenticationForm):
    # Override default error messages for login failure attempts
    error_messages = {
        'invalid_login': 'The username or password you entered is incorrect. Please try again.',
        'inactive': 'This account is currently inactive.',
    }

    # Username input
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
    # Password input
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'value': '',
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
        label='Password',
        strip=False, # do not strip whitespace
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add form-control class to all fields
        for fieldname in ['username', 'password']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})