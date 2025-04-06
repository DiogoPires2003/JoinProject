
from django.contrib import admin
from django.urls import path
from healthApp.views import login_view, register, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('register/', register,name='register'),
    path('home/', home,name='home'),
]
