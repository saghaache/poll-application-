from django.urls import path
from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Polls
    path('', views.poll_list, name='poll_list'),
    path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('poll/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
    path('poll/<int:poll_id>/results/', views.results, name='results'),
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),

    # Admin
    path('admin/polls/', views.admin_poll_list, name='admin_poll_list'),
    path('admin/polls/create/', views.admin_poll_create, name='admin_poll_create'),
    path('admin/polls/<int:poll_id>/edit/', views.admin_poll_edit, name='admin_poll_edit'),
    path('admin/polls/<int:poll_id>/delete/', views.admin_poll_delete, name='admin_poll_delete'),

    path('admin/polls/<int:poll_id>/options/add/', views.admin_option_create, name='admin_option_create'),
    path('admin/polls/<int:poll_id>/options/<int:option_id>/delete/', views.admin_option_delete, name='admin_option_delete'),

    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
]