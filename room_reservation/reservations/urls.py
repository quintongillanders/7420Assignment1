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
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html"
    ), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('users/', views.user_list, name='user_list'),

]
