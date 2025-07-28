from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:transaction_id>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),
    
  # Budget URLs
    path('budgets/', views.budget_list, name='budgets'),
    path('budgets/create/', views.create_budget, name='create_budget'),
    path('budgets/<int:pk>/edit/', views.edit_budget, name='edit_budget'),
    path('budgets/<int:pk>/delete/', views.delete_budget, name='delete_budget'),
    
    # Goal URLs
    path('goals/', views.goal_list, name='goals'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:pk>/add/', views.add_to_goal, name='add_to_goal'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),
    
    # Reports URL
    path('reports/', views.reports, name='reports'),
]