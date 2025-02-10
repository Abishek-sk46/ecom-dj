from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Post, Aboutus
from django.core.paginator import Paginator
from .forms import ContactForm, RegisterForm
import logging

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
            form.save()  # user data created
            print("Register Success")
            return redirect('blog:index')
    return render(request, 'register.html', {'form': form})