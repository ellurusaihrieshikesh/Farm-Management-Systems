from django.contrib import admin
from .models import Farm, TodoList, Expense, Income, Budget, CropStage, CropCalendar

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['farm_name', 'crop_type', 'location', 'area', 'start_date', 'user']
    list_filter = ['crop_type', 'area_unit', 'created_at']
    search_fields = ['farm_name', 'location', 'crop_type']

@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ['task', 'farm', 'user', 'priority', 'completed', 'due_date', 'created_at']
    list_filter = ['completed', 'priority', 'created_at', 'farm']
    search_fields = ['task', 'description', 'farm__farm_name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['farm', 'category', 'amount', 'date', 'user', 'created_at']
    list_filter = ['category', 'date', 'created_at', 'farm']
    search_fields = ['description', 'farm__farm_name']
    date_hierarchy = 'date'

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['farm', 'category', 'amount', 'date', 'user', 'created_at']
    list_filter = ['category', 'date', 'created_at', 'farm']
    search_fields = ['description', 'farm__farm_name']
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['farm', 'category', 'allocated_amount', 'period', 'start_date', 'end_date', 'user']
    list_filter = ['category', 'period', 'start_date', 'farm']
    search_fields = ['description', 'farm__farm_name']
    date_hierarchy = 'start_date'

@admin.register(CropStage)
class CropStageAdmin(admin.ModelAdmin):
    list_display = ['farm', 'stage_name', 'start_date', 'end_date', 'completed', 'user', 'created_at']
    list_filter = ['stage_name', 'completed', 'start_date', 'farm']
    search_fields = ['notes', 'farm__farm_name']
    date_hierarchy = 'start_date'

@admin.register(CropCalendar)
class CropCalendarAdmin(admin.ModelAdmin):
    list_display = ['farm', 'event_type', 'date', 'reminder_days', 'completed', 'user', 'created_at']
    list_filter = ['event_type', 'completed', 'date', 'farm']
    search_fields = ['description', 'farm__farm_name']
    date_hierarchy = 'date'

