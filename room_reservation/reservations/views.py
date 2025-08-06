from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ConferenceRoom, Reservation
from.forms import ReservationForm, ConferenceRoomForm

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

@staff_member_required
def add_room(request):
    if request.method == 'POST':
        form = ConferenceRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = ConferenceRoomForm()
    return render(request, 'reservations/add_room.html', {'form': form})
