
from django.contrib import admin
from django.urls import path
from healthApp.views import login_view, register, home
from healthApp.views import pedir_cita, nosotros, centros, servicios_salud, informacion_util, contacto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('register/', register,name='register'),
    path('home/', home,name='home'),
    path('pedir-cita/', pedir_cita, name='pedir_cita'),
    path('admin/', admin.site.urls),
    path('nosotros/', nosotros, name='nosotros'),
    path('centros/', centros, name='centros'),
    path('servicios-salud/', servicios_salud, name='servicios_salud'),
    path('informacion-util/', informacion_util, name='informacion_util'),
    path('contacto/', contacto, name='contacto'),
    path('area-privada/', login_view , name='area_privada'),
]
