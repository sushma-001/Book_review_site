from django.contrib import admin
from .models import Reader  # Import the Reader model, not ReaderManager

# Register the Reader model with the admin site
admin.site.register(Reader)
