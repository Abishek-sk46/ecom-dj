from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Post, Aboutus
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPasswordForm, LoginForm, PostForm, RegisterForm, ResetPasswordForm
import logging
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib.auth.models import User
# forgotpassword
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

# send email
from django.core.mail import send_mail



def index(request):
    blog_title = "Latest Posts"
    all_posts = Post.objects.all()
    paginator = Paginator(all_posts, 4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, "index.html", {'blog_title': blog_title, 'posts': posts})

def detail(request, slug):
    post = Post.objects.get(slug=slug)
    related_posts = Post.objects.filter(category=post.category).exclude(slug=slug)
    return render(request, "detail.html", {'post': post, 'related_posts': related_posts})

def old_url(request):
    return redirect('new_url')

def new_url(request):
    return HttpResponse("Hello, world. You're at the new url.")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if form.is_valid():
            logger = logging.getLogger("TESTING")
            logger.debug(f"POST data: {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}")
            success_message = "Your message has been sent successfully!"
            return render(request, "contact.html", {'form': form, 'success_message': success_message})
        else:
            logger.debug('Form is invalid')
        return render(request, "contact.html", {'form': form, 'name': name, 'email': email, 'message': message})
    return render(request, "contact.html")

def about(request):
    content = Aboutus.objects.first()
    if content is None or not content.content:
        content = "Default content goes here."
    else:
        content = content.content
    return render(request, "about.html", {'content': content})

def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password']) # password hashed
            user.save()
              # user data created
            messages.success(request, 'User created successfully')
            return redirect('blog:login')
    return render(request, 'register.html', {'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login succes')
                return redirect('blog:dashboard')

    return render(request, 'login.html',{'form':form})

def dashboard(request):
    blog_title = "My Posts"
    # getting user post
    all_posts=Post.objects.filter(user=request.user)
    paginator = Paginator(all_posts, 4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, 'dashboard.html' , {'blog_title': blog_title, 'posts':posts,})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout succes')
    return redirect('blog:index')

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form =ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            # send email with reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = 'Reset Your Password'
            message = render_to_string('reset_password_email.html', {
                'domain': domain,
                'uid': uid,
                'token': token,
            })

            send_mail(subject, message, 'noreply@gmail.com', [email])
            messages.success(request, 'Email has been sent with password reset link')


    return render(request,'forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    form = ResetPasswordForm()
    if request.method == 'POST':
        form =ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)

            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset succes')
                return redirect('blog:login')
            else:
                messages.error(request, 'Invalid Link')
                return redirect('blog:login')
    return render(request, 'reset_password.html')


def new_post(request):
    form=PostForm()
    categories= Category.objects.all()
    if request.method == 'POST':
        form=PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('blog:dashboard')
            
    return render(request,'new_post.html',{'categories':categories , 'form':form})