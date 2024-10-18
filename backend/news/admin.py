from django.contrib import admin
from .models import NewsOutlet

# Register your models here.

@admin.register(NewsOutlet)
class NewsOutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    fields = ('name', 'url', 'icon')
