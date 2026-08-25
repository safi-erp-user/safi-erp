from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

# مسیر دیتابیس
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'my.db')

# ایجاد engine
engine = create_engine(
    f'sqlite:///{DB_PATH}',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class برای مدل‌ها
Base = declarative_base()


def init_db():
    """ایجاد جداول در صورت عدم وجود"""
    from database import models  # Import models to register them
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency برای دریافت session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_default_data():
    """ایجاد داده‌های پیش‌فرض"""
    from database.models import User, AppSetting
    from services.auth_service import hash_password

    db = SessionLocal()
    try:
        # بررسی وجود کاربر admin
        admin = db.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                full_name='مدیر سیستم',
                role='ADMIN',
                is_active=True
            )
            db.add(admin)

        # تنظیمات پیش‌فرض
        settings = [
            {'key': 'workshop_name', 'value': 'کارگاه تولید صافی'},
            {'key': 'manager_name', 'value': 'مدیر'},
            {'key': 'currency', 'value': 'تومان'},
            {'key': 'settlement_limit', 'value': '20000000'},
            {'key': 'dark_mode', 'value': 'false'},
        ]

        for setting in settings:
            existing = db.query(AppSetting).filter_by(key=setting['key']).first()
            if not existing:
                db.add(AppSetting(**setting))

        db.commit()
    finally:
        db.close()