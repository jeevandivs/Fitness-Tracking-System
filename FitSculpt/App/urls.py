from django.urls import include, path
from . import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.index_view, name='index'),          
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'), 
    path('user_home/', views.user_home_view, name='user_home'),
    path('forgot/', views.forgot_view, name='forgot'),

    path('fm_home/', views.fm_home_view, name='fm_home'),
    path('fm_register/', views.fm_register_view, name='fm_register'),
    path('fm_forgot/', views.fm_forgot_view, name='fm_forgot'),
    path('fm_reset/<uidb64>/<token>/', views.fm_reset_password_view, name='fm_reset_password'),
    path('fm_login/', views.fm_login_view, name='fm_login'),
    path('fm_profile/', views.fm_profile_view, name='fm_profile'),
    path('fm_logout/', views.fm_logout_view, name='fm_logout'),


    path('admin_home/', views.admin_home_view, name='admin_home'),
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('admin_users/', views.admin_users_view, name='admin_users'),
    path('admin_fm/', views.admin_fm_view, name='admin_fm'),
    path('accept_fm/<int:user_id>/', views.accept_fm_view, name='accept_fm'),
    path('view_certificate/<int:user_id>/', views.view_certificate, name='view_certificate'),



    path('accounts/', include('allauth.urls')),
    path('google_login/', views.google_login_view, name='google_login'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('logout/',views.logout_view,name='logout'),
    path('reset/<uidb64>/<token>/',views.reset_password_view, name='reset_password'),

 ]
if settings.DEBUG:  

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

