"""
URL configuration for the jobs app.
"""
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Job listings
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/category/<slug:category_slug>/', views.JobCategoryListView.as_view(), name='job_list_by_category'),
    
    # Job detail
    path('jobs/<slug:slug>/', views.JobDetailView.as_view(), name='job_detail'),
    
    # Job management (requires login)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('jobs/create/', views.JobCreateView.as_view(), name='job_create'),
    path('jobs/<slug:slug>/edit/', views.JobUpdateView.as_view(), name='job_update'),
    path('jobs/<slug:slug>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    
    # AJAX endpoints
    path('api/search-suggestions/', views.job_search_suggestions, name='search_suggestions'),
]
