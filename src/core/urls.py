from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('import/', views.import_file, name='import_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('', views.home, name='home'),
    path('reports/', views.reports, name='reports'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
]
