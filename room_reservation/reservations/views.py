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
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

@staff_member_required
def view_all_reservations(request):
    reservations = Reservation.objects.all().order_by('-date', 'start_time')
    return render(request, 'reservations/admin_reservations.html', {
        'reservations': reservations
    })

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
                messages.error(request,
                               'The time slot for this room has been taken, please select a different time or room.')
            else:
                reservation.save()

                user_email = reservation.user.email
                if user_email:
                    subject = f'Room Reservation Confirmation - {reservation.room.name}'
                    message = f"""
                Hello {request.user.username},

                Your reservation has been confirmed:

                Room: {reservation.room.name}
                Date: {reservation.date.strftime('%d-%m-%Y')}
                Time: {reservation.start_time.strftime('%I:%M %p').lstrip('0')} - {reservation.end_time.strftime('%I:%M %p').lstrip('0')}

                Thank you!
                Te Whare Runaga Conference Room Booking System
                """

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_email],
                        fail_silently=False,
                    )
                    messages.success(request,
                                     'Reservation created successfully! A confirmation email has been sent to you.')
                except Exception as e:
                    # log error but do not fail reservation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"failed to send confirmation email: {str(e)}")
                    messages.success(request, 'Reservation created successfully! (Email notification failed to send)')

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
      messages.success(request, "Room added successfully!")
      return redirect('reservations:room_list')
    else:
      messages.error(request, "Failed to add room. Please check the form data.")
  else:
    form = ConferenceRoomForm()

  context = {
    'form': form,
    'rooms_count': ConferenceRoom.objects.count(),
  }

  return render(request, 'reservations/add_room.html', context)


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
                return redirect('reservations:room_list')
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

                # Send the user an email after updating reservation
                user_email = updated_reservation.user.email
                if user_email:
                    subject = f'Room Reservation Updated - {updated_reservation.room.name}'
                    message = f"""
                Hello {updated_reservation.user.username},
                
                Your reservation for {updated_reservation.room.name} has been updated.
                
                Room: {updated_reservation.room.name}
                Date: {updated_reservation.date.strftime('%Y-%m-%d')}
                Time: {updated_reservation.start_time.strftime('%I:%M %p')}-{updated_reservation.end_time.strftime('%I:%M %p')}
                
                Thank you!
                Te Whare Runaga Conference Room Booking System
                """
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user_email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Failed to send reservation update email: {str(e)}')

                messages.success(request, 'Reservation updated successfully!')
                return redirect('reservations:my_reservations')
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
        user_email = reservation.user.email
        room_name = reservation.room.name
        reservation_date = reservation.date
        start_time = reservation.start_time
        end_time = reservation.end_time
        reservation.delete()
        messages.success(request, 'Reservation canceled successfully!')

        # Once the user has canceled their reservation:
        if user_email:
            subject = f'Room Reservation Canceled - {reservation.room.name}'
            message = f"""
        Hello {request.user.username},
        
        Your reservation for room {room_name} has been canceled.
        
        Room: {room_name}
        Date: {reservation_date.strftime('%d-%m-%Y')}
        Time: {start_time.strftime('%I:%M %p').lstrip('0')} - {end_time.strftime('%I:%M %p').lstrip('0')}
        
        Thank you!
        Te Whare Runaga Conference Room Booking System
        """
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"failed to send cancellation email: {str(e)}")

    return redirect('reservations:my_reservations')


# Edit a room, meant for staff only
@staff_member_required
def edit_room(request, room_id):
    room = get_object_or_404(ConferenceRoom, id=room_id)
    old_room_name = room.name

    if request.method == 'POST':
        form = ConferenceRoomForm(request.POST, instance=room)
        if form.is_valid():
            updated_room = form.save()
            updated_room.save()

            # if the room name has changed recently, send an email notification to users with reservations:
            if old_room_name != updated_room.name:
                reservations = Reservation.objects.filter(room=room)
                for res in reservations:
                    user_email = res.user.email
                    if user_email:
                        subject = f'Room Name Changed - {updated_room.name}'
                        message = f"""
                    Hello {res.user.username},
                    
                    Please note that the room you have a reservation for has been updated:
                    
                    Old Room Name: {old_room_name}
                    New Room Name: {updated_room.name}
                    Date: {res.date.strftime('%d-%m-%Y')}
                    Time: {res.start_time.strftime('%I:%M %p')}-{res.end_time.strftime('%I:%M %p')}
                    
                    Thank you!
                    Te Whare Runaga Conference Room Booking System staff
                    """
                        try:
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user_email],
                                fail_silently=False,
                            )
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f'Failed to send room name change email: {str(e)}')
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
        # get all reservations in current room before deletion
        room.delete()
        messages.success(request, 'Room deleted successfully!')
        return redirect('reservations:room_list')

    messages.info(request, f'Room "{room.name}" deletion cancelled')
    return redirect('reservations:room_list')

@staff_member_required
def admin_make_reservation(request):
    if request.method == 'POST':
        form = AdminReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()


            # send user a confirmation email on behalf of an admin.
            user_email = reservation.user.email
            if user_email:
                subject = f'Room Reservation confirmation on behalf of our staff - {reservation.room.name}'
                message = f"""
                Hello {reservation.user.username},

                Our staff have created a reservation for you on your behalf:
                
                Room: {reservation.room.name}
                Date: {reservation.date.strftime('%d-%m-%Y')}
                Time: {reservation.start_time.strftime('%I:%M %p').lstrip('0')} - {reservation.end_time.strftime('%I:%M %p').lstrip('0')}
                
                Thank you!
                Te Whare Runaga Conference Room Booking System staff
                """

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_email],
                        fail_silently=False,
                    )
                    messages.success(request, 'Reservation created successfully! A confirmation email has been sent to the user')
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"failed to send confirmation email (admin reservation): {str(e)}")
                    messages.success(request, 'Reservation created successfully! (Email notification failed to send)')
            else:
                messages.success(request, 'Reservation created successfully, but this user does not have an email on their account')

            return redirect('reservations:room_list')
    else:
        form = AdminReservationForm()

    return render(request, 'reservations/admin_make_reservation.html', {'form': form})


# Oversee all reservations and cancel reservations, meant for staff only
@staff_member_required
def view_all_reservations(request):
    reservations = Reservation.objects.all().order_by('-date', 'start_time')
    return render(request, 'reservations/admin_reservations.html', {'reservations': reservations})

@staff_member_required
def admin_cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        user_email = reservation.user.email
        room_name = reservation.room.name
        reservation_date = reservation.date
        start_time = reservation.start_time
        end_time = reservation.end_time
        username = reservation.user.username

        reservation.delete()
        messages.success(request, 'Reservation canceled successfully! A confirmation email has been sent to the user.')

        # Send the user an email notifying them of the staff cancellation
        if user_email:
            subject = f'Room Reservation Canceled - {room_name}'
            message = f"""
        Hello {username},
        As per your request, our staff have canceled your reservation for {room_name}:
        
        Room: {room_name}
        Date: {reservation_date.strftime('%d-%m-%Y')}
        Time: {start_time.strftime('%I:%M %p').lstrip('0')} - {end_time.strftime('%I:%M %p').lstrip('0')}
        
        Thank you!
        Te Whare Runaga Conference Room Booking System staff
        """
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"failed to send cancellation email (admin reservation): {str(e)}")

    return redirect('reservations:admin_reservations')

@staff_member_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'reservations/user_list.html', {'users': users})

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = 'is_staff' in request.POST
        user.is_active = 'is_active' in request.POST
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('reservations:user_list')
    return render(request, 'reservations/edit_user.html', {'user': user})


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "What are you doing? You can't delete yourself!")
        return redirect('reservations:user_list')

    if request.method == "POST":
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('reservations:user_list')
    return render(request, 'reservations/confirm_delete_user.html', {'user': user})

@staff_member_required
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('reservations:user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'reservations/add_user.html', {'form': form})

