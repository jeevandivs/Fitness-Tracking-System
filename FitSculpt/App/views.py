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
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Client.objects.get(username=username)
            if user.password == password:  
                request.session['user_id'] = user.user_id 
                request.session['username'] = user.username  
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
                date_joined = datetime.datetime.now()
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
            if user.password == password:  
                request.session['fm_user_id'] = user.user_id 
                request.session['username'] = user.username  
                return redirect('fm_home')  
                
            else:
                messages.error(request, 'Invalid username or password.')
        except FitnessManager.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'fm_login.html')


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
        
        return render(request, 'user_profile.html', {'form': form, 'client': client})
    return redirect('login')

@custom_login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin001' and password == 'admin001':
            return render(request, 'admin_home.html')
    return render(request, 'admin_login.html')

def admin_home_view(request):
    return render(request, 'admin_home.html')
def admin_users_view(request):
    return render(request, 'admin_users.html')
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

def admin_fm_view(request):
    with connection.cursor() as cursor:
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
    
    return render(request, 'admin_fm.html', {'applicants': applicants, 'MEDIA_URL': settings.MEDIA_URL})

    

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

def view_certificate(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT certificate_proof FROM tbl_fitness_manager WHERE user_id = %s", [user_id])
        certificate_proof = cursor.fetchone()[0]
    
    certificate_url = settings.MEDIA_URL + certificate_proof
    print(certificate_url)
    
    return render(request, 'media.html', {'certificate_url': certificate_url})

