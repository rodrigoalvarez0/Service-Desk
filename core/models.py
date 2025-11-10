from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

# ---------------- TICKETS ----------------
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting on User'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    requester_email = models.EmailField(blank=True, null=True)
    sla_due = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set SLA deadline based on priority if not set
        if not self.sla_due:
            hours = {'low': 72, 'medium': 48, 'high': 24, 'urgent': 8}.get(self.priority, 24)
            self.sla_due = timezone.now() + timedelta(hours=hours)
        super().save(*args, **kwargs)

    def is_sla_breached(self):
        # Return False gracefully if sla_due hasn't been set (older tickets)
        if not self.sla_due:
            return False
        return self.status not in ['resolved', 'escalated'] and timezone.now() > self.sla_due

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Comment(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        who = self.author.username if self.author else "Anonymous"
        return f"Comment by {who} on ticket #{self.ticket_id}"


# ---------------- KNOWLEDGE BASE ----------------
class KBCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "KB categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class KBArticle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(KBCategory, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            candidate = base
            n = 1
            while KBArticle.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                n += 1
                candidate = f"{base}-{n}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
