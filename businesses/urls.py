from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.business_list, name='list'),
    path('<int:pk>/', views.business_detail, name='detail'),
    path('add/', views.business_create, name='create'),
    path('<int:pk>/edit/', views.business_edit, name='edit'),
    path('<int:pk>/delete/', views.business_delete, name='delete'),
]
