# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Human-Recruiter is a Django 4.2 HR management system (Spanish-language UI) covering employee management, recruitment, attendance, payroll, vacations, and access control. It uses the MVT (Model-View-Template) architecture with AdminLTE3 as the frontend framework.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (username: root, password: root)
python user_init.py

# Seed database with sample data (departments, positions, candidates, employees, etc.)
python core/erp/utils.py

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Architecture

### Django Project Structure

- **`config/`** — Project configuration: `settings.py`, `urls.py`, `db.py` (database presets for SQLite/PostgreSQL/MySQL), `wsgi.py`
- **`core/`** — All Django apps live here as sub-packages
- **`templates/`** — Global base templates (dashboard, sidebar, form, list, delete, PDF report layouts)
- **`static/`** — Source static assets; `staticfiles/` — collected static output

### Core Apps

| App | Path | Purpose |
|-----|------|---------|
| `core.erp` | Main business logic | Models for Company, Candidatos, Departments, EmployeePositions, Vacants, Selection, Employee, EmployeeTurn, Headings, Salary/SalaryDetail/SalaryHeadings, Assistance/AssistanceDetail, Vacations |
| `core.user` | Custom user model | Extends `AbstractUser` with image, token, and FK to Employee (`AUTH_USER_MODEL = 'user.User'`) |
| `core.login` | Authentication | Login, logout, password reset/change via email token |
| `core.security` | Access logging | `AccessUser` model tracks login IP/time per user |
| `core.dashboard` | Dashboard view | Aggregates salary, attendance, and entity counts; triggers vacation state transitions on page load |

### Key Patterns

- **Views are class-based** (Django generic views: `ListView`, `CreateView`, `UpdateView`, `DeleteView`, `TemplateView`, `FormView`). Each ERP entity has its own sub-directory under `core/erp/views/` (e.g., `core/erp/views/empleados/`, `core/erp/views/salary/`).
- **Permission control** uses `ValidatePermissionRequiredMixin` and `IsSuperuserMixin` in `core/erp/mixins.py`. Permissions are group-based, stored in the session via `User.get_group_session()`.
- **All models implement `toJSON()`** (sometimes `toJson()`) for AJAX-driven DataTables on the frontend. Views return JSON via `HttpResponse(json.dumps(data))` in POST handlers with an `action` dispatch pattern.
- **Email notifications** are sent via direct SMTP (not Django's email backend) for hiring notifications (`post_save` signal on `Employee`) and vacation reminders.
- **PDF generation** uses WeasyPrint (`core/print_pdf.py` and views).
- **Frontend stack**: AdminLTE3, jQuery, DataTables, Select2, SweetAlert, jQuery Confirm, daterangepicker. JS/CSS are in `core/erp/static/` per-entity and `static/`.

### URL Routing

Root `config/urls.py` delegates to:
- `/login/` → `core.login.url`
- `/erp/` → `core.erp.urls` (app_name: `erp`)
- `/user/` → `core.user.url` (app_name: `user`)
- `/security/` → `core.security.urls`
- `/dashboard/` and `/` → `DashboardView`

### Database

Default is SQLite. Database presets are in `config/db.py` (`SQLITE`, `POSTGRESQL`, `MYSQL`). Switch by changing `DATABASES = db.SQLITE` in `settings.py`.

**Note:** Migrations are git-ignored except for `__init__.py` files. You must run `makemigrations` after cloning.

### Custom User Model

`core.user.models.User` extends `AbstractUser` and has a FK to `Employee`. A user must be linked to an employee record. The `crum` library (`django-crum`) is used to access the current request/user from within models.
