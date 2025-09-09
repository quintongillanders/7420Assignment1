from django.utils import timezone
from .models import Reservation
from datetime import datetime, timedelta
from celery import shared_task
from django.core.mail import send_mail
import logging
logger = logging.getLogger(__name__)


@shared_task
def send_reminder_emails():
   logger.info("Running send_reminder_emails task")
   now = timezone.now()
   one_hour_from_now = now + timedelta(hours=1)

   # Fetch all reservations that haven't had reminders sent
   reservations = Reservation.objects.filter(reminder_sent=False)

   for reservation in reservations:
       # combine the date and time to get the exact datetime of the reservation
       reservation_start = datetime.combine(reservation.date, reservation.start_time)

       # check if the reservation is within the next hour
       if now <= reservation_start <= one_hour_from_now:
           user_email = reservation.user.email
           if user_email:
               subject = f'Reminder: Your reservation for {reservation.room.name}'
               message = f"""Reminder: Your reservation for {reservation.room.name} starts in one hour.
               
               Room: {reservation.room.name}
               Date: {reservation.date.strftime('%d-%m-%Y')}
               Time: {reservation.start_time.strftime('%I:%M %p').lstrip('0')} - {reservation.end_time.strftime('%I:%M %p').lstrip('0')}
               
               Thank you!
               """
               try:
                   send_mail(
                       subject,
                       message,
                       'quingillanders@gmail.com',
                       [user_email],
                       fail_silently=False,
                   )
                   # Mark the reminder as set
                   reservation.reminder_sent = True
                   reservation.save()
               except Exception as e:
                   logger.error(f"Failed to send reminder email: {str(e)}")
