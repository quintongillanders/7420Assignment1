from django.db import models
from django.contrib.auth.models import User

class ConferenceRoom(models.Model):
    # These will be the basic details about each meeting room
    name = models.CharField(max_length=100) # Room name
    location = models.CharField(max_length=100) # Where the room is located
    capacity = models.PositiveIntegerField() # How many people can fit in the room

    def __str__(self):
        # Show name, location and how many seats
        return f"{self.name} @ {self.location} - Seats: {self.capacity}"

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Shows who booked the room
    room = models.ForeignKey(ConferenceRoom, on_delete=models.CASCADE) # Which room the user booked
    date = models.DateField() # What time the reservation is for
    start_time = models.TimeField() # When the reservation starts
    end_time = models.TimeField() # When the reservation ends
    created_at = models.DateTimeField(auto_now_add=True) # When the reservation was made
    reminder_sent = models.BooleanField(default=False) # Track if reminder email was sent

    def __str__(self):
        return f"{self.room.name} - {self.date} {self.start_time}-{self.end_time}" #Show which room, date and time.
