from django.contrib import admin
from .models import BlogPost, Comment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'published_at')
    list_filter = ('status', 'published_at')
    search_fields = ('title', 'text', 'owner__username')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created_at', 'active']
    list_filter = ['active', 'created_at', 'updated_at']
    search_fields = ['name', 'email', 'body']
