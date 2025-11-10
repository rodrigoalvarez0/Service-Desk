from django.contrib import admin
from .models import Ticket, Comment, KBCategory, KBArticle

admin.site.site_header = "Ticketing System By: Rodrigo Alvarez"
admin.site.site_title = "Ticketing System By: Rodrigo Alvarez"
admin.site.index_title = "Welcome to the Ticketing System"

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description', 'requester_email')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal',)
    search_fields = ('body',)

@admin.register(KBCategory)
class KBCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(KBArticle)
class KBArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'views', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
