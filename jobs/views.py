"""
Views for the jobs app.

Uses Class-Based Views for clean, maintainable code.
"""
from datetime import timezone

from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Job, Category
from .forms import JobForm, JobSearchForm, CategoryForm


class JobListView(ListView):
    """
    List view for job postings with search and filter functionality.
    
    Features:
    - Pagination (12 jobs per page)
    - Search by keyword, location
    - Filter by job_type and category
    - AJAX support for real-time filtering
    - Caching for better performance
    """
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter jobs based on search parameters."""
        queryset = Job.objects.filter(
            is_active=True,
            status='published'
        ).select_related('category').prefetch_related('category')
        
        # Get search parameters
        form = JobSearchForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
            
            # Keyword search (title, company, description)
            if data.get('q'):
                q = data['q']
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(company_name__icontains=q) |
                    Q(description__icontains=q)
                )
            
            # Location filter
            if data.get('location'):
                queryset = queryset.filter(
                    location__icontains=data['location']
                )
            
            # Job type filter - handle multiple selections
            job_type_param = self.request.GET.getlist('job_type')
            if job_type_param:
                queryset = queryset.filter(job_type__in=job_type_param)
            elif data.get('job_type'):
                queryset = queryset.filter(job_type=data['job_type'])
            
            # Category filter - handle multiple selections
            category_param = self.request.GET.getlist('category')
            if category_param:
                queryset = queryset.filter(category__slug__in=category_param)
            elif data.get('category'):
                queryset = queryset.filter(category=data['category'])
            
            # Salary range filter
            salary_range = self.request.GET.get('salary_range')
            if salary_range:
                # This is a simplified implementation
                # In production, you'd want a more sophisticated salary parsing
                if salary_range == '0-50k':
                    queryset = queryset.filter(salary_range__icontains='k')
                elif salary_range == '50k-100k':
                    queryset = queryset.filter(salary_range__icontains='k')
                elif salary_range == '100k-plus':
                    queryset = queryset.filter(salary_range__icontains='k')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        """Add search form and filter data to context."""
        context = super().get_context_data(**kwargs)
        
        # Search form with current values
        context['search_form'] = JobSearchForm(self.request.GET or None)
        
        # Job type choices for sidebar filter
        context['job_types'] = Job.JOB_TYPE_CHOICES
        
        # Categories for sidebar filter
        context['categories'] = Category.objects.all().order_by('name')
        
        # Current filters for maintaining state - handle multiple selections
        current_filters = {
            'q': self.request.GET.get('q', ''),
            'location': self.request.GET.get('location', ''),
            'job_type': self.request.GET.getlist('job_type'),
            'category': self.request.GET.getlist('category'),
            'salary_range': self.request.GET.get('salary_range', ''),
        }
        context['current_filters'] = current_filters
        
        # Job counts by type (cached for performance)
        cache_key = 'job_type_counts'
        job_type_counts = cache.get(cache_key)
        if not job_type_counts:
            job_type_counts = {
                job_type[0]: Job.objects.filter(
                    is_active=True, 
                    status='published',
                    job_type=job_type[0]
                ).count()
                for job_type in Job.JOB_TYPE_CHOICES
            }
            cache.set(cache_key, job_type_counts, 300)  # Cache for 5 minutes
        
        context['job_type_counts'] = job_type_counts
        
        # Job counts by category (cached)
        cache_key = 'category_counts'
        category_counts = cache.get(cache_key)
        if not category_counts:
            category_counts = {}
            for cat in context['categories']:
                category_counts[cat.slug] = Job.objects.filter(
                    is_active=True,
                    status='published',
                    category=cat
                ).count()
            cache.set(cache_key, category_counts, 300)
        
        context['category_counts'] = category_counts
        
        # Total active jobs count
        context['total_jobs'] = Job.objects.filter(
            is_active=True, 
            status='published'
        ).count()
        
        # Check if this is an AJAX request
        context['is_ajax'] = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """Handle AJAX requests for filtered results."""
        if context.get('is_ajax'):
            html = render(self.request, 'jobs/includes/job_list_items.html', context).content
            return JsonResponse({
                'html': html.decode('utf-8'),
                'count': context['paginator'].count if context.get('paginator') else 0,
                'start_index': context['page_obj'].start_index() if context.get('page_obj') else 0,
                'end_index': context['page_obj'].end_index() if context.get('page_obj') else 0,
            })
        return super().render_to_response(context, **response_kwargs)


class JobDetailView(DetailView):
    """
    Detail view for individual job postings.
    
    Increments view count on each visit.
    """
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show active, published jobs."""
        return Job.objects.filter(
            is_active=True,
            status='published'
        ).select_related('category')
    
    def get_object(self, queryset=None):
        """Get job and increment view count."""
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        """Add related jobs to context."""
        context = super().get_context_data(**kwargs)
        
        # Get related jobs (same category or similar type)
        job = self.object
        related_jobs = Job.objects.filter(
            is_active=True,
            status='published'
        ).exclude(
            id=job.id
        ).filter(
            Q(category=job.category) |
            Q(job_type=job.job_type)
        ).select_related('category')[:4]
        
        context['related_jobs'] = related_jobs
        
        # Schema markup for SEO
        context['schema_markup'] = self.get_schema_markup(job)
        
        return context
    
    def get_schema_markup(self, job):
        """Generate JSON-LD schema markup for job posting."""
        return {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": job.title,
            "description": job.description,
            "datePosted": job.posted_date.isoformat(),
            "validThrough": job.deadline_date.isoformat() if job.deadline_date else None,
            "employmentType": job.job_type.replace('_', '').upper(),
            "hiringOrganization": {
                "@type": "Organization",
                "name": job.company_name,
                "logo": job.company_logo.url if job.company_logo else None
            },
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": job.location
                }
            }
        }


class JobCategoryListView(JobListView):
    """
    List view filtered by category.
    """
    
    def get_queryset(self):
        """Filter jobs by category slug."""
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add category to context."""
        context = super().get_context_data(**kwargs)
        context['current_category'] = getattr(self, 'category', None)
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    """
    Create view for new job postings.
    
    Requires user to be logged in.
    """
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:dashboard')
    
    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(
            self.request, 
            f'Job "{form.instance.title}" has been created successfully!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(
            self.request,
            'Please correct the errors below.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add form title and action to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Post a New Job'
        context['form_action'] = 'Create Job'
        return context


class JobUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update view for existing job postings.
    
    Requires user to be logged in.
    """
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    slug_url_kwarg = 'slug'
    
    def get_success_url(self):
        """Redirect to job detail page after update."""
        return self.object.get_absolute_url()
    
    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(
            self.request,
            f'Job "{form.instance.title}" has been updated successfully!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(
            self.request,
            'Please correct the errors below.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add form title and action to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Job'
        context['form_action'] = 'Update Job'
        return context


class JobDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete view for job postings.
    
    Requires user to be logged in.
    """
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('jobs:dashboard')
    
    def delete(self, request, *args, **kwargs):
        """Handle job deletion with success message."""
        job = self.get_object()
        messages.success(
            request,
            f'Job "{job.title}" has been deleted successfully!'
        )
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for managing job postings.
    
    Shows all jobs with management options.
    """
    template_name = 'jobs/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add job statistics and lists to context."""
        context = super().get_context_data(**kwargs)
        
        # All jobs ordered by posted date
        all_jobs = Job.objects.all().order_by('-posted_date')
        
        # Statistics with annotations
        context['stats'] = {
            'total': all_jobs.count(),
            'published': all_jobs.filter(status='published').count(),
            'draft': all_jobs.filter(status='draft').count(),
            'closed': all_jobs.filter(status='closed').count(),
            'active': all_jobs.filter(is_active=True).count(),
            'expiring_soon': all_jobs.filter(
                deadline_date__lte=timezone.now() + timezone.timedelta(days=7),
                deadline_date__gte=timezone.now(),
                status='published'
            ).count(),
        }
        
        # Paginated job list
        paginator = Paginator(all_jobs, 10)
        page_number = self.request.GET.get('page')
        context['jobs'] = paginator.get_page(page_number)
        
        # Recent jobs (last 5)
        context['recent_jobs'] = all_jobs[:5]
        
        # Chart data for analytics
        context['chart_data'] = self.get_chart_data()
        
        return context
    
    def get_chart_data(self):
        """Get data for dashboard charts."""
        # Jobs by type
        jobs_by_type = []
        for code, label in Job.JOB_TYPE_CHOICES:
            count = Job.objects.filter(job_type=code).count()
            if count > 0:
                jobs_by_type.append({
                    'label': label,
                    'count': count
                })
        
        # Jobs by month (last 6 months)
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        jobs_by_month = []
        for i in range(5, -1, -1):
            month = timezone.now() - timedelta(days=30*i)
            count = Job.objects.filter(
                posted_date__month=month.month,
                posted_date__year=month.year
            ).count()
            jobs_by_month.append({
                'month': month.strftime('%b %Y'),
                'count': count
            })
        
        return {
            'by_type': json.dumps(jobs_by_type),
            'by_month': json.dumps(jobs_by_month)
        }


class HomeView(TemplateView):
    """
    Home page view with featured jobs and search.
    """
    template_name = 'jobs/home.html'
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add featured content to context."""
        context = super().get_context_data(**kwargs)
        
        # Search form
        context['search_form'] = JobSearchForm()
        
        # Featured jobs (latest 6 published jobs)
        featured_jobs = Job.objects.filter(
            is_active=True,
            status='published'
        ).select_related('category').prefetch_related('category')[:6]
        context['featured_jobs'] = featured_jobs
        
        # Categories with job counts (cached)
        cache_key = 'home_categories'
        categories_data = cache.get(cache_key)
        if not categories_data:
            categories = Category.objects.all().order_by('name')
            categories_data = []
            for cat in categories:
                job_count = Job.objects.filter(
                    category=cat,
                    is_active=True,
                    status='published'
                ).count()
                if job_count > 0 or not cat.name.startswith('_'):  # Show all categories
                    categories_data.append({
                        'category': cat,
                        'job_count': job_count
                    })
            cache.set(cache_key, categories_data, 3600)  # Cache for 1 hour
        
        context['categories'] = categories_data
        
        # Job type counts
        job_type_counts = {}
        for code, label in Job.JOB_TYPE_CHOICES:
            count = Job.objects.filter(
                is_active=True,
                status='published',
                job_type=code
            ).count()
            job_type_counts[code] = count
        
        context['job_type_counts'] = job_type_counts
        context['job_types'] = Job.JOB_TYPE_CHOICES
        
        # Total jobs
        context['total_jobs'] = Job.objects.filter(
            is_active=True,
            status='published'
        ).count()
        
        # Recent companies (unique companies with jobs)
        context['companies'] = Job.objects.filter(
            is_active=True,
            status='published'
        ).values('company_name', 'company_logo').distinct()[:8]
        
        # Popular locations (simplified)
        context['popular_locations'] = [
            {'name': 'Remote', 'count': Job.objects.filter(location__icontains='remote').count()},
            {'name': 'New York', 'count': Job.objects.filter(location__icontains='new york').count()},
            {'name': 'San Francisco', 'count': Job.objects.filter(location__icontains='san francisco').count()},
            {'name': 'London', 'count': Job.objects.filter(location__icontains='london').count()},
        ]
        
        return context


# API endpoints for modern features

@require_GET
def job_search_suggestions(request):
    """
    AJAX endpoint for job search autocomplete suggestions.
    
    Returns JSON with matching job titles and companies.
    """
    query = request.GET.get('q', '').strip()
    suggestions = {'titles': [], 'companies': [], 'locations': []}
    
    if query and len(query) >= 2:
        # Search in titles (cached)
        cache_key = f'suggestions_titles_{query}'
        titles = cache.get(cache_key)
        if not titles:
            titles = list(Job.objects.filter(
                title__icontains=query,
                is_active=True,
                status='published'
            ).values_list('title', flat=True).distinct()[:5])
            cache.set(cache_key, titles, 300)
        suggestions['titles'] = titles
        
        # Search in companies (cached)
        cache_key = f'suggestions_companies_{query}'
        companies = cache.get(cache_key)
        if not companies:
            companies = list(Job.objects.filter(
                company_name__icontains=query,
                is_active=True,
                status='published'
            ).values_list('company_name', flat=True).distinct()[:5])
            cache.set(cache_key, companies, 300)
        suggestions['companies'] = companies
        
        # Search in locations (cached)
        cache_key = f'suggestions_locations_{query}'
        locations = cache.get(cache_key)
        if not locations:
            locations = list(Job.objects.filter(
                location__icontains=query,
                is_active=True,
                status='published'
            ).values_list('location', flat=True).distinct()[:5])
            cache.set(cache_key, locations, 300)
        suggestions['locations'] = locations
    
    return JsonResponse(suggestions)


@require_GET
def get_job_counts(request):
    """
    API endpoint to get job counts for real-time updates.
    """
    counts = {
        'total': Job.objects.filter(is_active=True, status='published').count(),
        'by_type': {},
        'by_category': {}
    }
    
    # Counts by type
    for code, label in Job.JOB_TYPE_CHOICES:
        counts['by_type'][code] = Job.objects.filter(
            is_active=True, status='published', job_type=code
        ).count()
    
    # Counts by category
    for cat in Category.objects.all():
        counts['by_category'][cat.slug] = Job.objects.filter(
            is_active=True, status='published', category=cat
        ).count()
    
    return JsonResponse(counts)


@require_GET
def advanced_search(request):
    """
    Advanced search API endpoint.
    """
    jobs = Job.objects.filter(is_active=True, status='published')
    
    # Apply all filters
    if request.GET.get('q'):
        q = request.GET['q']
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(company_name__icontains=q) |
            Q(description__icontains=q)
        )
    
    if request.GET.get('location'):
        jobs = jobs.filter(location__icontains=request.GET['location'])
    
    if request.GET.getlist('job_type'):
        jobs = jobs.filter(job_type__in=request.GET.getlist('job_type'))
    
    if request.GET.getlist('category'):
        jobs = jobs.filter(category__slug__in=request.GET.getlist('category'))
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    start = (page - 1) * per_page
    end = start + per_page
    
    jobs_list = jobs[start:end]
    
    data = {
        'jobs': [
            {
                'id': job.id,
                'title': job.title,
                'company': job.company_name,
                'location': job.location,
                'job_type': job.get_job_type_display(),
                'salary_range': job.salary_range,
                'posted_date': job.posted_date.isoformat(),
                'url': job.get_absolute_url(),
                'logo': job.company_logo.url if job.company_logo else None,
            }
            for job in jobs_list
        ],
        'total': jobs.count(),
        'page': page,
        'pages': (jobs.count() + per_page - 1) // per_page,
    }
    
    return JsonResponse(data)