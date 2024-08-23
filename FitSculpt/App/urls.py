from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),          
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'), 
    path('user_home/', views.user_home_view, name='user_home'),
    path('forgot/', views.forgot_view, name='forgot'),
    path('fm_home/', views.fm_home_view, name='fm_home'),
    path('fm_login/', views.fm_login_view, name='fm_login'),
    path('admin_home/', views.admin_home_view, name='admin_home'),
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('accounts/', include('allauth.urls')),
    path('google_login/', views.google_login_view, name='google_login'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('logout/',views.logout_view,name='logout'),
 ]
