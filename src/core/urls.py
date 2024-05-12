from django.urls import path
from .views import home_view, graph_view, files_view, notif_view

app_name = 'core'

urlpatterns = [
    path('', home_view, name='home'),
    path('graph/', graph_view, name='graph'),
    path('files/', files_view, name='files'),
    path('notifications/', notif_view, name='notifications'),
]
