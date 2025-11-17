"""
Export database to JSON format
Run: python export_database.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_portal.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import Farm, TodoList
import json
from datetime import datetime

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return str(obj)

def export_users():
    users = User.objects.all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': serialize_datetime(user.date_joined),
            'last_login': serialize_datetime(user.last_login) if user.last_login else None,
        })
    
    return users_data

def export_farms():
    farms = Farm.objects.all()
    farms_data = []
    
    for farm in farms:
        farms_data.append({
            'id': farm.id,
            'farm_name': farm.farm_name,
            'owner_username': farm.user.username,
            'owner_id': farm.user.id,
            'location': farm.location,
            'crop_type': farm.crop_type,
            'area': str(farm.area),
            'area_unit': farm.area_unit,
            'start_date': str(farm.start_date),
            'end_date': farm.end_date,
            'created_at': serialize_datetime(farm.created_at),
            'updated_at': serialize_datetime(farm.updated_at),
        })
    
    return farms_data

def export_todos():
    todos = TodoList.objects.all()
    todos_data = []
    
    for todo in todos:
        todos_data.append({
            'id': todo.id,
            'farm_name': todo.farm.farm_name,
            'farm_id': todo.farm.id,
            'owner_username': todo.user.username,
            'owner_id': todo.user.id,
            'task': todo.task,
            'description': todo.description,
            'completed': todo.completed,
            'priority': todo.priority,
            'due_date': str(todo.due_date) if todo.due_date else None,
            'created_at': serialize_datetime(todo.created_at),
            'updated_at': serialize_datetime(todo.updated_at),
        })
    
    return todos_data

if __name__ == "__main__":
    data = {
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': 'db.sqlite3',
        'users': export_users(),
        'farms': export_farms(),
        'todos': export_todos(),
    }
    
    # Save to JSON file
    filename = f'database_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Database exported successfully to: {filename}")
    print(f"Total Users: {len(data['users'])}")
    print(f"Total Farms: {len(data['farms'])}")
    print(f"Total Todos: {len(data['todos'])}")
    print("\nYou can open this file in any text editor to view the data.")

