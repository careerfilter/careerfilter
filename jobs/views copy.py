"""
Views for the jobs app.

Uses Class-Based Views for clean, maintainable code.
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.core.paginator import Paginator

from .models import Job, Category
from .forms import JobForm, JobSearchForm, CategoryForm


class JobListView(ListView):
    """
    List view for job postings with search and filter functionality.
    
    Features:
    - Pagination (12 jobs per page)
    - Search by keyword, location
    - Filter by job_type and category
    - Only shows active, published jobs
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
        ).select_related('category')
        
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
            
            # Job type filter
            if data.get('job_type'):
                queryset = queryset.filter(job_type=data['job_type'])
            
            # Category filter
            if data.get('category'):
                queryset = queryset.filter(category=data['category'])
        
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
        
        # Current filters for maintaining state
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'location': self.request.GET.get('location', ''),
            'job_type': self.request.GET.get('job_type', ''),
            'category': self.request.GET.get('category', ''),
        }
        
        # Job counts by type
        context['job_type_counts'] = {
            job_type[0]: Job.objects.filter(
                is_active=True, 
                status='published',
                job_type=job_type[0]
            ).count()
            for job_type in Job.JOB_TYPE_CHOICES
        }
        
        # Job counts by category
        context['category_counts'] = {
            cat.id: Job.objects.filter(
                is_active=True,
                status='published',
                category=cat
            ).count()
            for cat in context['categories']
        }
        
        # Total active jobs count
        context['total_jobs'] = Job.objects.filter(
            is_active=True, 
            status='published'
        ).count()
        
        return context


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
        )[:4]
        
        context['related_jobs'] = related_jobs
        
        return context


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
        
        # Statistics
        context['stats'] = {
            'total': all_jobs.count(),
            'published': all_jobs.filter(status='published').count(),
            'draft': all_jobs.filter(status='draft').count(),
            'closed': all_jobs.filter(status='closed').count(),
            'active': all_jobs.filter(is_active=True).count(),
        }
        
        # Paginated job list
        paginator = Paginator(all_jobs, 10)
        page_number = self.request.GET.get('page')
        context['jobs'] = paginator.get_page(page_number)
        
        # Recent jobs (last 5)
        context['recent_jobs'] = all_jobs[:5]
        
        return context


class HomeView(TemplateView):
    """
    Home page view with featured jobs and search.
    """
    template_name = 'jobs/home.html'
    
    def get_context_data(self, **kwargs):
        """Add featured content to context."""
        context = super().get_context_data(**kwargs)
        
        # Search form
        context['search_form'] = JobSearchForm()
        
        # Featured jobs (latest 6 published jobs)
        context['featured_jobs'] = Job.objects.filter(
            is_active=True,
            status='published'
        ).select_related('category')[:6]
        
        # Categories with job counts
        categories = Category.objects.all().order_by('name')
        context['categories'] = [
            {
                'category': cat,
                'job_count': Job.objects.filter(
                    category=cat,
                    is_active=True,
                    status='published'
                ).count()
            }
            for cat in categories
        ]
        
        # Job type counts
        context['job_type_counts'] = {
            job_type[1]: Job.objects.filter(
                is_active=True,
                status='published',
                job_type=job_type[0]
            ).count()
            for job_type in Job.JOB_TYPE_CHOICES
        }
        
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
        
        return context


# Function-based views for simpler cases

def job_search_suggestions(request):
    """
    AJAX endpoint for job search autocomplete suggestions.
    
    Returns JSON with matching job titles and companies.
    """
    from django.http import JsonResponse
    
    query = request.GET.get('q', '').strip()
    suggestions = {'titles': [], 'companies': [], 'locations': []}
    
    if query and len(query) >= 2:
        # Search in titles
        titles = Job.objects.filter(
            title__icontains=query,
            is_active=True,
            status='published'
        ).values_list('title', flat=True).distinct()[:5]
        suggestions['titles'] = list(titles)
        
        # Search in companies
        companies = Job.objects.filter(
            company_name__icontains=query,
            is_active=True,
            status='published'
        ).values_list('company_name', flat=True).distinct()[:5]
        suggestions['companies'] = list(companies)
        
        # Search in locations
        locations = Job.objects.filter(
            location__icontains=query,
            is_active=True,
            status='published'
        ).values_list('location', flat=True).distinct()[:5]
        suggestions['locations'] = list(locations)
    
    return JsonResponse(suggestions)
