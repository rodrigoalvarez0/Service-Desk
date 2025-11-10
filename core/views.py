from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q, F
from django.http import JsonResponse

from .models import (
    Ticket,
    Comment,
    KBArticle,
    KBCategory,
)
from .forms import (
    TicketForm,
    TicketUpdateForm,
    CommentForm,
)

# ---------------- HOME ----------------
def home(request):
    return render(request, 'home.html', {})

# ---------------- TICKETS ----------------
def ticket_list(request):
    tickets = Ticket.objects.order_by("-created_at")
    return render(request, "tickets/list.html", {"tickets": tickets})

def ticket_create(request):
    # --- AJAX KB suggestion endpoint ---
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        q = request.GET.get("q", "").strip()
        matches = []
        if q:
            kb_results = KBArticle.objects.filter(
                is_published=True,
                title__icontains=q
            ).values("title", "slug")[:5]
            matches = list(kb_results)
        return JsonResponse({"results": matches})

    # --- Normal form handling ---
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ticket_list")
    else:
        form = TicketForm()

    return render(request, "tickets/create.html", {"form": form})

def ticket_detail(request, pk: int):
    ticket = get_object_or_404(Ticket, pk=pk)

    # Handle new comment POST
    if request.method == "POST" and "add_comment" in request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user if request.user.is_authenticated else None
            comment.save()
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = CommentForm()

    comments = ticket.comments.all()
    return render(
        request,
        "tickets/detail.html",
        {"ticket": ticket, "comments": comments, "comment_form": form},
    )

def ticket_edit(request, pk: int):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, "tickets/edit.html", {"form": form, "ticket": ticket})

# ---------------- DASHBOARD ----------------
def dashboard(request):
    qs = Ticket.objects.all()
    total = qs.count()

    # Basic counts
    open_count = qs.exclude(status__in=['resolved', 'escalated']).count()
    resolved_count = qs.filter(status='resolved').count()
    escalated_count = qs.filter(status='escalated').count()

    # Grouped breakdowns
    by_status_qs = qs.values('status').annotate(c=Count('id')).order_by()
    by_priority_qs = qs.values('priority').annotate(c=Count('id')).order_by()

    # SLA metrics
    now = timezone.now()
    with_sla_count = qs.filter(sla_due__isnull=False).count()
    breached_count = qs.filter(sla_due__lt=now).exclude(status__in=['resolved', 'escalated']).count()
    sla_ok_count = max(with_sla_count - breached_count, 0)
    sla_rate = round((sla_ok_count / with_sla_count) * 100, 1) if with_sla_count else None

    # Labels for display
    status_labels = dict(Ticket.STATUS_CHOICES)
    priority_labels = dict(Ticket.PRIORITY_CHOICES)

    by_status = [
        {"key": row["status"], "label": status_labels.get(row["status"], row["status"]), "count": row["c"]}
        for row in by_status_qs
    ]
    by_priority = [
        {"key": row["priority"], "label": priority_labels.get(row["priority"], row["priority"]), "count": row["c"]}
        for row in by_priority_qs
    ]

    return render(
        request,
        "reports/dashboard.html",
        {
            "total": total,
            "open_count": open_count,
            "resolved_count": resolved_count,
            "escalated_count": escalated_count,
            "by_status": by_status,
            "by_priority": by_priority,
            "with_sla_count": with_sla_count,
            "breached_count": breached_count,
            "sla_rate": sla_rate,
        },
    )

# ---------------- KNOWLEDGE BASE ----------------
def kb_list(request):
    q = request.GET.get("q", "").strip()
    articles = KBArticle.objects.filter(is_published=True)
    if q:
        articles = articles.filter(Q(title__icontains=q) | Q(content__icontains=q))
    articles = articles.select_related("category").order_by("-created_at")

    categories = KBCategory.objects.all().order_by("name")
    return render(request, "kb/list.html", {"articles": articles, "categories": categories, "q": q})

def kb_detail(request, slug: str):
    article = get_object_or_404(KBArticle, slug=slug, is_published=True)
    # increment views atomically
    KBArticle.objects.filter(pk=article.pk).update(views=F("views") + 1)
    article.views += 1  # keep in-memory object in sync for this response
    return render(request, "kb/detail.html", {"article": article})
