from app import app, db  # Замініть 'your_application' на назву вашого файлу з Flask-додатком
from models import User  # Якщо ваша модель User в окремому файлі

# Створіть контекст додатку
with app.app_context():
    db.create_all()  # Це створить базу даних та таблиці