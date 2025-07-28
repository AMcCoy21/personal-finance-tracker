from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout 
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Transaction, Category, Budget, Goal
from .forms import TransactionForm, BudgetForm, GoalForm
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from .models import Budget, Goal
from .forms import BudgetForm, GoalForm, AddToGoalForm
import json

def home(request):
    """Landing page - redirect to dashboard if logged in"""
    print(f"Home view called, user authenticated: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'transactions/home.html')

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            # Auto login after registration
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home') 

@login_required
def dashboard(request):
    """Main dashboard with financial overview"""
    user = request.user
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Calculate monthly totals
    monthly_income = Transaction.objects.filter(
        user=user,
        transaction_type=Transaction.INCOME,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    monthly_expenses = Transaction.objects.filter(
        user=user,
        transaction_type=Transaction.EXPENSE,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    monthly_savings = monthly_income - monthly_expenses
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:5]
    
    # Budget status
    budgets = Budget.objects.filter(user=user, month=current_month, year=current_year)
    budget_status = []
    for budget in budgets:
        spent = budget.get_spent_amount()
        remaining = budget.get_remaining_amount()
        percentage = budget.get_percentage_used()
        budget_status.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'is_over': budget.is_over_budget()
        })
    
    # Financial goals progress
    goals = Goal.objects.filter(user=user, is_completed=False).order_by('target_date')[:3]
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_savings': monthly_savings,
        'recent_transactions': recent_transactions,
        'budget_status': budget_status,
        'goals': goals,
        'current_month': current_month,
        'current_year': current_year,
    }
    
    return render(request, 'transactions/dashboard.html', context)

@login_required
def transaction_list(request):
    """List all transactions with filtering"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type in ['income', 'expense']:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'selected_category': category_id,
        'selected_type': transaction_type,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'transactions/transaction_list.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    # Add this line to pass categories to template
    categories = Category.objects.all()
    
    return render(request, 'transactions/add_transaction.html', {
        'form': form,
        'categories': categories  # Add this
    })

@login_required
def edit_transaction(request, transaction_id):
    """Edit existing transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transactions/edit_transaction.html', {
        'form': form, 
        'transaction': transaction
    })

@login_required
def delete_transaction(request, transaction_id):
    """Delete transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction.delete()
    messages.success(request, 'Transaction deleted successfully!')
    return redirect('transaction_list')

@login_required
# Budget Views
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    total_budget = budgets.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate spent budget properly
    spent_budget = 0
    for budget in budgets:
        spent_budget += budget.get_spent_amount()
    
    remaining_budget = total_budget - spent_budget
    
    context = {
        'budgets': budgets,
        'total_budget': total_budget,
        'spent_budget': spent_budget,
        'remaining_budget': remaining_budget,
    }
    return render(request, 'budgets/budget_list.html', context)

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budgets')
    else:
        form = BudgetForm()
    return render(request, 'budgets/budget_form.html', {'form': form})

def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budgets')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'budgets/budget_form.html', {'form': form})

def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully!')
    return redirect('budgets')

# Goal Views
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    completed_goals = goals.filter(current_amount__gte=F('target_amount')).count()
    active_goals = goals.filter(current_amount__lt=F('target_amount')).count()
    total_target = goals.aggregate(Sum('target_amount'))['target_amount__sum'] or 0
    
    context = {
        'goals': goals,
        'completed_goals': completed_goals,
        'active_goals': active_goals,
        'total_target': total_target,
    }
    return render(request, 'goals/goal_list.html', context)


def create_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            # Remove this line: goal.goal_type = 'savings'
            goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('goals')
    else:
        form = GoalForm()
    return render(request, 'goals/goal_form.html', {'form': form})

def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goals')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'goals/goal_form.html', {'form': form})

def add_to_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddToGoalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            goal.current_amount += amount
            goal.save()
            messages.success(request, f'Added ${amount} to {goal.name}!')
            return redirect('goals')
    else:
        form = AddToGoalForm()
    return render(request, 'goals/add_to_goal.html', {'form': form, 'goal': goal})

def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, 'Goal deleted successfully!')
    return redirect('goals')

# Reports View
def reports(request):
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')
    
    # Base queryset
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if category:
        transactions = transactions.filter(category=category)
    
    # Calculate totals - FIXED: Use transaction_type instead of type
    income_transactions = transactions.filter(transaction_type=Transaction.INCOME)
    expense_transactions = transactions.filter(transaction_type=Transaction.EXPENSE)
    
    total_income = income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expense_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    net_amount = total_income - total_expenses
    total_transactions = transactions.count()
    
    # Get categories for filter dropdown
    categories = Category.objects.all().order_by('name')
    
    # Expense categories for chart
    expense_categories = expense_transactions.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    # Income sources for chart
    income_sources = income_transactions.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    # Prepare chart data
    expense_labels = [cat['category__name'] for cat in expense_categories]
    expense_data = [float(cat['total']) for cat in expense_categories]
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_amount': net_amount,
        'total_transactions': total_transactions,
        'categories': categories,
        'expense_categories': expense_categories,
        'income_sources': income_sources,
        'expense_labels': json.dumps(expense_labels),
        'expense_data': json.dumps(expense_data),
    }
    return render(request, 'reports/reports.html', context)