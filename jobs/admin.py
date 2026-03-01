"""
Admin configuration for the jobs app.
"""
from django.contrib import admin
from .models import Job, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ('name', 'slug', 'job_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def job_count(self, obj):
        """Return the number of jobs in this category."""
        return obj.jobs.count()
    job_count.short_description = 'Jobs'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin configuration for Job model."""
    list_display = (
        'title', 'company_name', 'location', 'job_type', 
        'category', 'status', 'posted_date', 'deadline_date', 'is_active'
    )
    list_filter = (
        'job_type', 'status', 'category', 'is_active', 
        'posted_date', 'location'
    )
    search_fields = (
        'title', 'company_name', 'location', 'description', 'requirements'
    )
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_date'
    ordering = ('-posted_date',)
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'slug', 'company_name', 'company_logo', 'category')
        }),
        ('Location & Type', {
            'fields': ('location', 'job_type', 'salary_range')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements')
        }),
        ('Application', {
            'fields': ('application_link', 'application_email')
        }),
        ('Status & Dates', {
            'fields': ('status', 'is_active', 'posted_date', 'deadline_date')
        }),
    )
    
    readonly_fields = ('posted_date',)
    
    actions = ['make_published', 'make_draft', 'activate_jobs', 'deactivate_jobs']
    
    def make_published(self, request, queryset):
        """Mark selected jobs as published."""
        queryset.update(status='published')
    make_published.short_description = "Mark selected jobs as published"
    
    def make_draft(self, request, queryset):
        """Mark selected jobs as draft."""
        queryset.update(status='draft')
    make_draft.short_description = "Mark selected jobs as draft"
    
    def activate_jobs(self, request, queryset):
        """Activate selected jobs."""
        queryset.update(is_active=True)
    activate_jobs.short_description = "Activate selected jobs"
    
    def deactivate_jobs(self, request, queryset):
        """Deactivate selected jobs."""
        queryset.update(is_active=False)
    deactivate_jobs.short_description = "Deactivate selected jobs"
