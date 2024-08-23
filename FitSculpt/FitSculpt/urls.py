# FitSculpt/urls.py

from django.contrib import admin
from django.urls import include, path
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('App.urls')),
]
