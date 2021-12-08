from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup-view'),

    path('signup/<str:ref_code>/', views.main_view, name='main-view'),
    path('sent/', views.activation_sent_view, name='activation_sent'),
    path('activate/<slug:uidb64>/<slug:token>/',
         views.activate, name='activate'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]
