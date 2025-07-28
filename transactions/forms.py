from django import forms
from django.utils import timezone
from .models import Transaction, Category, Budget, Goal

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'transaction_type', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        
        # Filter categories based on transaction type if editing
        if self.instance.pk and self.instance.transaction_type:
            self.fields['category'].queryset = Category.objects.filter(
                transaction_type=self.instance.transaction_type
            )
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('transaction_type')
        
        # Validate that category matches transaction type
        if category and transaction_type:
            if category.transaction_type != transaction_type:
                raise forms.ValidationError(
                    f"Selected category '{category.name}' is for {category.get_transaction_type_display().lower()}, "
                    f"but you selected {transaction_type}."
                )
        
        return cleaned_data

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']  # Use your existing fields
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),  # Since it's a ForeignKey
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default month and year to current
        if not self.instance.pk:
            now = timezone.now()
            self.fields['month'].initial = now.month
            self.fields['year'].initial = now.year
        
        # Only show expense categories for budgets
        self.fields['category'].queryset = Category.objects.filter(
            transaction_type=Category.EXPENSE
        ).order_by('name')
        
        # Month choices
        MONTH_CHOICES = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        self.fields['month'].widget.choices = MONTH_CHOICES

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'current_amount', 'target_date', 'description']  # Added 'goal_type'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'goal_type': forms.Select(attrs={'class': 'form-control'}),  # Add this widget
            'target_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_target_date(self):
        target_date = self.cleaned_data.get('target_date')
        if target_date and target_date <= timezone.now().date():
            raise forms.ValidationError("Target date must be in the future.")
        return target_date
    
    def clean(self):
        cleaned_data = super().clean()
        target_amount = cleaned_data.get('target_amount')
        current_amount = cleaned_data.get('current_amount')
        
        if target_amount and current_amount and current_amount > target_amount:
            raise forms.ValidationError("Current amount cannot be greater than target amount.")
        
        return cleaned_data

class CategoryFilterForm(forms.Form):
    """Form for filtering transactions by category and date"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Transaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class AddToGoalForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )