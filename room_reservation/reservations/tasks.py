from django.core.mail import send_mail
from django.utils import timezone
from .models import Reservation
from datetime import timedelta

def send_reminder_emails():
    # Get reservations starting in 1 hour from now
    one_hour_from_now = timezone.now() + timedelta(hours=1)
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=one_hour_from_now,
        reminder_sent=False
    )

    for reservation in upcoming_reservations:
        subject = f'Upcoming Room Reservation for {reservation.room.name}'
        message = f'''
        Reminder: Your room reservation starts in 1 hour.
        Room: {reservation.room.name}
        Date: {reservation.date}
        Time: {reservation.start_time} - {reservation.end_time}
        '''
        send_mail(
            subject,
            message,
            'noreply@yourdomain.com',
            [reservation.user.email],
            fail_silently=False,
        )
        reservation.reminder_sent = True
        reservation.save()
