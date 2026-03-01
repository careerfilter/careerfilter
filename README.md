# Django Job Board

A modern, production-ready job board application built with Django, optimized for Vercel serverless deployment. Features a clean, responsive UI with Tailwind CSS and comprehensive job management capabilities.

![Django Job Board](https://img.shields.io/badge/Django-4.2+-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![Vercel](https://img.shields.io/badge/Vercel-Ready-000000?logo=vercel)

## Features

### Core Features
- **Job Listings System** - Full-featured job posting with search and filters
- **Category Management** - Organize jobs by categories (Tech, Marketing, Design, etc.)
- **Advanced Search** - Search by keyword, location, job type, and category
- **Responsive Design** - Mobile-first design with Tailwind CSS
- **User Dashboard** - Manage job postings with statistics

### Job Features
- Job types: Full-time, Part-time, Contract, Remote, Internship, Freelance
- Company logo upload support
- Salary range display
- Application deadline tracking
- Draft/Published status workflow
- View count tracking
- "Posted X days ago" formatting

### Technical Features
- Class-Based Views for clean, maintainable code
- Django Forms with validation
- PostgreSQL support via `dj-database-url`
- Whitenoise for static file serving
- Cloudinary integration for media files (optional)
- SEO-friendly URLs with slugs

## Project Structure

```
django-jobboard/
├── api/
│   └── index.py              # Vercel serverless entry point
├── core/                     # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Django settings (Vercel-optimized)
│   ├── urls.py
│   └── wsgi.py
├── jobs/                     # Main jobs application
│   ├── __init__.py
│   ├── admin.py              # Custom Django admin
│   ├── apps.py
│   ├── forms.py              # Job and search forms
│   ├── models.py             # Job and Category models
│   ├── urls.py               # URL routing
│   └── views.py              # Class-Based Views
├── templates/
│   ├── base.html             # Base template with Tailwind
│   └── jobs/
│       ├── home.html         # Homepage with hero search
│       ├── job_list.html     # Job listings with filters
│       ├── job_detail.html   # Individual job page
│       ├── job_form.html     # Create/edit job form
│       ├── job_confirm_delete.html
│       └── dashboard.html    # Management dashboard
├── static/                   # Static files (CSS, JS, images)
├── build_files.sh            # Vercel build script
├── manage.py
├── requirements.txt
├── runtime.txt               # Python version
├── vercel.json               # Vercel configuration
└── .env.example              # Environment variables template
```

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)
- PostgreSQL database (Neon/Supabase recommended for production)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-jobboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
   
   For local development, your `.env` should look like:
   ```
   SECRET_KEY=your-local-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py shell -c "
   from jobs.models import Category
   categories = [
       ('Technology', '💻', '#3B82F6'),
       ('Marketing', '📢', '#10B981'),
       ('Design', '🎨', '#8B5CF6'),
       ('Sales', '💼', '#F59E0B'),
       ('Customer Service', '🎧', '#EC4899'),
       ('Finance', '💰', '#6366F1'),
   ]
   for name, icon, color in categories:
       Category.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})
   print('Categories created!')
   "
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Website: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Vercel Deployment

### 1. Prepare Your Project

Ensure your project is ready for deployment:

```bash
# Verify all files are committed
git status

# Test local build
python manage.py collectstatic --noinput
```

### 2. Set Up PostgreSQL Database

**Option A: Neon PostgreSQL (Recommended)**
1. Go to [Neon](https://neon.tech) and create an account
2. Create a new project
3. Get your connection string from the dashboard
4. Format: `postgres://user:password@host:port/database`

**Option B: Supabase**
1. Go to [Supabase](https://supabase.com) and create an account
2. Create a new project
3. Get your connection string from Settings > Database

### 3. Deploy to Vercel

**Using Vercel CLI:**

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

**Using Vercel Dashboard:**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your Git repository
4. Configure project:
   - **Framework Preset**: Other
   - **Build Command**: `bash build_files.sh`
   - **Output Directory**: `staticfiles`
   - **Install Command**: `pip install -r requirements.txt`

### 4. Configure Environment Variables

In your Vercel project settings, add these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secure-random-key` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `.vercel.app,your-domain.com` |
| `DATABASE_URL` | PostgreSQL connection | `postgres://user:pass@host/db` |

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Run Migrations

After deployment, run migrations using Vercel CLI:

```bash
vercel --prod

# Then run migrations
vercel env pull .env.production
export $(cat .env.production | xargs)
python manage.py migrate
```

Or use a one-off command:
```bash
vercel --prod --command "python manage.py migrate"
```

### 6. Create Admin User

```bash
vercel --prod --command "python manage.py createsuperuser"
```

## Custom Domain Configuration

1. Go to your Vercel project dashboard
2. Navigate to **Settings > Domains**
3. Add your custom domain
4. Update `ALLOWED_HOSTS` environment variable:
   ```
   .vercel.app,your-domain.com,www.your-domain.com
   ```
5. Configure DNS records as instructed by Vercel

## Database Management

### Running Migrations

**Local:**
```bash
python manage.py migrate
```

**Production (Vercel):**
```bash
# Using Vercel CLI with production environment
vercel --prod --command "python manage.py migrate"
```

### Creating a Backup

**Neon:**
- Automatic backups are included
- Use Neon dashboard for point-in-time recovery

**Manual backup:**
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restoring from Backup

```bash
psql $DATABASE_URL < backup.sql
```

## Media Files Configuration

### Option 1: Cloudinary (Recommended for Production)

1. Create a [Cloudinary](https://cloudinary.com) account
2. Get your API credentials
3. Add to environment variables:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

### Option 2: Base64 Encoding (Simple, Limited)

For simple logo uploads, the app will store files in the database or use the default storage.

### Option 3: External Storage (AWS S3, etc.)

Configure Django storages backend in `settings.py`.

## Customization Guide

### Adding New Job Types

Edit `jobs/models.py`:

```python
JOB_TYPE_CHOICES = [
    ('full_time', 'Full-time'),
    ('part_time', 'Part-time'),
    # Add your new type here
    ('new_type', 'New Type'),
]
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Customizing the Theme

Colors are defined in `templates/base.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',
                    500: '#3b82f6',
                    600: '#2563eb',
                    // ...
                }
            }
        }
    }
}
```

### Adding New Pages

1. Create view in `jobs/views.py`
2. Add URL pattern in `jobs/urls.py`
3. Create template in `templates/jobs/`

## API Endpoints

The following endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/jobs/` | GET | Job listings with search |
| `/jobs/<slug>/` | GET | Job detail page |
| `/jobs/create/` | GET/POST | Create new job |
| `/jobs/<slug>/edit/` | GET/POST | Edit job |
| `/jobs/<slug>/delete/` | GET/POST | Delete job |
| `/dashboard/` | GET | Management dashboard |
| `/admin/` | GET | Django admin |
| `/api/search-suggestions/` | GET | AJAX search suggestions |

## Troubleshooting

### Static Files Not Loading

1. Check `STATIC_ROOT` is set correctly
2. Run `python manage.py collectstatic`
3. Verify Whitenoise is in `MIDDLEWARE`

### Database Connection Issues

1. Verify `DATABASE_URL` format
2. Check database is accessible from Vercel IPs
3. Ensure SSL mode is configured for PostgreSQL

### Migration Errors

```bash
# Reset migrations (careful - data loss!)
python manage.py migrate jobs zero
python manage.py makemigrations jobs
python manage.py migrate
```

### 500 Errors on Vercel

1. Check Vercel function logs
2. Verify all environment variables are set
3. Ensure `DEBUG=False` in production

## Security Considerations

- Keep `SECRET_KEY` secret and unique per environment
- Set `DEBUG=False` in production
- Use HTTPS (automatic on Vercel)
- Regularly update dependencies
- Enable Django security middleware

## Performance Optimization

- Static files served via Whitenoise with compression
- Database queries optimized with `select_related`
- Pagination for job listings (12 per page)
- Database indexes on frequently queried fields

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check Django documentation: https://docs.djangoproject.com/
- Vercel documentation: https://vercel.com/docs

---

Built with ❤️ using Django and Tailwind CSS
