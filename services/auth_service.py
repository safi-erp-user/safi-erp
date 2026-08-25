import hashlib
import os
from datetime import datetime
from database.database import SessionLocal
from database.models import User


def hash_password(password):
    """هش کردن رمز عبور"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()


def verify_password(password, password_hash):
    """بررسی رمز عبور"""
    try:
        salt_hex, key_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key == new_key
    except:
        return False


def authenticate_user(username, password):
    """ورود کاربر"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return None, 'کاربری با این نام پیدا نشد'

        if not user.is_active:
            return None, 'این کاربر غیرفعال است'

        if not verify_password(password, user.password_hash):
            return None, 'رمز عبور اشتباه است'

        # ثبت آخرین ورود
        user.last_login = datetime.now()
        db.commit()

        return user, None
    finally:
        db.close()


def get_user_by_id(user_id):
    """دریافت کاربر با شناسه"""
    db = SessionLocal()
    try:
        return db.query(User).filter_by(id=user_id).first()
    finally:
        db.close()


def get_all_users():
    """دریافت همه کاربران"""
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def create_user(username, password, full_name, role='USER'):
    """ایجاد کاربر جدید"""
    db = SessionLocal()
    try:
        # بررسی تکراری بودن نام کاربری
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            return None, 'این نام کاربری قبلاً ثبت شده است'

        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        return user, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ایجاد کاربر: {str(e)}'
    finally:
        db.close()


def update_user(user_id, full_name=None, role=None, is_active=None):
    """ویرایش کاربر"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return None, 'کاربر پیدا نشد'

        if full_name:
            user.full_name = full_name
        if role:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        db.commit()
        return user, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ویرایش کاربر: {str(e)}'
    finally:
        db.close()


def delete_user(user_id):
    """حذف کاربر"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return False, 'کاربر پیدا نشد'

        db.delete(user)
        db.commit()
        return True, None
    except Exception as e:
        db.rollback()
        return False, f'خطا در حذف کاربر: {str(e)}'
    finally:
        db.close()