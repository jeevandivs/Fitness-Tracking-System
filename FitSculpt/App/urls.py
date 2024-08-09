from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),          
    path('login/', views.login_view, name='login'), 
    path('login/client',views.client_view,name='client'),  
    path('signup/', views.signup_view, name='signup'), 
    path('about/', views.about_view, name='about'),   
    path('contact/', views.contact_view, name='contact')
]
