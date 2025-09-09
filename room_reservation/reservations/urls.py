from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'reservations'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('reserve/', views.make_reservation, name='make_reservation'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('reservation/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('reservation/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('register/', views.register, name='register'),
    path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('admin-reserve/', views.admin_make_reservation, name='admin_make_reservation'),
    path('reservations/', views.view_all_reservations, name='admin_reservations'),
    path('admin-reservation/cancel/<int:reservation_id>/', views.admin_cancel_reservation, name='admin_cancel_reservation'),
    path('users/', views.user_list, name='user_list'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('user/add/', views.add_user, name='add_user')

]
