"""
Forms for the jobs app.
"""
from django import forms
from django.utils import timezone
from .models import Job, Category


class JobForm(forms.ModelForm):
    """Form for creating and editing job postings."""
    
    # Custom widget for deadline date
    deadline_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }
        ),
        help_text="Leave blank if no deadline"
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'company_logo', 'category',
            'location', 'job_type', 'salary_range',
            'description', 'requirements',
            'application_link', 'application_email',
            'status', 'is_active', 'deadline_date'
        ]
        
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'e.g., Senior Software Engineer'
                }
            ),
            'company_name': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'e.g., Acme Inc.'
                }
            ),
            'company_logo': forms.FileInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'e.g., San Francisco, CA or Remote'
                }
            ),
            'job_type': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'salary_range': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'e.g., $80k - $120k'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'rows': 6,
                    'placeholder': 'Describe the role, responsibilities, and what you\'re looking for...'
                }
            ),
            'requirements': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'rows': 4,
                    'placeholder': 'List required skills, experience, and qualifications...'
                }
            ),
            'application_link': forms.URLInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'https://...'
                }
            ),
            'application_email': forms.EmailInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'jobs@company.com'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
                }
            ),
        }
        
        help_texts = {
            'application_link': 'External URL where candidates can apply',
            'application_email': 'Email address for receiving applications (alternative to link)',
            'is_active': 'Uncheck to hide this job from listings',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category queryset ordered
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = "Select a category"
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        application_link = cleaned_data.get('application_link')
        application_email = cleaned_data.get('application_email')
        deadline_date = cleaned_data.get('deadline_date')
        
        # Ensure at least one application method is provided
        if not application_link and not application_email:
            raise forms.ValidationError(
                "Please provide either an application link or an application email."
            )
        
        # Validate deadline is not in the past
        if deadline_date and deadline_date < timezone.now().date():
            raise forms.ValidationError(
                {"deadline_date": "Deadline cannot be in the past."}
            )
        
        return cleaned_data


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs."""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Job title, keywords, or company'
            }
        )
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'City, state, or zip code'
            }
        )
    )
    
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }
        )
    )
    
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all().order_by('name'),
        empty_label="All Categories",
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }
        )
    )


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'color']
        
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'rows': 3
                }
            ),
            'icon': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'e.g., 💻 or fa-laptop-code'
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'type': 'color',
                    'class': 'w-full h-10 px-2 border border-gray-300 rounded-lg'
                }
            ),
        }
