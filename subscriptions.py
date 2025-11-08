"""Модуль для управления подписками пользователей"""
import json
import os
from datetime import datetime, timedelta

SUBSCRIPTIONS_FILE = "data/subscriptions.json"

def load_subscriptions():
    """Загрузить данные о подписках"""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(SUBSCRIPTIONS_FILE):
        with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_subscriptions(subscriptions):
    """Сохранить данные о подписках"""
    os.makedirs("data", exist_ok=True)
    with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscriptions, f, ensure_ascii=False, indent=2)

def is_premium_user(user_id):
    """Проверить, есть ли у пользователя активная подписка"""
    subscriptions = load_subscriptions()
    user_id_str = str(user_id)

    if user_id_str not in subscriptions:
        return False

    expiry_date = datetime.fromisoformat(subscriptions[user_id_str]["expiry"])
    return datetime.now() < expiry_date

def activate_subscription(user_id, days=30):
    """Активировать подписку для пользователя"""
    subscriptions = load_subscriptions()
    user_id_str = str(user_id)

    expiry_date = datetime.now() + timedelta(days=days)
    subscriptions[user_id_str] = {
        "activated": datetime.now().isoformat(),
        "expiry": expiry_date.isoformat(),
        "days": days
    }

    save_subscriptions(subscriptions)
    return expiry_date

def get_subscription_info(user_id):
    """Получить информацию о подписке пользователя"""
    subscriptions = load_subscriptions()
    user_id_str = str(user_id)

    if user_id_str not in subscriptions:
        return None

    return subscriptions[user_id_str]
