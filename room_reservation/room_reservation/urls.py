from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from reservations import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='reservations:room_list'), name='logout'),
    path('admin/reservation/cancel/<int:reservation_id>/', views.admin_cancel_reservation, name='admin_cancel_reservation'),
    path('', include('reservations.urls')),
]