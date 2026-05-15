from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('accessibility/', views.accessibility_statement, name='accessibility_statement'),
    path('blog/', views.blog, name='blog'),
    path('blog/posts-tab/', views.blog_posts_tab, name='blog_posts_tab'),
    path('blog/add/', views.blog_create, name='blog_create'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/like/', views.blog_like_toggle, name='blog_like_toggle'),
    path('blog/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('blog/<slug:slug>/hide/', views.blog_hide_post, name='blog_hide_post'),
    path('blog/<slug:slug>/report/', views.blog_report_post, name='blog_report_post'),
    path('blog/comment/<int:pk>/like/', views.blog_comment_like_toggle, name='blog_comment_like_toggle'),
    path('blog/comment/<int:pk>/delete/', views.blog_comment_delete, name='blog_comment_delete'),
]
