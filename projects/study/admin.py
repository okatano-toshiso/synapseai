from django.contrib import admin
from .models import Card, Progress, ReviewLog

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("front", "chapter", "topic", "category", "is_active")
    list_filter = ("chapter", "category", "topic", "is_active")
    search_fields = ("front", "back", "trap")

admin.site.register(Progress)
admin.site.register(ReviewLog)
