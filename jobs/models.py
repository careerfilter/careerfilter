"""
Models for the jobs app.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Category(models.Model):
    """Category model for job classification."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Font awesome icon class or emoji"
    )
    color = models.CharField(
        max_length=7, 
        default='#3B82F6',
        help_text="Hex color code for category"
    )
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:job_list_by_category', kwargs={'category_slug': self.slug})


class Job(models.Model):
    """Job posting model with all required fields."""
    
    # Job Type Choices
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    # Status Choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]
    
    # Primary Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(
        upload_to='company_logos/%Y/%m/',
        blank=True,
        null=True,
        help_text="Company logo image"
    )
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs'
    )
    
    # Location & Type
    location = models.CharField(
        max_length=200,
        help_text="City, State or 'Remote'"
    )
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default='full_time'
    )
    salary_range = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., $50k - $80k or 'Competitive'"
    )
    
    # Job Details
    description = models.TextField(
        help_text="Detailed job description"
    )
    requirements = models.TextField(
        blank=True,
        help_text="Job requirements and qualifications"
    )
    
    # Application
    application_link = models.URLField(
        blank=True,
        help_text="External application URL"
    )
    application_email = models.EmailField(
        blank=True,
        help_text="Email address for applications"
    )
    
    # Status & Dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the job is currently active"
    )
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateField(
        blank=True,
        null=True,
        help_text="Application deadline"
    )
    
    # Metadata
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-posted_date']
        indexes = [
            models.Index(fields=['-posted_date']),
            models.Index(fields=['job_type']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create unique slug
            base_slug = slugify(f"{self.title}-{self.company_name}")
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})
    
    def get_application_url(self):
        """Return the appropriate application URL or mailto link."""
        if self.application_link:
            return self.application_link
        elif self.application_email:
            return f"mailto:{self.application_email}"
        return None
    
    def get_time_since_posted(self):
        """Return human-readable time since posted."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.posted_date)
    
    def is_expired(self):
        """Check if the job deadline has passed."""
        if self.deadline_date:
            return self.deadline_date < timezone.now().date()
        return False
    
    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def job_type_display_class(self):
        """Return CSS class for job type badge."""
        class_map = {
            'full_time': 'bg-blue-100 text-blue-800',
            'part_time': 'bg-green-100 text-green-800',
            'contract': 'bg-yellow-100 text-yellow-800',
            'remote': 'bg-purple-100 text-purple-800',
            'internship': 'bg-pink-100 text-pink-800',
            'freelance': 'bg-orange-100 text-orange-800',
        }
        return class_map.get(self.job_type, 'bg-gray-100 text-gray-800')
