from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from bot.api import BotRegisterAPIView


urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('core.urls')),

    path('api/v1/bot/register/', BotRegisterAPIView.as_view(), name='bot-register'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
     
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/'},
         name='logout')


]

