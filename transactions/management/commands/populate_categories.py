from django.core.management.base import BaseCommand
from transactions.models import Category

class Command(BaseCommand):
    help = 'Populate the database with common expense and income categories'
    
    def handle(self, *args, **options):
        # Common expense categories
        expense_categories = [
            'Groceries',
            'Transportation',
            'Entertainment',
            'Utilities',
            'Rent/Mortgage',
            'Healthcare',
            'Dining Out',
            'Shopping',
            'Insurance',
            'Education',
            'Travel',
            'Subscriptions',
            'Phone',
            'Internet',
            'Gas',
            'Parking',
            'Gym/Fitness',
            'Personal Care',
            'Pet Expenses',
            'Gifts',
            'Charity',
            'Miscellaneous'
        ]
        
        # Common income categories
        income_categories = [
            'Salary',
            'Freelance',
            'Business Income',
            'Investment Returns',
            'Rental Income',
            'Side Hustle',
            'Bonus',
            'Tax Refund',
            'Cash Gifts',
            'Dividends',
            'Interest',
            'Other Income'
        ]
        
        # Create expense categories
        for category_name in expense_categories:
            category, created = Category.objects.get_or_create(
                name=category_name,
                transaction_type=Category.EXPENSE
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created expense category: {category_name}')
                )
            else:
                self.stdout.write(f'Expense category already exists: {category_name}')
        
        # Create income categories
        for category_name in income_categories:
            category, created = Category.objects.get_or_create(
                name=category_name,
                transaction_type=Category.INCOME
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created income category: {category_name}')
                )
            else:
                self.stdout.write(f'Income category already exists: {category_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated categories!')
        )
