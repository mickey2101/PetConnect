# animals/admin.py
from django.contrib import admin
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'gender', 'status')
    list_filter = ('species', 'status', 'good_with_kids', 'good_with_cats', 'good_with_dogs')
    search_fields = ('name', 'breed', 'description')