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
    path('plans/',views.plans_view,name='plans'),
    path('select_plan/', views.select_plan_view, name='select_plan'),
    path('delete_plan/', views.delete_plan, name='delete_plan'),
    path('payment_gateway/<int:plan_id>/', views.payment_gateway_view, name='payment_gateway'),
    path('workouts/', views.workouts_view, name='workouts'),
    path('workouts/day/<int:day>/', views.workouts_by_day_view, name='workouts_by_day'),
    path('view_workout_img/<int:workout_id>/', views.view_workout_img, name='view_workout_img'),
    path('nutrition/', views.nutrition_view, name='nutrition'),
    path('personal_workout', views.personal_workout_view, name='personal_workout'),
    path('select_trainer/', views.select_trainer_view, name='select_trainer'),
    path('set_live_session/', views.set_live_session_view, name='set_live_session'),
    path('view-scheduled-class/', views.view_scheduled_class, name='view_scheduled_class'),
    path('personal_nutrition/', views.personal_nutrition_view, name='personal_nutrition'),
    path('select_dietitian/', views.select_dietitian_view, name='select_dietitian'),
    path('send-message/<int:fm_id>/', views.client_message_view, name='send_message'),
    path('eating_habits/', views.eating_habits_view, name='eating_habits'),
    path('track_foods/', views.track_foods_view, name='track_foods'),



    path('fm_home/', views.fm_home_view, name='fm_home'),
    path('fm_register/', views.fm_register_view, name='fm_register'),
    path('fm_forgot/', views.fm_forgot_view, name='fm_forgot'),
    path('fm_reset/<uidb64>/<token>/', views.fm_reset_password_view, name='fm_reset_password'),
    path('fm_login/', views.fm_login_view, name='fm_login'),
    path('fm_profile/', views.fm_profile_view, name='fm_profile'),
    path('fm_logout/', views.fm_logout_view, name='fm_logout'),
    path('fm_users/', views.fm_users, name='fm_users'),
    path('fm_payment/', views.fm_payment, name='fm_payment'),
    path('fm_workouts/', views.fm_workouts_view, name='fm_workouts'),
    path('see_all_workouts/', views.see_all_workouts, name='see_all_workouts'),
    path('add_workout/', views.add_workout, name='add_workout'),
    path('update_workout/<int:workout_id>/', views.update_workout, name='update_workout'),
    path('delete_workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('fm_nutritions/', views.fm_nutritions_view, name='fm_nutritions'),
    path('fm_nutritions2/', views.fm_nutritions2, name='fm_nutritions2'),
    path('see_all_food/', views.see_all_food, name='see_all_food'),
    path('add_food/', views.add_food, name='add_food'),
    path('update_food/<int:food_id>/', views.update_food, name='update_food'),
    path('delete_food/<int:food_id>/', views.delete_food, name='delete_food'),
    path('fm_plans/', views.fm_plans, name='fm_plans'),
    path('view_messages/', views.view_messages, name='view_messages'),
    path('view_messages/messages/<int:client_id>/', view_client_messages, name='view_client_messages'),
    path('messages/reply/<int:message_id>/', reply_message, name='reply_message'),
    path('view_messages/send_message/<int:client_id>/', send_message_to_client, name='send_message_to_client'),
    path('nutrition_advice/', views.nutrition_advice_view, name='nutrition_advice'),





    path('admin_home/', views.admin_home_view, name='admin_home'),
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_users/', views.admin_users_view, name='admin_users'),
    path('admin_fm/', views.admin_fm_view, name='admin_fm'),
    path('accept_fm/<int:user_id>/', views.accept_fm_view, name='accept_fm'),
    path('delete_fm/<int:user_id>/', views.delete_fm, name='delete_fm'),
    path('delete_client/<int:user_id>/', views.delete_client, name='delete_client'),
    path('view_certificate/<int:user_id>/', views.view_certificate, name='view_certificate'),
    path('admin_payment/', views.admin_payment, name='admin_payment'),
    path('admin_plans/', views.admin_plans, name='admin_plans'),
    path('see_all_plan/', views.see_all_plan, name='see_all_plan'),
    path('add_plan/', views.add_plan, name='add_plan'),
    path('update_plan/<int:plan_id>/', views.update_plan, name='update_plan'),
    path('admin_delete_plan/<int:plan_id>/', views.admin_delete_plan, name='admin_delete_plan'),
    path('view_sessions/', views.view_sessions_view, name='view_sessions'),






    path('accounts/', include('allauth.urls')),
    path('google_login/', views.google_login_view, name='google_login'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('logout/',views.logout_view,name='logout'),
    path('reset/<uidb64>/<token>/',views.reset_password_view, name='reset_password'),

 ]
if settings.DEBUG:  

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

