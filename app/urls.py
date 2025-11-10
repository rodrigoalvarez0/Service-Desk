# app/urls.py
from django.contrib import admin
from django.urls import path
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', core_views.home, name='home'),

    # Tickets
    path('tickets/', core_views.ticket_list, name='ticket_list'),
    path('tickets/new/', core_views.ticket_create, name='ticket_create'),
    path('tickets/create/', core_views.ticket_create),  # <-- alias so /tickets/create/ works
    path('tickets/<int:pk>/', core_views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/edit/', core_views.ticket_edit, name='ticket_edit'),

    # Dashboard
    path('dashboard/', core_views.dashboard, name='dashboard'),

    # Knowledge Base
    path('kb/', core_views.kb_list, name='kb_list'),
    path('kb/<slug:slug>/', core_views.kb_detail, name='kb_detail'),
]
