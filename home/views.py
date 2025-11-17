from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms import ModelForm
from .models import UserProfile

def index(request):
    """Landing page view"""
    return render(request, 'home/index.html')

def login_view(request):
    """Login page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'home/login.html')

def register_view(request):
    """Registration page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validation
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'home/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'home/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'home/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'home/register.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

@login_required
def dashboard(request):
    """Dashboard view"""
    from . import models
    from django.db.models import Sum
    from datetime import timedelta
    from django.utils import timezone
    
    # Get stats for dashboard
    farms_count = models.Farm.objects.filter(user=request.user).count()
    
    # Get all todos for user
    todos = models.TodoList.objects.filter(user=request.user)
    todos_count = todos.count()
    
    # Get user's farms for the todo form
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Financial statistics (last 30 days)
    start_date = timezone.now().date() - timedelta(days=30)
    total_expenses = models.Expense.objects.filter(
        user=request.user,
        date__gte=start_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_income = models.Income.objects.filter(
        user=request.user,
        date__gte=start_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_profit = total_income - total_expenses
    
    context = {
        'farms_count': farms_count,
        'todos': todos,
        'todos_count': todos_count,
        'user_farms': user_farms,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_profit': net_profit,
    }
    return render(request, 'home/dashboard.html', context)

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']

@login_required
def edit_profile(request):
    """Allow a logged-in user to edit personal details."""
    from .models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'home/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def management(request):
    """Management page view with farm CRUD operations"""
    from . import models
    
    # Get all farms for the logged-in user
    farms = models.Farm.objects.filter(user=request.user)
    
    # Handle farm creation
    if request.method == 'POST' and 'add_farm' in request.POST:
        farm_name = request.POST.get('farm_name')
        location = request.POST.get('location')
        crop_type = request.POST.get('crop_type')
        area = request.POST.get('area')
        area_unit = request.POST.get('area_unit')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            models.Farm.objects.create(
                user=request.user,
                farm_name=farm_name,
                location=location,
                crop_type=crop_type,
                area=area,
                area_unit=area_unit,
                start_date=start_date,
                end_date=end_date
            )
            messages.success(request, 'Farm added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding farm: {str(e)}')
        
        return redirect('management')
    
    context = {
        'farms': farms,
    }
    return render(request, 'home/management.html', context)

@login_required
def edit_farm(request, farm_id):
    """Edit farm view"""
    from . import models
    
    try:
        farm = models.Farm.objects.get(id=farm_id, user=request.user)
    except models.Farm.DoesNotExist:
        messages.error(request, 'Farm not found.')
        return redirect('management')
    
    if request.method == 'POST':
        farm.farm_name = request.POST.get('farm_name')
        farm.location = request.POST.get('location')
        farm.crop_type = request.POST.get('crop_type')
        farm.area = request.POST.get('area')
        farm.area_unit = request.POST.get('area_unit')
        farm.start_date = request.POST.get('start_date')
        farm.end_date = request.POST.get('end_date')
        
        try:
            farm.save()
            messages.success(request, 'Farm updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating farm: {str(e)}')
        
        return redirect('management')
    
    context = {
        'farm': farm,
        'farms': models.Farm.objects.filter(user=request.user),
    }
    return render(request, 'home/management.html', context)

@login_required
def delete_farm(request, farm_id):
    """Delete farm view"""
    from . import models
    
    try:
        farm = models.Farm.objects.get(id=farm_id, user=request.user)
        farm_name = farm.farm_name
        farm.delete()
        messages.success(request, f'Farm "{farm_name}" deleted successfully!')
    except models.Farm.DoesNotExist:
        messages.error(request, 'Farm not found.')
    
    return redirect('management')

@login_required
def add_todo(request):
    """Add todo view"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        task = request.POST.get('task')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.TodoList.objects.create(
                user=request.user,
                farm=farm,
                task=task,
                description=description,
                priority=priority,
                due_date=due_date if due_date else None
            )
            messages.success(request, 'Todo added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding todo: {str(e)}')
    
    return redirect('dashboard')

@login_required
def toggle_todo(request, todo_id):
    """Toggle todo completion status"""
    from . import models
    
    try:
        todo = models.TodoList.objects.get(id=todo_id, user=request.user)
        todo.completed = not todo.completed
        todo.save()
        status = "completed" if todo.completed else "reopened"
        messages.success(request, f'Todo {status} successfully!')
    except models.TodoList.DoesNotExist:
        messages.error(request, 'Todo not found.')
    
    return redirect('dashboard')

@login_required
def delete_todo(request, todo_id):
    """Delete todo view"""
    from . import models
    
    try:
        todo = models.TodoList.objects.get(id=todo_id, user=request.user)
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
    except models.TodoList.DoesNotExist:
        messages.error(request, 'Todo not found.')
    
    return redirect('dashboard')


@login_required
def chatbot_query(request):
    """Handle chatbot queries using Gemini API"""
    if request.method == 'POST':
        import json
        import google.generativeai as genai
        from django.conf import settings
        from django.http import JsonResponse
        
        try:
            # Get the user's message
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Configure Gemini API (you'll need to set GOOGLE_API_KEY in settings)
            api_key = getattr(settings, 'GOOGLE_API_KEY', None)
            if not api_key:
                return JsonResponse({
                    'response': 'API key not configured. Please contact the administrator.'
                })
            
            genai.configure(api_key=api_key)
            
            # Use a known working model from the available list
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            # Create a prompt that's specific to farming with better structure
            prompt = f"""
            You are an AI farming assistant specialized in agricultural knowledge. Follow these guidelines:
            
            1. Provide practical, actionable advice for farmers
            2. Be concise but informative
            3. When asked about weather, acknowledge you don't have real-time data but suggest specific resources
            4. For soil health, crop care, and farming practices, provide detailed, evidence-based recommendations
            5. Structure responses with clear headings or bullet points when appropriate
            
            User question: {user_message}
            
            Response:
            """
            
            # Generate response
            response = model.generate_content(prompt)
            
            return JsonResponse({
                'response': response.text
            })
        except Exception as e:
            return JsonResponse({
                'response': f"Sorry, I encountered an error: {str(e)}"
            })
    
        return JsonResponse({'response': 'Invalid request method'})

# ==================== FINANCIAL MANAGEMENT VIEWS ====================

@login_required
def financial_overview(request):
    """Financial overview dashboard"""
    from . import models
    from django.db.models import Sum, Q
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get user's farms
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Date filters (default to last 30 days)
    date_filter = request.GET.get('period', '30')
    if date_filter == 'all':
        start_date = None
        end_date = None
    elif date_filter == '7':
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
    elif date_filter == '90':
        start_date = timezone.now().date() - timedelta(days=90)
        end_date = timezone.now().date()
    elif date_filter == '365':
        start_date = timezone.now().date() - timedelta(days=365)
        end_date = timezone.now().date()
    else:  # 30 days default
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
    
    # Filter expenses and incomes
    expense_filter = Q(user=request.user)
    income_filter = Q(user=request.user)
    
    if start_date and end_date:
        expense_filter &= Q(date__gte=start_date, date__lte=end_date)
        income_filter &= Q(date__gte=start_date, date__lte=end_date)
    
    # Calculate totals
    total_expenses = models.Expense.objects.filter(expense_filter).aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = models.Income.objects.filter(income_filter).aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_income - total_expenses
    
    # Expenses by category
    expenses_by_category = models.Expense.objects.filter(expense_filter).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Income by category
    incomes_by_category = models.Income.objects.filter(income_filter).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Expenses by farm
    expenses_by_farm = models.Expense.objects.filter(expense_filter).values('farm__farm_name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Recent transactions
    recent_expenses = models.Expense.objects.filter(user=request.user).order_by('-date')[:10]
    recent_incomes = models.Income.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Budget status
    active_budgets = models.Budget.objects.filter(
        user=request.user,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    context = {
        'user_farms': user_farms,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_profit': net_profit,
        'expenses_by_category': expenses_by_category,
        'incomes_by_category': incomes_by_category,
        'expenses_by_farm': expenses_by_farm,
        'recent_expenses': recent_expenses,
        'recent_incomes': recent_incomes,
        'active_budgets': active_budgets,
        'date_filter': date_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'home/financial_overview.html', context)


@login_required
def expense_list(request):
    """List all expenses"""
    from . import models
    
    expenses = models.Expense.objects.filter(user=request.user).order_by('-date')
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Filtering
    farm_filter = request.GET.get('farm')
    category_filter = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if farm_filter:
        expenses = expenses.filter(farm_id=farm_filter)
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    
    total_amount = sum(expense.amount for expense in expenses)
    
    context = {
        'expenses': expenses,
        'user_farms': user_farms,
        'total_amount': total_amount,
        'farm_filter': farm_filter,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'home/expense_list.html', context)


@login_required
def add_expense(request):
    """Add new expense"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.Expense.objects.create(
                user=request.user,
                farm=farm,
                category=category,
                amount=amount,
                description=description,
                date=date
            )
            messages.success(request, 'Expense added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')
        
        return redirect('expense_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    return render(request, 'home/add_expense.html', {'user_farms': user_farms})


@login_required
def edit_expense(request, expense_id):
    """Edit expense"""
    from . import models
    
    try:
        expense = models.Expense.objects.get(id=expense_id, user=request.user)
    except models.Expense.DoesNotExist:
        messages.error(request, 'Expense not found.')
        return redirect('expense_list')
    
    if request.method == 'POST':
        expense.farm = models.Farm.objects.get(id=request.POST.get('farm'), user=request.user)
        expense.category = request.POST.get('category')
        expense.amount = request.POST.get('amount')
        expense.description = request.POST.get('description', '')
        expense.date = request.POST.get('date')
        expense.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('expense_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    context = {
        'expense': expense,
        'user_farms': user_farms,
    }
    return render(request, 'home/edit_expense.html', context)


@login_required
def delete_expense(request, expense_id):
    """Delete expense"""
    from . import models
    
    try:
        expense = models.Expense.objects.get(id=expense_id, user=request.user)
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
    except models.Expense.DoesNotExist:
        messages.error(request, 'Expense not found.')
    
    return redirect('expense_list')


@login_required
def income_list(request):
    """List all incomes"""
    from . import models
    
    incomes = models.Income.objects.filter(user=request.user).order_by('-date')
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Filtering
    farm_filter = request.GET.get('farm')
    category_filter = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if farm_filter:
        incomes = incomes.filter(farm_id=farm_filter)
    if category_filter:
        incomes = incomes.filter(category=category_filter)
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)
    
    total_amount = sum(income.amount for income in incomes)
    
    context = {
        'incomes': incomes,
        'user_farms': user_farms,
        'total_amount': total_amount,
        'farm_filter': farm_filter,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'home/income_list.html', context)


@login_required
def add_income(request):
    """Add new income"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.Income.objects.create(
                user=request.user,
                farm=farm,
                category=category,
                amount=amount,
                description=description,
                date=date
            )
            messages.success(request, 'Income added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding income: {str(e)}')
        
        return redirect('income_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    return render(request, 'home/add_income.html', {'user_farms': user_farms})


@login_required
def edit_income(request, income_id):
    """Edit income"""
    from . import models
    
    try:
        income = models.Income.objects.get(id=income_id, user=request.user)
    except models.Income.DoesNotExist:
        messages.error(request, 'Income not found.')
        return redirect('income_list')
    
    if request.method == 'POST':
        income.farm = models.Farm.objects.get(id=request.POST.get('farm'), user=request.user)
        income.category = request.POST.get('category')
        income.amount = request.POST.get('amount')
        income.description = request.POST.get('description', '')
        income.date = request.POST.get('date')
        income.save()
        messages.success(request, 'Income updated successfully!')
        return redirect('income_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    context = {
        'income': income,
        'user_farms': user_farms,
    }
    return render(request, 'home/edit_income.html', context)


@login_required
def delete_income(request, income_id):
    """Delete income"""
    from . import models
    
    try:
        income = models.Income.objects.get(id=income_id, user=request.user)
        income.delete()
        messages.success(request, 'Income deleted successfully!')
    except models.Income.DoesNotExist:
        messages.error(request, 'Income not found.')
    
    return redirect('income_list')


@login_required
def budget_list(request):
    """List all budgets"""
    from . import models
    
    budgets = models.Budget.objects.filter(user=request.user).order_by('-start_date')
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Filtering
    farm_filter = request.GET.get('farm')
    period_filter = request.GET.get('period')
    
    if farm_filter:
        budgets = budgets.filter(farm_id=farm_filter)
    if period_filter:
        budgets = budgets.filter(period=period_filter)
    
    context = {
        'budgets': budgets,
        'user_farms': user_farms,
        'farm_filter': farm_filter,
        'period_filter': period_filter,
    }
    return render(request, 'home/budget_list.html', context)


@login_required
def add_budget(request):
    """Add new budget"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        category = request.POST.get('category')
        allocated_amount = request.POST.get('allocated_amount')
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description', '')
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.Budget.objects.create(
                user=request.user,
                farm=farm,
                category=category,
                allocated_amount=allocated_amount,
                period=period,
                start_date=start_date,
                end_date=end_date,
                description=description
            )
            messages.success(request, 'Budget added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding budget: {str(e)}')
        
        return redirect('budget_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    return render(request, 'home/add_budget.html', {'user_farms': user_farms})


@login_required
def edit_budget(request, budget_id):
    """Edit budget"""
    from . import models
    
    try:
        budget = models.Budget.objects.get(id=budget_id, user=request.user)
    except models.Budget.DoesNotExist:
        messages.error(request, 'Budget not found.')
        return redirect('budget_list')
    
    if request.method == 'POST':
        budget.farm = models.Farm.objects.get(id=request.POST.get('farm'), user=request.user)
        budget.category = request.POST.get('category')
        budget.allocated_amount = request.POST.get('allocated_amount')
        budget.period = request.POST.get('period')
        budget.start_date = request.POST.get('start_date')
        budget.end_date = request.POST.get('end_date')
        budget.description = request.POST.get('description', '')
        budget.save()
        messages.success(request, 'Budget updated successfully!')
        return redirect('budget_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    context = {
        'budget': budget,
        'user_farms': user_farms,
    }
    return render(request, 'home/edit_budget.html', context)


@login_required
def delete_budget(request, budget_id):
    """Delete budget"""
    from . import models
    
    try:
        budget = models.Budget.objects.get(id=budget_id, user=request.user)
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
    except models.Budget.DoesNotExist:
        messages.error(request, 'Budget not found.')
    
    return redirect('budget_list')


# ==================== CROP CALENDAR & SCHEDULING VIEWS ====================

@login_required
def crop_calendar(request):
    """Main crop calendar view with calendar display"""
    from . import models
    from datetime import date, timedelta
    from calendar import monthrange
    
    # Get user's farms
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Get month/year from query params (default to current month)
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Calculate first and last day of month
    first_day = date(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)
    
    # Get all calendar events for the month
    calendar_events = models.CropCalendar.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date', 'event_type')
    
    # Get all crop stages
    crop_stages = models.CropStage.objects.filter(
        user=request.user
    ).order_by('start_date')
    
    # Get upcoming events (next 7 days)
    upcoming_date = today + timedelta(days=7)
    upcoming_events = models.CropCalendar.objects.filter(
        user=request.user,
        date__gte=today,
        date__lte=upcoming_date,
        completed=False
    ).order_by('date')[:10]
    
    # Group events by date for calendar display
    events_by_date = {}
    for event in calendar_events:
        event_date = event.date
        if event_date not in events_by_date:
            events_by_date[event_date] = []
        events_by_date[event_date].append(event)
    
    # Prepare calendar days for display
    import calendar as cal
    cal_obj = cal.monthcalendar(year, month)
    calendar_days = []
    for week in cal_obj:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)  # Day from other month
            else:
                day_date = date(year, month, day)
                week_days.append({
                    'day': day,
                    'date': day_date,
                    'is_today': day_date == today,
                    'events': events_by_date.get(day_date, [])
                })
        calendar_days.append(week_days)
    
    # Calculate previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Month name
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month]
    
    context = {
        'user_farms': user_farms,
        'calendar_events': calendar_events,
        'crop_stages': crop_stages,
        'upcoming_events': upcoming_events,
        'events_by_date': events_by_date,
        'calendar_days': calendar_days,
        'current_date': today,
        'view_year': year,
        'view_month': month,
        'month_name': month_name,
        'first_day': first_day,
        'last_day': last_day,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    return render(request, 'home/crop_calendar.html', context)


@login_required
def crop_stages_list(request):
    """List all crop stages"""
    from . import models
    
    crop_stages = models.CropStage.objects.filter(user=request.user).order_by('-start_date')
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Filtering
    farm_filter = request.GET.get('farm')
    stage_filter = request.GET.get('stage')
    completed_filter = request.GET.get('completed')
    
    if farm_filter:
        crop_stages = crop_stages.filter(farm_id=farm_filter)
    if stage_filter:
        crop_stages = crop_stages.filter(stage_name=stage_filter)
    if completed_filter == 'true':
        crop_stages = crop_stages.filter(completed=True)
    elif completed_filter == 'false':
        crop_stages = crop_stages.filter(completed=False)
    
    context = {
        'crop_stages': crop_stages,
        'user_farms': user_farms,
        'farm_filter': farm_filter,
        'stage_filter': stage_filter,
        'completed_filter': completed_filter,
    }
    return render(request, 'home/crop_stages_list.html', context)


@login_required
def add_crop_stage(request):
    """Add new crop stage"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        stage_name = request.POST.get('stage_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        notes = request.POST.get('notes', '')
        completed = request.POST.get('completed') == 'on'
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.CropStage.objects.create(
                user=request.user,
                farm=farm,
                stage_name=stage_name,
                start_date=start_date,
                end_date=end_date,
                notes=notes,
                completed=completed
            )
            messages.success(request, 'Crop stage added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding crop stage: {str(e)}')
        
        return redirect('crop_stages_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    return render(request, 'home/add_crop_stage.html', {'user_farms': user_farms})


@login_required
def edit_crop_stage(request, stage_id):
    """Edit crop stage"""
    from . import models
    
    try:
        stage = models.CropStage.objects.get(id=stage_id, user=request.user)
    except models.CropStage.DoesNotExist:
        messages.error(request, 'Crop stage not found.')
        return redirect('crop_stages_list')
    
    if request.method == 'POST':
        stage.farm = models.Farm.objects.get(id=request.POST.get('farm'), user=request.user)
        stage.stage_name = request.POST.get('stage_name')
        stage.start_date = request.POST.get('start_date')
        stage.end_date = request.POST.get('end_date') or None
        stage.notes = request.POST.get('notes', '')
        stage.completed = request.POST.get('completed') == 'on'
        stage.save()
        messages.success(request, 'Crop stage updated successfully!')
        return redirect('crop_stages_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    context = {
        'stage': stage,
        'user_farms': user_farms,
    }
    return render(request, 'home/edit_crop_stage.html', context)


@login_required
def delete_crop_stage(request, stage_id):
    """Delete crop stage"""
    from . import models
    
    try:
        stage = models.CropStage.objects.get(id=stage_id, user=request.user)
        stage.delete()
        messages.success(request, 'Crop stage deleted successfully!')
    except models.CropStage.DoesNotExist:
        messages.error(request, 'Crop stage not found.')
    
    return redirect('crop_stages_list')


@login_required
def calendar_events_list(request):
    """List all calendar events"""
    from . import models
    
    events = models.CropCalendar.objects.filter(user=request.user).order_by('date')
    user_farms = models.Farm.objects.filter(user=request.user)
    
    # Filtering
    farm_filter = request.GET.get('farm')
    event_type_filter = request.GET.get('event_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    completed_filter = request.GET.get('completed')
    
    if farm_filter:
        events = events.filter(farm_id=farm_filter)
    if event_type_filter:
        events = events.filter(event_type=event_type_filter)
    if date_from:
        events = events.filter(date__gte=date_from)
    if date_to:
        events = events.filter(date__lte=date_to)
    if completed_filter == 'true':
        events = events.filter(completed=True)
    elif completed_filter == 'false':
        events = events.filter(completed=False)
    
    context = {
        'events': events,
        'user_farms': user_farms,
        'farm_filter': farm_filter,
        'event_type_filter': event_type_filter,
        'date_from': date_from,
        'date_to': date_to,
        'completed_filter': completed_filter,
    }
    return render(request, 'home/calendar_events_list.html', context)


@login_required
def add_calendar_event(request):
    """Add new calendar event"""
    from . import models
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        event_type = request.POST.get('event_type')
        date = request.POST.get('date')
        description = request.POST.get('description', '')
        reminder_days = int(request.POST.get('reminder_days', 0))
        completed = request.POST.get('completed') == 'on'
        
        try:
            farm = models.Farm.objects.get(id=farm_id, user=request.user)
            models.CropCalendar.objects.create(
                user=request.user,
                farm=farm,
                event_type=event_type,
                date=date,
                description=description,
                reminder_days=reminder_days,
                completed=completed
            )
            messages.success(request, 'Calendar event added successfully!')
        except models.Farm.DoesNotExist:
            messages.error(request, 'Farm not found.')
        except Exception as e:
            messages.error(request, f'Error adding calendar event: {str(e)}')
        
        return redirect('calendar_events_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    return render(request, 'home/add_calendar_event.html', {'user_farms': user_farms})


@login_required
def edit_calendar_event(request, event_id):
    """Edit calendar event"""
    from . import models
    
    try:
        event = models.CropCalendar.objects.get(id=event_id, user=request.user)
    except models.CropCalendar.DoesNotExist:
        messages.error(request, 'Calendar event not found.')
        return redirect('calendar_events_list')
    
    if request.method == 'POST':
        event.farm = models.Farm.objects.get(id=request.POST.get('farm'), user=request.user)
        event.event_type = request.POST.get('event_type')
        event.date = request.POST.get('date')
        event.description = request.POST.get('description', '')
        event.reminder_days = int(request.POST.get('reminder_days', 0))
        event.completed = request.POST.get('completed') == 'on'
        event.save()
        messages.success(request, 'Calendar event updated successfully!')
        return redirect('calendar_events_list')
    
    user_farms = models.Farm.objects.filter(user=request.user)
    context = {
        'event': event,
        'user_farms': user_farms,
    }
    return render(request, 'home/edit_calendar_event.html', context)


@login_required
def delete_calendar_event(request, event_id):
    """Delete calendar event"""
    from . import models
    
    try:
        event = models.CropCalendar.objects.get(id=event_id, user=request.user)
        event.delete()
        messages.success(request, 'Calendar event deleted successfully!')
    except models.CropCalendar.DoesNotExist:
        messages.error(request, 'Calendar event not found.')
    
    return redirect('calendar_events_list')


@login_required
def toggle_calendar_event(request, event_id):
    """Toggle calendar event completion status"""
    from . import models
    
    try:
        event = models.CropCalendar.objects.get(id=event_id, user=request.user)
        event.completed = not event.completed
        event.save()
        status = "completed" if event.completed else "reopened"
        messages.success(request, f'Event {status} successfully!')
    except models.CropCalendar.DoesNotExist:
        messages.error(request, 'Calendar event not found.')
    
    return redirect('crop_calendar')