from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    
    TRANSACTION_TYPES = [
        (EXPENSE, 'Expense'),
        (INCOME, 'Income'),
    ]
    
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default=EXPENSE
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"

class Transaction(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    
    TRANSACTION_TYPES = [
        (EXPENSE, 'Expense'),
        (INCOME, 'Income'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: ${self.amount} - {self.category.name}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name}: ${self.amount} ({self.month}/{self.year})"
    
    def get_spent_amount(self):
        """Calculate total spent in this budget's category for the month/year"""
        from django.db.models import Sum
        
        spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type=Transaction.EXPENSE,
            date__month=self.month,
            date__year=self.year
        ).aggregate(total=Sum('amount'))['total']
        
        return spent or Decimal('0.00')
    
    def get_remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.amount - self.get_spent_amount()
    
    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        spent = self.get_spent_amount()
        if self.amount > 0:
            return (spent / self.amount) * 100
        return 0
    
    def is_over_budget(self):
        """Check if spending exceeds budget"""
        return self.get_spent_amount() > self.amount
    
    # Removed duplicate spent and percentage_spent properties
    # Use get_spent_amount() and get_percentage_used() methods instead


class Goal(models.Model):
    # Remove the GOAL_TYPES and goal_type field entirely
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    # goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)  # DELETE THIS LINE
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    target_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.target_amount}"
    
    def get_progress_percentage(self):
        """Calculate progress percentage towards goal"""
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0
    
    def get_remaining_amount(self):
        """Calculate remaining amount to reach goal"""
        return max(self.target_amount - self.current_amount, Decimal('0.00'))