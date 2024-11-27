from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Reader,ToBeRead # Import your custom Reader model
import requests
import json
from django.views.decorators.http import require_POST
@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')

def SignUpPage(request):
    if request.method == 'POST':
        uname = request.POST.get('fullname')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')

        if pass1 != pass2:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
        else:
            try:
                my_user = Reader.objects.create_user(username=uname, email=email, password=pass1)
                my_user.save()
                return JsonResponse({'redirect_url': '/login/'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')

        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return JsonResponse({'redirect_url': '/home/'}, status=200)  # Redirect on successful login
        else:
            return JsonResponse({'error': 'Username or Password is incorrect'}, status=400)
    return render(request, 'login.html')

def LogOut(request):
    logout(request)
    return redirect('login')


def BaseHome(request):
    return render(request, 'base-home.html')


def ProfilePage(request):
    return render(request, 'profile.html')

def SearchPage(request):
    return render(request,'search.html')


def genre_search(request, genre=None):
    if genre:
        # Fetch books related to the genre using the Open Library API
        response = requests.get(f'https://openlibrary.org/search.json?subject={genre}')
        data = response.json()
        books = data.get('docs', [])[:20]  # Limit results to top 10 for display
        return render(request, 'genre_search.html', {'books': books, 'genre': genre})
    else:
        # Since Open Library API doesn't provide a genre list, define a static list of genres
        genres = ['Fiction', 'Non-fiction', 'Sci-Fi', 'Fantasy', 'Mystery']  # Example genres
        return render(request, 'genre_search.html', {'genres': genres})

@login_required(login_url='login')
def add_to_tbr(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        author = data.get('author')
        cover_url = data.get('cover_url')

        # Find or create the book in the Book model
        book, created = Reader.objects.get_or_create(
            title=title,
            author=author,
            defaults={'cover_image': cover_url}
        )

        # Check if the book is already in the user's TBR list
        if not ToBeRead.objects.filter(reader=request.user, book=book).exists():
            ToBeRead.objects.create(reader=request.user, book=book)
            return JsonResponse({'success': True, 'message': 'Book added to TBR list'}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'Book already in TBR list'}, status=400)
        
        
def ToBeReadView(request):
    if request.user.is_authenticated:
        # Fetch the books from ToBeRead model for the authenticated user
        tbr_books = ToBeRead.objects.filter(reader=request.user)
        context = {
            'tbr_books': tbr_books,
        }
        return render(request, 'tbr.html', context)
    else:
        return redirect('login')  # Redirect to login if user is not authenticated
  
@require_POST  # This ensures only POST requests are accepted
def update_status(request, book_id):
      if request.method == 'POST':
        try:
            book = Reader.objects.get(id=book_id)
            reader = request.user  # Get the currently logged-in user

            # Create a new ToBeRead entry if it doesn't already exist
            ToBeRead.objects.get_or_create(reader=reader, book=book)

            return JsonResponse({'success': True})

        except Reader.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Book not found'}, status=404)

        return JsonResponse({'success': False}, status=400)