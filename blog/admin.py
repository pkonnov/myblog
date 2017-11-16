from django.contrib import admin
from .models import Category, Article, Comment

class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['author', 'category', 'title',]}),
        ('Date information', {'fields': ['created_date', 'published_date',]}),
        ('Text', {'fields': ['text', 'image']}),
    ]
    list_display = ('title', 'published_date', 'was_published_recently')
    list_filter = ['published_date']
    search_fields = ['title']

admin.site.register(Category)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
