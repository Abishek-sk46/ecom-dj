from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    # posts = models.ManyToManyField(Post, related_name='categories')

    def __str__(self):
        return self.name

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    img_url = models.ImageField(null=True, upload_to='posts/images')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=False, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def formatted_img_url(self):
        url=self.img_url if self.img_url.__str__().startswith(('http','https')) else f'/media/{self.img_url}'
        return url

    def __str__(self):
        return self.title

class Aboutus(models.Model):
    content = models.TextField()