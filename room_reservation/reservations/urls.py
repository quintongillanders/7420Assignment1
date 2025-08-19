from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from .forms import CustomLoginForm
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'), # Main room list page
    path('reserve/', views.make_reservation, name='make_reservation'), # Page for making a reservation
    path('my_reservations/', views.my_reservations, name='my_reservations'), # Page for displaying the user's reservations
    path('reservation/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'), # Page for editing a reservation
    path('reservation/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'), # Page for canceling a reservation
    path('rooms/add/', views.add_room, name='add_room'), # Page for adding a new room
    path('login/', LoginView.as_view(template_name='registration/login.html', authentication_form=CustomLoginForm), name='login'), # Page for logging in
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), # Page for logging out
    path('register/', views.register, name='register'), # Page for registering a new user
    path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'), # Page for editing a room
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'), # Page for deleting a room
    ]
