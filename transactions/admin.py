from django.contrib import admin
from .models import Category, Transaction, Budget, Goal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'transaction_type', 'date', 'created_at']
    list_filter = ['transaction_type', 'category', 'date', 'created_at']
    search_fields = ['description', 'user__username', 'category__name']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'year', 'get_spent_display', 'get_remaining_display']
    list_filter = ['year', 'month', 'category']
    search_fields = ['user__username', 'category__name']
    ordering = ['-year', '-month']
    
    def get_spent_display(self, obj):
        return f"${obj.get_spent_amount():.2f}"
    get_spent_display.short_description = 'Spent'
    
    def get_remaining_display(self, obj):
        remaining = obj.get_remaining_amount()
        if remaining < 0:
            return f"-${abs(remaining):.2f}"
        return f"${remaining:.2f}"
    get_remaining_display.short_description = 'Remaining'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

@admin.register(Goal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'current_amount', 'get_progress_display', 'target_date', 'is_completed']
    list_filter = ['is_completed', 'target_date']
    search_fields = ['name', 'user__username']
    ordering = ['-created_at']
    
    def get_progress_display(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress_display.short_description = 'Progress'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
