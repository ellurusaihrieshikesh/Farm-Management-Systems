from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Additional user details stored separately from auth User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Farm(models.Model):
    """Farm model for managing farm information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    farm_name = models.CharField(max_length=200)
    location = models.TextField()
    crop_type = models.CharField(max_length=200)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in acres or hectares")
    area_unit = models.CharField(max_length=20, choices=[('acres', 'Acres'), ('hectares', 'Hectares')], default='acres')
    start_date = models.DateField()
    end_date = models.TextField(help_text="Expected harvest or end date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.farm_name} - {self.crop_type}"


class TodoList(models.Model):
    """TodoList model for farm tasks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='todos')
    task = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=20, 
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], 
        default='medium'
    )
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['completed', '-priority', 'due_date']
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.task}"


class Expense(models.Model):
    """Expense model for tracking farm expenses"""
    EXPENSE_CATEGORIES = [
        ('seeds', 'Seeds'),
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('irrigation', 'Irrigation'),
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Expenses'
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.category} - ₹{self.amount}"


class Income(models.Model):
    """Income model for tracking farm income"""
    INCOME_CATEGORIES = [
        ('crop_sale', 'Crop Sale'),
        ('livestock_sale', 'Livestock Sale'),
        ('government_subsidy', 'Government Subsidy'),
        ('rental_income', 'Rental Income'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='incomes')
    category = models.CharField(max_length=50, choices=INCOME_CATEGORIES, default='crop_sale')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Incomes'
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.category} - ₹{self.amount}"


class Budget(models.Model):
    """Budget model for planning farm budgets"""
    BUDGET_CATEGORIES = [
        ('seeds', 'Seeds'),
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('irrigation', 'Irrigation'),
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('seasonal', 'Seasonal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=50, choices=BUDGET_CATEGORIES)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name_plural = 'Budgets'
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.category} - ₹{self.allocated_amount}"
    
    def get_spent_amount(self):
        """Calculate total spent amount for this budget category in the period"""
        expenses = Expense.objects.filter(
            farm=self.farm,
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        return sum(expense.amount for expense in expenses)
    
    def get_remaining_amount(self):
        """Calculate remaining budget"""
        return self.allocated_amount - self.get_spent_amount()
    
    def get_percentage_spent(self):
        """Calculate percentage of budget spent"""
        if self.allocated_amount == 0:
            return 0
        return (self.get_spent_amount() / self.allocated_amount) * 100


class CropStage(models.Model):
    """Crop lifecycle stage tracking model"""
    STAGE_CHOICES = [
        ('preparation', 'Land Preparation'),
        ('planting', 'Planting'),
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative Growth'),
        ('flowering', 'Flowering'),
        ('fruiting', 'Fruiting'),
        ('maturation', 'Maturation'),
        ('harvesting', 'Harvesting'),
        ('post_harvest', 'Post-Harvest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_stages')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='crop_stages')
    stage_name = models.CharField(max_length=50, choices=STAGE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'stage_name']
        verbose_name_plural = 'Crop Stages'
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.get_stage_name_display()} ({self.start_date})"
    
    def get_duration_days(self):
        """Calculate duration of stage in days"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None


class CropCalendar(models.Model):
    """Crop calendar events and reminders model"""
    EVENT_TYPE_CHOICES = [
        ('watering', 'Watering'),
        ('fertilizing', 'Fertilizing'),
        ('pest_control', 'Pest Control'),
        ('weeding', 'Weeding'),
        ('pruning', 'Pruning'),
        ('harvesting', 'Harvesting'),
        ('soil_test', 'Soil Test'),
        ('irrigation', 'Irrigation'),
        ('planting', 'Planting'),
        ('transplanting', 'Transplanting'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_calendar_events')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='calendar_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    reminder_days = models.IntegerField(default=0, help_text="Days before event to send reminder (0 = no reminder)")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'event_type']
        verbose_name_plural = 'Crop Calendar Events'
    
    def __str__(self):
        return f"{self.farm.farm_name} - {self.get_event_type_display()} ({self.date})"
    
    def get_reminder_date(self):
        """Calculate when reminder should be sent"""
        if self.reminder_days > 0:
            from datetime import timedelta
            return self.date - timedelta(days=self.reminder_days)
        return None
    
    def is_due_soon(self, days=7):
        """Check if event is due within specified days"""
        from datetime import date, timedelta
        today = date.today()
        days_until = (self.date - today).days
        return 0 <= days_until <= days and not self.completed