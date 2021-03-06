from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import auth
from .models import CustomUser
from django.contrib import messages
from django.conf import settings 
from django.core.mail import send_mail 
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import token_generator
from django.contrib.auth.base_user import BaseUserManager

# def random_password(size=8):
#     return BaseUserManager().make_random_password(size)

def register(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        #username = request.POST['username']
        Email = request.POST['email']
        #password1 = request.POST['password1']
        #password2 = request.POST['password2']
        phone = request.POST['phone']
        alt_phone = request.POST['alt_phone']
        designation = request.POST['designation']
        address = request.POST['address']

        #if password1 == password2:
        # if CustomUser.objects.filter(username=username).exists():
        #     messages.info(request, 'Username Taken')
            #return redirect('register')
        if CustomUser.objects.filter(email=Email).exists():
            messages.info(request, 'Email Taken')
            return redirect('register')
        else:
            
            user = CustomUser.objects.create_user(username=Email, password="", email=Email, first_name=fname, last_name=lname, phone=phone, alt_phone=alt_phone, designation=designation, address=address)
            user.is_active = False
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = "http://"+domain+link
            email_body = 'Hi ' + user.first_name + ' Please use this link to verify your account\n'+ activate_url
            email = EmailMessage(
                'Activate your account',
                email_body,
                'rohan@gmail.com',
                [Email],
            )
            email.send(fail_silently=False)

            return redirect('email_ver_msg')
        #else:
            #messages.info(request, 'Password did not match')
            #return redirect('register')
    else:    
        return render(request, 'account/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('uname_pw_gen')
            user.is_active = True
            password = BaseUserManager().make_random_password(10)
            user.set_password(password)
            user.save()
            email_body = 'Hi ' + user.first_name+' \n Your username: '+ user.email+ '\n Your Password: '+password
            email = EmailMessage(
                'Activate your account',
                email_body,
                'rohan@gmail.com',
                [user.email],
            )
            email.send(fail_silently=False)
            

            messages.success(request, 'Account activated successfully')
            return redirect('uname_pw_gen')

        except Exception as ex:
            pass

        return redirect('uname_pw_gen')

def email_ver_msg(request):
    return render(request, 'account/email_ver_msg.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('login')

    else:
        return render(request, 'account/login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def forgot_uname(request):
    if request.method == 'POST':
        email = request.POST['email']
        if CustomUser.objects.filter(email=email).exists():
            p = CustomUser.objects.raw('SELECT * FROM account_customuser WHERE email = %s', [email])
            subject = 'Request for username'
            message = f'Hi Your Username is: {p[0].username}'
            email_from = settings.EMAIL_HOST_USER 
            recipient_list = [email, ] 
            send_mail( subject, message, email_from, recipient_list ) 
            return redirect('login')
        else:
            messages.info(request, 'Email not registered')
            return redirect('forgot_uname')
    else:
        return render(request, 'account/forgot_uname.html')

def uname_pw_gen(request):
    return render(request, 'account/uname_pw_gen.html')
