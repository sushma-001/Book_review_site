from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings  # To reference the custom user model
from django.core.validators import MinValueValidator, MaxValueValidator


class ReaderManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # This hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Reader(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Username can only contain letters, digits, and @/./+/-/_ characters."
            )
        ]
    )
    email = models.EmailField(unique=True)
    
    # Admin-related fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Allows access to Django admin
    is_superuser = models.BooleanField(default=False)  # Grants all permissions

    REQUIRED_FIELDS = ['email']  # Password is handled by AbstractBaseUser
    USERNAME_FIELD = 'username'

    objects = ReaderManager()

    def save(self, *args, **kwargs):
        # Hash the password if it is not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='books')

    def __str__(self):
        return self.title

class ToBeRead(models.Model):
    reader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} - To Be Read by {self.reader.username}"

class CurrentlyReading(models.Model):
    reader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} - Currently Reading by {self.reader.username}"

class Read(models.Model):
    reader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    finish_date = models.DateTimeField(auto_now_add=True)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.book.title} - Read by {self.reader.username}"
