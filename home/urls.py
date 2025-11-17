from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('management/', views.management, name='management'),
    path('farm/edit/<int:farm_id>/', views.edit_farm, name='edit_farm'),
    path('farm/delete/<int:farm_id>/', views.delete_farm, name='delete_farm'),
    path('todo/add/', views.add_todo, name='add_todo'),
    path('todo/toggle/<int:todo_id>/', views.toggle_todo, name='toggle_todo'),
    path('todo/delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('chatbot/query/', views.chatbot_query, name='chatbot_query'),

    # Financial Management URLs
    path('financial/', views.financial_overview, name='financial_overview'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/add/', views.add_income, name='add_income'),
    path('incomes/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('incomes/delete/<int:income_id>/', views.delete_income, name='delete_income'),
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/edit/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('budgets/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),

    # Crop Calendar & Scheduling URLs
    path('crop-calendar/', views.crop_calendar, name='crop_calendar'),
    path('crop-stages/', views.crop_stages_list, name='crop_stages_list'),
    path('crop-stages/add/', views.add_crop_stage, name='add_crop_stage'),
    path('crop-stages/edit/<int:stage_id>/', views.edit_crop_stage, name='edit_crop_stage'),
    path('crop-stages/delete/<int:stage_id>/', views.delete_crop_stage, name='delete_crop_stage'),
    path('calendar-events/', views.calendar_events_list, name='calendar_events_list'),
    path('calendar-events/add/', views.add_calendar_event, name='add_calendar_event'),
    path('calendar-events/edit/<int:event_id>/', views.edit_calendar_event, name='edit_calendar_event'),
    path('calendar-events/delete/<int:event_id>/', views.delete_calendar_event, name='delete_calendar_event'),
    path('calendar-events/toggle/<int:event_id>/', views.toggle_calendar_event, name='toggle_calendar_event'),
]