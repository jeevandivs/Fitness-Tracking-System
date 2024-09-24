from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import connection
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.cache import never_cache
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from FitSculpt import settings
from .forms import *
from .models import *
from .tokens import custom_token_generator
from .decorators import *
from django.utils.html import strip_tags
from datetime import datetime,date


def index_view(request):
    return render(request, 'index.html')

def calculate_age(dob):
    today = datetime.today().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email address')
            return render(request, 'register.html')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        if username in ['fm001', 'admin001']:
            messages.error(request, 'This username cannot be taken.')
            return render(request, 'register.html')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM client WHERE username = %s", [username])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Username already exists')
                    return render(request, 'register.html')
                cursor.execute("SELECT COUNT(*) FROM client WHERE email = %s", [email])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Email already registered')
                    return render(request, 'register.html')
                cursor.execute("SELECT COUNT(*) FROM client WHERE phone = %s", [phone])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Phone number already registered')
                    return render(request, 'register.html')
        except Exception as e:
            messages.error(request, f'Error checking username, email, or phone: {e}')
            return render(request, 'register.html')
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            if dob_date > datetime.today().date():
                messages.error(request, 'Date of birth cannot be in the future.')
                return render(request, 'register.html')
            age = calculate_age(dob_date)
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM-DD.')
            return render(request, 'register.html')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO client (name, email, phone, dob, username, password, age, date_joined) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
                    [name, email, phone, dob_date, username, password, age]
                )
            messages.success(request, 'Account created successfully')
            return redirect('login')  
        except Exception as e:
            messages.error(request, f'Error occurred: {e}')
            return render(request, 'register.html')
    return render(request, 'register.html')


from django.utils import timezone
from datetime import timedelta

def update_inactive_payments(user_id):
    now = timezone.now()

    threshold_date = now - timedelta(days=30)

    Payment.objects.filter(user_id=user_id, active=1, payment_date__lt=threshold_date).update(active=0)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Client.objects.get(username=username)
            if user.status == 1:
                if user.password == password:  
                    request.session['user_id'] = user.user_id 
                    request.session['username'] = user.username  
                    print(user.age)
                    update_inactive_payments(user.user_id)

                    return redirect('user_home')  
                else:
                    messages.error(request, 'Invalid username or password.')
        except Client.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')



def google_login_view(request):
    return render(request, 'google_login.html')


def forgot_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = Client.objects.get(username=username, email=email)
            current_site = get_current_site(request)
            token = custom_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))

            reset_link = f"http://localhost:8000/reset/{uid}/{token}/"

            subject = 'Password Reset Request'
            html_message = render_to_string('reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            plain_message = strip_tags(html_message)

            email = EmailMessage(
                subject,
                html_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            messages.success(request, 'A reset link has been sent to your email.')
            return redirect('login')

        except Client.DoesNotExist:
            messages.error(request, 'Invalid username or email.')
            return render(request,'forgot.html')
    return render(request, 'forgot.html')


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Client.objects.get(user_id=uid)
    except (TypeError, ValueError, OverflowError, Client.DoesNotExist):
        user = None

    if user and custom_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST, user=user)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password')
                user.password = new_password 
                user.save()

                send_mail(
                    'Password Reset Successful',
                    f'Hello {user.username}, your password in FITSCULPT has been successfully reset.Thank You',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = SetPasswordForm(user=user)
        return render(request, 'reset_password.html', {'form': form, 'valid_link': True})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('forgot')


@fm_custom_login_required
def fm_home_view(request):
    return render(request, 'fm_home.html')

@fm_custom_login_required
def fm_users(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, name, email, phone,dob, username,gender,age,height,weight,date_joined
            FROM client""")
        clients = cursor.fetchall()
        clients = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'dob': row[4],
                'username': row[5],
                'gender': row[6],
                'age': row[7],
                'height': row[8],
                'weight': row[9],
                'date_joined': row[10],
            } 
            for row in clients
        ]
        context = {
        'clients': clients,
    }
    return render(request, 'fm_users.html',context)

@fm_custom_login_required
def fm_payment(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * from tbl_payment""")
        payments = cursor.fetchall()
        payments = [
            {
                'payment_id': row[0],
                'plan_id': row[1],
                'user_id': row[2],
                'payment_date': row[3],
                'mode': row[4],
                'status': row[5],
            } 
            for row in payments
        ]
        context = {
        'payments': payments,
    }
    return render(request, 'fm_payment.html',context)


@admin_custom_login_required
def admin_payment(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * from tbl_payment""")
        payments = cursor.fetchall()
        payments = [
            {
                'payment_id': row[0],
                'plan_id': row[1],
                'user_id': row[2],
                'payment_date': row[3],
                'mode': row[4],
                'status': row[5],
            } 
            for row in payments
        ]
        context = {
        'payments': payments,
    }
    return render(request, 'admin_payment.html',context)

@fm_custom_login_required
def fm_profile_view(request):
    user_id = request.session.get('fm_user_id')  
    if user_id:
        tbl_fitness_manager = FitnessManager.objects.get(user_id=user_id)  
        
        if request.method == 'POST':
            form = FmUpdateForm(request.POST, instance=tbl_fitness_manager)
            if form.is_valid():
                form.save()
                return redirect('fm_home')
        else:
            form = FmUpdateForm(instance=tbl_fitness_manager)
        
        return render(request, 'fm_profile.html', {'form': form, 'tbl_fitness_manager': tbl_fitness_manager})
    return redirect('fm_login')

@fm_custom_login_required
def fm_logout_view(request):
    request.session.flush()
    return redirect('fm_login')


import datetime   
from  django.core.files.storage import FileSystemStorage
def fm_register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        qualification = request.POST.get('qualification')
        designation = request.POST.get('designation')
        certificate=request.FILES.get('certificate_proof',None)
        certificate_url=None
        if certificate:
            fs= FileSystemStorage()
            filename=fs.save(certificate.name,certificate)
            certificate_url=fs.url(filename)
        else:
            messages.error(request,'Please Upload Your certificate proof.')
            return render(request,'fm_register.html')
        try:
            with connection.cursor() as cursor:
                
                cursor.execute("SELECT COUNT(*) FROM tbl_fitness_manager WHERE email = %s", [email])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Email already registered')
                    return render(request, 'fm_register.html')

                cursor.execute("SELECT COUNT(*) FROM tbl_fitness_manager WHERE phone = %s", [phone])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Phone number already registered')
                    return render(request, 'fm_register.html')

                # Get qualification_id from the database
                cursor.execute("SELECT qualification_id FROM tbl_qualifications WHERE qualification = %s", [qualification])
                qualification_id = cursor.fetchone()
                if not qualification_id:
                    messages.error(request, 'Invalid qualification selected')
                    return render(request, 'fm_register.html')
                qualification_id = qualification_id[0]

                # Get designation_id from the database
                cursor.execute("SELECT designation_id FROM tbl_designations WHERE designation = %s", [designation])
                designation_id = cursor.fetchone()
                if not designation_id:
                    messages.error(request, 'Invalid designation selected')
                    return render(request, 'fm_register.html')
                designation_id = designation_id[0]

                # Insert into tbl_fitness_manager
                date_joined = datetime.now()
                cursor.execute("""
                    INSERT INTO tbl_fitness_manager (name, email, phone, qualification_id, designation_id,certificate_proof, date_joined)
                    VALUES (%s, %s, %s, %s, %s, %s,%s)
                """, [name, email, phone, qualification_id, designation_id,filename, date_joined])
                messages.success(request, 'You have requested for job successfully')
                messages.success(request, 'You Will get a mail from FITSCULPT regarding your Application Status...')

                return redirect('fm_register')

        except Exception as e:
            messages.error(request, f'Error processing your request: {e}')
            return render(request, 'fm_register.html')

    return render(request, 'fm_register.html')

def fm_forgot_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = FitnessManager.objects.get(username=username, email=email)
            current_site = get_current_site(request)
            token = custom_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))

            reset_link = f"http://localhost:8000/fm_reset/{uid}/{token}/"

            subject = 'Password Reset Request'
            html_message = render_to_string('fm_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            plain_message = strip_tags(html_message)

            email = EmailMessage(
                subject,
                html_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            messages.success(request, 'A reset link has been sent to your email.')
            return redirect('fm_login')

        except FitnessManager.DoesNotExist:
            messages.error(request, 'Invalid username or email.')

    return render(request, 'fm_forgot.html')

def fm_reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"Decoded UID: {uid}")
        user = FitnessManager.objects.get(user_id=uid)
        print(f"Retrieved User: {user}")
    except (TypeError, ValueError, OverflowError, FitnessManager.DoesNotExist):
        user = None
        print("User retrieval failed")

    if user and custom_token_generator.check_token(user, token):
        print("Token is valid")
        if request.method == 'POST':
            form = Fm_SetPasswordForm(request.POST, user=user)
            if form.is_valid():
                print("Form is valid")
                new_password = form.cleaned_data.get('new_password')
                user.password = new_password 
                user.save()
                print("Password updated successfully")

                send_mail(
                    'Password Reset Successful',
                    f'Hello {user.username}, your password in FITSCULPT has been successfully reset.Thank You',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('fm_login')
            else:
                print("Form is not valid")
                print(form.errors)
        else:
            form = Fm_SetPasswordForm(user=user)
        return render(request, 'fm_reset_password.html', {'form': form, 'valid_link': True})
    else:
        print("Token is invalid or link has expired")
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('fm_forgot')



def fm_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = FitnessManager.objects.get(username=username)
            if user.status == 1: 
                if user.password == password:  
                    request.session['fm_user_id'] = user.user_id 
                    request.session['username'] = user.username  
                    return redirect('fm_home')  
                
                else:
                    messages.error(request, 'Invalid username or password.')
        except FitnessManager.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'fm_login.html')
from django.utils import timezone
from datetime import timedelta

def update_inactive_payments(user_id):
    now = timezone.now()

    threshold_date = now - timedelta(days=30)

    Payment.objects.filter(user_id=user_id, active=1, payment_date__lt=threshold_date).update(active=0)


@custom_login_required
def user_home_view(request):
    return render(request, 'user_home.html')
@custom_login_required
def user_profile_view(request):
    user_id = request.session.get('user_id')  

    if user_id:
        client = Client.objects.get(user_id=user_id)  
        
        if request.method == 'POST':
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect('user_home')
        else:
            form = ClientUpdateForm(instance=client)
        
        bmi = None
        if client.height and client.weight:  
            height_in_meters = client.height / 100  
            bmi = client.weight / (height_in_meters ** 2)

        return render(request, 'user_profile.html', {'form': form, 'client': client, 'bmi': bmi})
    return redirect('login')

@custom_login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')


from django.shortcuts import render
from .models import Plan, Client  

@custom_login_required
def plans_view(request):
    plans = Plan.objects.all()  
    plan_id = request.POST.get('plan_id')
    user_id = request.session.get('user_id')
    previous_plan_amount = request.session.get('previous_plan_amount', None)
 
    print(user_id, plan_id)
    
    user_age = None
    if user_id:
        try:
            client = Client.objects.get(user_id=user_id)
            user_age = client.age 
        except Client.DoesNotExist:
            user_age = None

    is_child_plan_enabled = user_age is not None and user_age < 12

    # Check if the user has an active plan (active=1)
    user_has_plan = Payment.objects.filter(user_id=user_id, active=1).exists()

    current_plan = None
    current_plan_name = None
    if user_has_plan:
        payment_record = Payment.objects.filter(user_id=user_id, active=1).first()
        if payment_record:
            current_plan = payment_record.plan_id

            # Get the current plan name
            plan_record = Plan.objects.filter(plan_id=current_plan).first()
            if plan_record:
                current_plan_name = plan_record.plan_name
    
    print(current_plan)
    print(current_plan_name)
    
    return render(request, 'plans.html', {
        'plans': plans,
        'is_child_plan_enabled': is_child_plan_enabled,
        'user_has_plan': user_has_plan,
        'current_plan': current_plan,
        'current_plan_name': current_plan_name,
        'previous_plan_amount': previous_plan_amount
    })

from django.shortcuts import render, redirect
from .models import Plan, Payment 
from django.utils import timezone  
@custom_login_required
def payment_gateway_view(request, plan_id):
    user_id = request.session.get('user_id')
    
    try:
        plan = Plan.objects.get(plan_id=plan_id)
    except Plan.DoesNotExist:
        messages.error(request, "Plan not found.")
        return redirect('plans')

    if request.method == 'POST':
        # Process payment here
        payment = Payment(
            plan_id=plan_id,
            user_id=user_id,
            payment_date=timezone.now(),
            mode='online',
            status='success',
            active=1
        )
        payment.save()  
        return render(request, 'user_home.html')

    # If it's a GET request, just render the payment gateway form
    return render(request, 'payment_gateway.html', {'plan': plan})

from datetime import datetime
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from .models import Payment  # Adjust according to your models

@custom_login_required
def delete_plan(request):
    if request.method == 'POST':
        # Fetch the user ID from the session
        user_id = request.session.get('user_id')
        print("User ID:", user_id)

        # Fetch the plan ID from the POST data
        plan_id = request.POST.get('plan_id')
        print("Plan ID:", plan_id)

        # Fetch the payment records associated with the user
        payment_records = Payment.objects.filter(user_id=user_id, active=1)

        # Check if there are any active payment records
        if payment_records.exists():
            for payment_record in payment_records:
                plan = Plan.objects.filter(plan_id=payment_record.plan_id).first()
                if plan:
                    # Store the plan amount in the session
                    request.session['previous_plan_amount'] = plan.amount

                # Update the active field to 0
                payment_record.active = 0
                payment_record.save()
            messages.success(request, "Your plan has been successfully deactivated.")
        else:
            messages.warning(request, "No active plan found for deactivation.")

        # Redirect to the plans page
        return redirect('plans')  # Adjust the redirect as needed

    # If not a POST request, redirect to plans
    return redirect('plans')


from django.shortcuts import redirect
@custom_login_required
def select_plan_view(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        user_id=request.session.get('user_id')
        # You can add any additional logic here if needed
        return redirect('payment_gateway', plan_id=plan_id)
    return redirect('plans')

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin001' and password == 'admin001':
            request.session['admin_username'] =username
            request.session['admin_password'] =password  
            return redirect('admin_home')
    return render(request, 'admin_login.html')

@admin_custom_login_required
def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


@admin_custom_login_required
def admin_home_view(request):
    return render(request, 'admin_home.html')
@admin_custom_login_required
def admin_users_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, name, email, phone, username, date_joined
            FROM client where status=1 """)
        clients = cursor.fetchall()
        clients = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'username': row[4],
                'date_joined': row[5],
            } 
            for row in clients
        ]

        cursor.execute("""
            SELECT user_id, name, email, phone, username, date_joined
            FROM client where status=0 """)
        rm_clients = cursor.fetchall()
        rm_clients = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'username': row[4],
                'date_joined': row[5],
            } 
            for row in rm_clients
        ]
        context = {
        'clients': clients,
        'rm_clients': rm_clients,
    }
    return render(request, 'admin_users.html',context)
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from django.conf import settings
from django.shortcuts import render
from django.db import connection

@admin_custom_login_required
def admin_fm_view(request):
    with connection.cursor() as cursor:
        # Fetch fitness managers without a username and password
        cursor.execute("""
            SELECT user_id, name, email, phone, qualification_id, designation_id, certificate_proof 
            FROM tbl_fitness_manager 
            WHERE username='' AND password=''
        """)
        applicants = cursor.fetchall()
        applicants = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'qualification_id': row[4],
                'designation_id': row[5],
                'certificate_proof': row[6],
            } 
            for row in applicants
        ]
        
        # Fetch fitness managers with a username and password
        cursor.execute("""
            SELECT user_id, name, email, phone, qualification_id, designation_id, certificate_proof, username, password
            FROM tbl_fitness_manager 
            WHERE username != '' AND password != '' && status=1
        """)
        complete_fms = cursor.fetchall()
        complete_fms = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'qualification_id': row[4],
                'designation_id': row[5],
                'certificate_proof': row[6],
                'username': row[7],
                'password': row[8],
            }
            for row in complete_fms
        ]
        
        cursor.execute("""
            SELECT user_id, name, email, phone, qualification_id, designation_id, certificate_proof, username, password
            FROM tbl_fitness_manager 
            WHERE status=0
        """)
        removed_fms = cursor.fetchall()
        removed_fms = [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'qualification_id': row[4],
                'designation_id': row[5],
                'certificate_proof': row[6],
                'username': row[7],
                'password': row[8],
            }
            for row in removed_fms
        ]

    context = {
        'applicants': applicants,
        'complete_fms': complete_fms,
        'removed_fms' : removed_fms,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'admin_fm.html', context)

def delete_fm(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE tbl_fitness_manager SET status=0 WHERE user_id = %s", [user_id])
    return redirect('admin_fm')
def delete_client(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE client SET status=0 WHERE user_id = %s", [user_id])
    return redirect('admin_users')

def accept_fm_view(request, user_id):
    with connection.cursor() as cursor:
        username = get_random_string(8)
        password = get_random_string(12) 
        
        cursor.execute("SELECT email FROM tbl_fitness_manager WHERE user_id = %s", [user_id])
        email = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE tbl_fitness_manager
            SET username = %s, password = %s
            WHERE user_id = %s
        """, [username, password, user_id])

        send_mail(
            'Congratulations... You are Seleceted as Fitness Manager In FITSCULPT'
            'Your Fitness Manager Account Credentials',
            f'Your account has been approved.\nUsername: {username}\nPassword: {password}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

    return redirect('admin_fm')  
@admin_custom_login_required
def view_certificate(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT certificate_proof FROM tbl_fitness_manager WHERE user_id = %s", [user_id])
        certificate_proof = cursor.fetchone()[0]
    
    certificate_url = settings.MEDIA_URL + certificate_proof
    print(certificate_url)
    
    return render(request, 'media.html', {'certificate_url': certificate_url})
@custom_login_required
def view_workout_img(request, workout_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT workout_image FROM tbl_workouts WHERE workout_id = %s", [workout_id])
        workout_image = cursor.fetchone()[0]
    
    workout_url = settings.MEDIA_URL + workout_image
    print(workout_url)
    
    return render(request, 'workout_media.html', {'workout_url': workout_url})

from django.shortcuts import render, redirect
from .models import Workout
from django.core.files.storage import FileSystemStorage
@fm_custom_login_required
def fm_workouts_view(request):
    return render(request, 'fm_workouts.html')
@fm_custom_login_required
def see_all_workouts(request):
    workouts = Workout.objects.all()
    return render(request, 'fm_workouts.html', {'workouts': workouts})


from django.shortcuts import render, redirect
from .models import Workout, Plan, Service
from django.core.files.storage import FileSystemStorage

@fm_custom_login_required
def add_workout(request):
    if request.method == 'POST':
        # Get form data
        workout_name = request.POST['workout_name']
        description = request.POST['description']
        body_part = request.POST['body_part']
        duration = request.POST['duration']
        workout_image = request.FILES['workout_image']
        
        # Save the workout details and get the workout_id
        workout = Workout(
            workout_name=workout_name,
            description=description,
            body_part=body_part,
            duration=duration,
            workout_image=workout_image
        )
        workout.save()  # This saves the workout and assigns the workout_id
        workout_id = workout.workout_id  # Get the auto-incremented workout_id

        # Get the selected plans from the form
        selected_plans = request.POST.getlist('plans')
        
        for plan_id in selected_plans:
            plan = Plan.objects.get(plan_id=plan_id)
            
            # Create Service for each selected plan
            if plan.plan_name == 'Basic Plan':
                service_no = 1
                service_type = 'Basic'
                service_description = 'Basic plan including 5 workouts for each body part'
                category = 'plan 1'
            elif plan.plan_name == 'Standard Plan':
                service_no = 2
                service_type = 'Standard'
                service_description = 'Standard plan including 7 workouts for each body part'
                category = 'plan 2'
            elif plan.plan_name == 'Premium Plan':
                service_no = 3
                service_type = 'Premium'
                service_description = 'Premium plan including 9 workouts for each body part'
                category = 'plan 3'
            elif plan.plan_name == 'Child Plan':
                service_no = 4
                service_type = 'Child'
                service_description = 'Child plan including 4 workouts for each body part'
                category = 'plan 4'
            
            service = Service(
                service_no=service_no,
                service_type=service_type,
                workout_id=workout_id,  # Use workout_id here
                nutrition_no=5,  # Example value, you can modify this
                description=service_description,
                category=category,
                day=1 if body_part.strip().lower() == 'chest' else   # Day 1 for chest
        2 if body_part.strip().lower() == 'back' else    # Day 2 for back
        3 if body_part.strip().lower() == 'biceps' else  # Day 3 for biceps
        4 if body_part.strip().lower() == 'triceps' else # Day 4 for triceps
        5 if body_part.strip().lower() == 'shoulder' else# Day 5 for shoulder
        6 if body_part.strip().lower() == 'leg' else 0     # Day 6 for leg
            )
            service.save()
        
        # Redirect to workout list page after submission
        return redirect('see_all_workouts')
    
    # Fetch available plans from the database
    plans = Plan.objects.all()
    return render(request, 'add_workout.html', {'plans': plans})

from django.shortcuts import render, redirect
from .models import Workout, Plan, Service

@fm_custom_login_required
def update_workout(request, workout_id):
    # Fetch the workout object
    workout = Workout.objects.get(workout_id=workout_id)

    # Fetch associated services for this workout
    associated_services = Service.objects.filter(workout_id=workout_id)

    # Get the service_no(s) from associated services
    associated_service_nos = [service.service_no for service in associated_services]

    # Fetch plans from tbl_plans
    all_plans = Plan.objects.all()

    # Get associated plans (pre-select these in the dropdown)
    associated_plans = Plan.objects.filter(service_no__in=associated_service_nos)

    if request.method == 'POST':
        # Handle form submission for updating the plans
        selected_plan_ids = request.POST.getlist('plans')  # Get selected plan IDs from the form
        
        # Clear existing services for this workout
        Service.objects.filter(workout_id=workout_id).delete()

        # Add the newly selected plans
        for plan_id in selected_plan_ids:
            plan = Plan.objects.get(plan_id=plan_id)

            # Initialize variables for service creation
            service_no = 0
            service_type = ''
            service_description = ''
            category = ''

            if plan.plan_name == 'Basic Plan':
                service_no = 1
                service_type = 'Basic'
                service_description = 'Basic plan including 5 workouts for each body part'
                category = 'plan 1'
            elif plan.plan_name == 'Standard Plan':
                service_no = 2
                service_type = 'Standard'
                service_description = 'Standard plan including 7 workouts for each body part'
                category = 'plan 2'
            elif plan.plan_name == 'Premium Plan':
                service_no = 3
                service_type = 'Premium'
                service_description = 'Premium plan including 9 workouts for each body part'
                category = 'plan 3'
            elif plan.plan_name == 'Child Plan':
                service_no = 4
                service_type = 'Child'
                service_description = 'Child plan including 4 workouts for each body part'
                category = 'plan 4'

            # Determine the day based on the workout body part
            day = {
                'chest': 1,
                'back': 2,
                'biceps': 3,
                'triceps': 4,
                'shoulder': 5,
                'leg': 6
            }.get(workout.body_part.strip().lower(), 0)  # Default to 0 if not found

            # Create and save the service
            service = Service(
                service_no=service_no,
                service_type=service_type,
                workout_id=workout_id,
                nutrition_no=5,  # You can set this dynamically if needed
                description=service_description,
                category=category,
                day=day
            )
            service.save()

        return redirect('see_all_workouts')  # Redirect to workout list after update

    context = {
        'workout': workout,
        'all_plans': all_plans,  # All available plans
        'associated_plans': associated_plans,  # Plans already linked to the workout
    }

    return render(request, 'update_workout.html', context)



@fm_custom_login_required
def delete_workout(request, workout_id):
    workout = Workout.objects.get(workout_id=workout_id)
    if request.method == 'POST':
        workout.delete()
        return redirect('see_all_workouts')

    return render(request, 'delete_workout.html', {'workout': workout})  # Confirm delete



from django.shortcuts import render, redirect
from .models import Workout
from django.core.files.storage import FileSystemStorage
@fm_custom_login_required
def fm_nutritions_view(request):
    return render(request, 'fm_nutritions.html')
@fm_custom_login_required
def see_all_food(request):
    foods = FoodDatabase.objects.all()
    return render(request, 'fm_nutritions.html', {'foods': foods})

@fm_custom_login_required
def add_food(request):
    # Fetch unique nutrition_no and their descriptions
    nutrition_options = Nutrition.objects.values('nutrition_no').annotate(
        first_description=models.F('description')
    ).distinct()

    if request.method == 'POST':
        food_name = request.POST['food_name']
        food_type = request.POST['food_type']
        calories = request.POST['calories']
        proteins = request.POST['proteins']
        carbs = request.POST['carbs']
        fats = request.POST['fats']

        # Create the food entry
        food = FoodDatabase(
            food_name=food_name,
            food_type=food_type,
            calories=calories,
            proteins=proteins,
            carbs=carbs,
            fats=fats
        )
        food.save()  # Save the food entry

        food_id = food.food_id  # Get the newly created food_id
        print(food_id)

        selected_nutrition_nos = request.POST.getlist('nutritional_descriptions')  # Get selected nutrition_nos

        # Insert entries for each selected nutrition_no
        for nutrition_no in selected_nutrition_nos:
            # Use filter() to get a queryset
            nutrition_entries = Nutrition.objects.filter(nutrition_no=nutrition_no)
            if nutrition_entries.exists():
                nutrition_entry = nutrition_entries.first()  # Get the first matching entry

                # Create a new Nutrition entry for each selected nutrition_no
                Nutrition.objects.create(
                    nutrition_no=nutrition_entry.nutrition_no,  # Store the nutrition_no
                    food_id=food_id,                             # Associate with the new food_id
                    description=nutrition_entry.description      # Fetch the description
                )

        return redirect('see_all_food')  # Redirect to see all food after adding

    context = {
        'nutrition_options': nutrition_options,
    }

    return render(request, 'add_food.html', context)





@fm_custom_login_required
def update_food(request, food_id):
    food = FoodDatabase.objects.get(food_id=food_id)
    if request.method == 'POST':
        food.food_name = request.POST['food_name']
        food.food_type = request.POST['food_type']
        food.calories = request.POST['calories']
        food.proteins = request.POST['proteins']
        food.carbs = request.POST['carbs']
        food.fats = request.POST['fats']
        food.save()
        return redirect('see_all_food')

    return render(request, 'update_food.html', {'food': food})  # Render form with workout details
@fm_custom_login_required
def delete_food(request, food_id):
    food = FoodDatabase.objects.get(food_id=food_id)
    if request.method == 'POST':
        food.delete()
        return redirect('see_all_food')

    return render(request, 'delete_food.html', {'food': food})  # Confirm delete


from django.shortcuts import render
from .models import Plan, Service, Workout
from django.db import connection

@custom_login_required
def workouts_view(request, day=None):
    user_id = request.session.get('user_id')

    # Fetch plan_id from tbl_payment
    with connection.cursor() as cursor:
        cursor.execute("SELECT plan_id FROM tbl_payment WHERE user_id = %s AND status = 'success'", [user_id])
        result = cursor.fetchone()
        plan_id = result[0] if result else None

    plan = None
    workouts = []

    if plan_id:
        plan = Plan.objects.get(plan_id=plan_id)

        if day:
            services = Service.objects.filter(service_no=plan.service_no, day=day)

            for service in services:
                workout = Workout.objects.get(workout_id=service.workout_id)
                workouts.append(workout)

    context = {
        'plan': plan,
        'workouts': workouts,
        'error': 'No workouts found for this day.' if not workouts and day else ''
    }
    return render(request, 'workouts.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Plan, Service, Workout
from django.db import connection

@custom_login_required
def workouts_by_day_view(request, day):
    user_id = request.session.get('user_id')

    # Fetch plan_id from tbl_payment
    with connection.cursor() as cursor:
        cursor.execute("SELECT plan_id FROM tbl_payment WHERE user_id = %s AND status = 'success'", [user_id])
        result = cursor.fetchone()
        plan_id = result[0] if result else None

    if plan_id:
        # Fetch the plan details
        plan = Plan.objects.get(plan_id=plan_id)

        # Fetch services associated with the plan for the selected day
        services = Service.objects.filter(service_no=plan.service_no, day=day)

        # Get the corresponding workouts
        workouts = []
        for service in services:
            workout = Workout.objects.get(workout_id=service.workout_id)
            workouts.append(workout)

        # Render the template with the workouts
        context = {
            'plan': plan,
            'workouts': workouts,
        }
        return render(request, 'workouts.html', context)
    else:
        return render(request, 'workouts.html', {'error': 'No active plan found.'})

from django.shortcuts import render, redirect
from .models import Client, Nutrition, FoodDatabase
from django.db.models import Q

@custom_login_required
def nutrition_view(request):
    user_id = request.session.get('user_id')

    if user_id:
        client = Client.objects.get(user_id=user_id)
        height_in_meters = client.height / 100 if client.height else None
        bmi = client.weight / (height_in_meters ** 2) if client.weight and client.height else None

        if bmi:
            if bmi < 18.5:
                nutrition_category = 'Underweight'
            elif 18.5 <= bmi < 24.9:
                nutrition_category = 'Normal'
            elif 25 <= bmi < 29.9:
                nutrition_category = 'Overweight'
            else:
                nutrition_category = 'Obesity'
        else:
            return render(request, 'nutritions.html', {'error': 'Please update your height and weight to get nutrition suggestions.'})

        food_type = 'Vegetarian' if client.food_type == 'veg' else 'Non Vegetarian'

        if nutrition_category == 'Underweight':
            nutrition = Nutrition.objects.filter(Q(nutrition_no__in=[1, 4]) if food_type == 'Vegetarian' else Q(nutrition_no__in=[5, 8]))
        elif nutrition_category == 'Normal':
            nutrition = Nutrition.objects.filter(Q(nutrition_no=4) if food_type == 'Vegetarian' else Q(nutrition_no=8))
        elif nutrition_category == 'Overweight':
            nutrition = Nutrition.objects.filter(Q(nutrition_no__in=[3, 4]) if food_type == 'Vegetarian' else Q(nutrition_no__in=[7, 8]))
        else:
            nutrition = Nutrition.objects.filter(Q(nutrition_no=3) if food_type == 'Vegetarian' else Q(nutrition_no=7))

        # Now, fetch all food items associated with the nutrition_no
        food_details = []
        for item in nutrition:
            foods = FoodDatabase.objects.filter(food_id=item.food_id).all()  # Assuming food_id relates to the Nutrition
            for food in foods:
                food_details.append({
                    'nutrition_id': item.nutrition_id,
                    'nutrition_description': item.description,
                    'food_name': food.food_name,
                    'calories': food.calories,
                    'proteins': food.proteins,
                    'carbs': food.carbs,
                    'fats': food.fats,
                })

        return render(request, 'nutritions.html', {
            'nutrition': nutrition,
            'food_details': food_details,
            'bmi': bmi,
            'client': client,
            'nutrition_category': nutrition_category
        })
    
    return redirect('login')


@fm_custom_login_required
def fm_nutritions_view(request):
    return render(request, 'fm_nutritions.html')

@fm_custom_login_required
def fm_plans(request):
    plans = Plan.objects.all()
    return render(request, 'fm_plans.html', {'plans': plans})

@fm_custom_login_required
def fm_nutritions2(request):
    nutritions = Nutrition.objects.all()
    return render(request, 'fm_nutritions2.html', {'nutritions': nutritions})

@admin_custom_login_required
def admin_plans(request):
    return render(request, 'admin_plans.html')

@admin_custom_login_required
def see_all_plan(request):
    plans = Plan.objects.all()
    return render(request, 'admin_plans.html', {'plans': plans})

@admin_custom_login_required
def add_plan(request):
    if request.method == 'POST':
        plan_name = request.POST['plan_name']
        amount = request.POST['amount']
        description = request.POST['description']
        service_no = request.POST['service_no']    
        plan = Plan(
            plan_name=plan_name,
            amount=amount,
            description=description,
            service_no=service_no
        )
        plan.save()  
        plan_id = plan.plan_id  
        print(plan_id)
                
        return redirect('see_all_plan')
    
    plans = Plan.objects.all()
    return render(request, 'add_plan.html', {'plans': plans})



@admin_custom_login_required
def update_plan(request, plan_id):
    plan = Plan.objects.get(plan_id=plan_id)
    if request.method == 'POST':
        plan.plan_name = request.POST['plan_name']
        plan.amount = request.POST['amount']
        plan.description = request.POST['description']
        plan.service_no = request.POST['service_no'] 
        plan.save()
        return redirect('see_all_plan')

    return render(request, 'update_plan.html', {'plan': plan})  
@admin_custom_login_required
def admin_delete_plan(request, plan_id):
    plan = Plan.objects.get(plan_id=plan_id)
    if request.method == 'POST':
        plan.delete()
        return redirect('see_all_plan')

    return render(request, 'admin_delete_plan.html', {'plan': plan}) 