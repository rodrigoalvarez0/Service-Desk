# Service Desk

A lightweight Django-based service desk prototype for tracking tickets, internal comments, a Knowledge Base (KB), and SLA monitoring.

## Summary
This project provides:
- Ticket creation, status/priority management and comments (including internal notes).
- Knowledge Base with search and view counts.
- SLA auto-deadline calculation and a CLI command to detect/escalate breached SLAs.
- Simple dashboard and admin integration.

## Features
- Tickets: create, list, view, edit.
- Comments: public and internal agent-only notes.
- Knowledge Base: categories, articles and search.
- SLA handling: per-priority deadlines and check_sla management command.
- Dashboard: aggregated metrics and SLA overview.

## Quick start (development)
1. Fork and Clone the Repository to your desired directory:
   git clone https://github.com/YOUR-USERNAME/service-desk.git
   cd service-desk
3. Create and activate a virtual environment:
   python -m venv .venv
   .venv\Scripts\Activate
4. Install dependencies:
   pip install -r requirements.txt
5. Apply migrations and create a superuser:
   python manage.py migrate
   python manage.py createsuperuser
6. Run the development server:
   python manage.py runserver

The admin site is available at: http://127.0.0.1:8000/admin/

## Running tests
Run the test suite:
python manage.py test

## Useful management commands
- Check SLA and mark/escalate breached tickets:
  python manage.py check_sla

## Configuration
- Settings are in app/settings.py.
- Default development DB: SQLite (db.sqlite3).

## Solo project / contributions
This is a solo project. If you fork or contribute, please:
- Keep commits focused and descriptive.
- Add tests for new behavior.
- Update migrations when altering models.



