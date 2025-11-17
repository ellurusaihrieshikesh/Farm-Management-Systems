"""
Simple script to view database contents in a readable format
Run: python view_database.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_portal.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import Farm, TodoList
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def view_users():
    print_header("USERS DATABASE")
    users = User.objects.all()
    print(f"Total Users: {users.count()}\n")
    
    if users.exists():
        for user in users:
            print(f"  User ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  First Name: {user.first_name or '(Not set)'}")
            print(f"  Last Name: {user.last_name or '(Not set)'}")
            print(f"  Is Staff: {user.is_staff}")
            print(f"  Is Superuser: {user.is_superuser}")
            print(f"  Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
            print(f"  Active: {user.is_active}")
            print(f"  {'-'*60}\n")
    else:
        print("No users found.\n")

def view_farms():
    print_header("FARMS DATABASE")
    farms = Farm.objects.all()
    print(f"Total Farms: {farms.count()}\n")
    
    if farms.exists():
        for farm in farms:
            print(f"  Farm ID: {farm.id}")
            print(f"  Farm Name: {farm.farm_name}")
            print(f"  Owner: {farm.user.username}")
            print(f"  Location: {farm.location}")
            print(f"  Crop Type: {farm.crop_type}")
            print(f"  Area: {farm.area} {farm.area_unit}")
            print(f"  Start Date: {farm.start_date}")
            print(f"  End Date: {farm.end_date}")
            print(f"  Created: {farm.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Updated: {farm.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  {'-'*60}\n")
    else:
        print("No farms found.\n")

def view_todos():
    print_header("TODO LIST")
    todos = TodoList.objects.all()
    print(f"Total Todos: {todos.count()}\n")
    
    if todos.exists():
        for todo in todos:
            print(f"  Todo ID: {todo.id}")
            print(f"  Farm: {todo.farm.farm_name}")
            print(f"  Owner: {todo.user.username}")
            print(f"  Task: {todo.task}")
            if todo.description:
                print(f"  Description: {todo.description}")
            print(f"  Priority: {todo.priority}")
            print(f"  Completed: {todo.completed}")
            if todo.due_date:
                print(f"  Due Date: {todo.due_date}")
            print(f"  Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  {'-'*60}\n")
    else:
        print("No todos found.\n")

def view_statistics():
    print_header("STATISTICS")
    total_users = User.objects.count()
    total_farms = Farm.objects.count()
    total_todos = TodoList.objects.count()
    completed_todos = TodoList.objects.filter(completed=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    print(f"Total Users: {total_users}")
    print(f"Active Users: {active_users}")
    print(f"Total Farms: {total_farms}")
    print(f"Total Todos: {total_todos}")
    print(f"Completed Todos: {completed_todos}")
    
    if total_farms > 0:
        farms_by_user = {}
        for farm in Farm.objects.all():
            username = farm.user.username
            farms_by_user[username] = farms_by_user.get(username, 0) + 1
        
        print("\nFarms by User:")
        for username, count in farms_by_user.items():
            print(f"  {username}: {count} farm(s)")
    
    print()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("=" + " "*68 + "=")
    print("=" + " "*20 + "DATABASE VIEWER" + " "*34 + "=")
    print("=" + " "*15 + "Digital Farm Management Portal" + " "*24 + "=")
    print("=" + " "*68 + "=")
    print("="*70)
    
    view_statistics()
    view_users()
    view_farms()
    view_todos()
    
    print("="*70)
    print("View complete! Database file: db.sqlite3")
    print("="*70 + "\n")

