from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Ticket, Comment

class Command(BaseCommand):
    help = "Check for SLA breaches and auto-escalate tickets."

    def handle(self, *args, **options):
        now = timezone.now()
        breached = Ticket.objects.filter(
            sla_due__lt=now, status__in=['new', 'in_progress', 'waiting']
        )
        count = 0
        for ticket in breached:
            ticket.status = 'escalated'
            ticket.save()
            Comment.objects.create(
                ticket=ticket,
                body=f"⚠️ Ticket auto-escalated due to SLA breach at {now:%Y-%m-%d %H:%M}",
                is_internal=True,
            )
            count += 1
            self.stdout.write(self.style.WARNING(f"Escalated ticket #{ticket.id}"))
        self.stdout.write(self.style.SUCCESS(f"Done. Escalated {count} ticket(s)."))
