from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from .forms import CustomLoginForm
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('reserve/', views.make_reservation, name='make_reservation'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('reservation/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('reservation/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('login/', LoginView.as_view(template_name='registration/login.html', authentication_form=CustomLoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    ]
