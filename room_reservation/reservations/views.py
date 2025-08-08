from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, ConferenceRoomForm, ReservationForm
from .models import ConferenceRoom, Reservation

@login_required
def room_list(request):
    rooms = ConferenceRoom.objects.all()
    return render(request, 'reservations/room_list.html', {'rooms': rooms})

@login_required
def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('my_reservations')
    else:
        form = ReservationForm()
    return render(request, 'reservations/make_reservation.html', {'form': form})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations}) 

@login_required
def add_room(request):
    if request.method == 'POST':
        form = ConferenceRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = ConferenceRoomForm()
    return render(request, 'reservations/add_room.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Registration successful! You are now logged in.')
                return redirect('room_list')  # Redirect to the room list after login
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
