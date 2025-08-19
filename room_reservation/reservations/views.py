from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time
from .forms import CustomUserCreationForm, ConferenceRoomForm, ReservationForm
from .models import ConferenceRoom, Reservation
from .forms import AdminReservationForm


# Login page
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')

        # if username or password fields are empty
        if not username or not password:
            messages.error(request, 'Please enter both username and password and try again.')
            return render(request, 'registration/login.html')

        # Attempt to log the user in
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user) # Login the user and take them to the main page after login
            return redirect('room_list') # sends the user back to the login page
        else:
            messages.error(request, 'Incorrect username or password. Please try again.')

            return render(request, 'registration/login.html')


# Room list page
@login_required
def room_list(request):
    # Get the date from the request, or use today's date
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # get the current time for availability
    current_time = timezone.now().time()
    
    # get all rooms
    rooms = ConferenceRoom.objects.all()
    
    # find all reservations for that specific date
    reservations = Reservation.objects.filter(date=selected_date)

# Attach availability status to each room
    for room in rooms:
        room_reservations = reservations.filter(room=room).order_by('start_time')
        room.is_available = not room_reservations.exists()
        
        # store the time slots of rooms
        room.booking_times = []
        for res in room_reservations:
            room.booking_times.append({
                'start': res.start_time.strftime('%I:%M %p').lstrip('0'),
                'end': res.end_time.strftime('%I:%M %p').lstrip('0')
            })
    
    context = {
        'rooms': rooms,
        'selected_date': selected_date,
        'date_str': selected_date.strftime('%d-%m-%Y'),  # Date format as DD-MM-YYYY
        'user': request.user  # Make sure user is available in the template
    }
    return render(request, 'reservations/room_list.html', context)



# Make a reservation
@login_required
def make_reservation(request):
    # Get room_id and date if exists
    room_id = request.GET.get('room')
    date_str = request.GET.get('date')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            
            # Check for overlapping reservations
            overlapping = Reservation.objects.filter(
                room=reservation.room,
                date=reservation.date,
                start_time__lt=reservation.end_time,
                end_time__gt=reservation.start_time
            ).exists()
            
            if overlapping:
                messages.error(request, 'The time slot for this room has been taken, please select a different time or room.')
            else:
                reservation.save()
                messages.success(request, 'Reservation created successfully!')
                return redirect('reservations:my_reservations')
    else:

        initial_data = {}
        if room_id:
            try:
                initial_data['room'] = ConferenceRoom.objects.get(id=room_id)
            except ConferenceRoom.DoesNotExist:
                pass
                
        if date_str:
            try:
                initial_data['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
                
        form = ReservationForm(initial=initial_data)
    
    return render(request, 'reservations/make_reservation.html', {'form': form})


# View the user's reservations
@login_required
def my_reservations(request):
    now = timezone.now()  # get the current date and time
    
    # Filter reservations for the current user that are in the future only
    reservations = Reservation.objects.filter(
        user=request.user,
        date__gte=now.date()  # Only get reservations from today or later
    ).filter(
        # This ensures we don't get past reservations from today
        Q(date__gt=now.date()) |
        Q(date=now.date(), end_time__gt=now.time())
    ).order_by('date', 'start_time')

    return render(request, 'reservations/my_reservations.html', {
        'reservations': reservations
    })


# Add a new conference room (Staff only access)
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


# Register a new user
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
                return redirect('room_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Edit an existing reservation
@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save(commit=False)
            
            # Exclude current reservation from overlapping checks
            overlapping = Reservation.objects.filter(
                room=updated_reservation.room,
                date=updated_reservation.date,
                start_time__lt=updated_reservation.end_time,
                end_time__gt=updated_reservation.start_time
            ).exclude(id=reservation_id).exists()
            
            if overlapping:
                messages.error(request, 'This room is already booked for the selected time slot. Please choose a different time or room.')
            else:
                updated_reservation.save()
                messages.success(request, 'Reservation updated successfully!')
                return redirect('my_reservations')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'reservations/edit_reservation.html', {
        'form': form,
        'reservation': reservation
    })

# Cancel a reservation
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Reservation canceled successfully!')
    return redirect('reservations:my_reservations')


# Edit a room, meant for staff only but for now it is open to all
@staff_member_required
def edit_room(request, room_id):
    room = get_object_or_404(ConferenceRoom, id=room_id)

    if request.method == 'POST':
        form = ConferenceRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('reservations:room_list')

    else:
        form = ConferenceRoomForm(instance=room)
    return render(request, 'reservations/edit_room.html', {
        'form': form,
        'room': room
    })

# Delete a room, meant for staff only
@staff_member_required
def delete_room(request, room_id):
    room = get_object_or_404(ConferenceRoom, id=room_id)

    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted successfully!')
        return redirect('room_list')

    messages.info(request, f'Room "{room.name}" deletion cancelled')
    return redirect('reservations:room_list')

@staff_member_required
def admin_make_reservation(request):
    if request.method == 'POST':
        form = AdminReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation created successfully!')
            return redirect('reservations:room_list')  # Using the namespaced URL name
    else:
        form = AdminReservationForm()

    return render(request, 'reservations/admin_make_reservation.html', {'form': form})
