from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('reserve/', views.make_reservation, name='make_reservation'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('rooms/add/', views.add_room, name='add_room'),

    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]