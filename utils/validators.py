from datetime import datetime


def validate_required(value, field_name):
    """اعتبارسنجی فیلد ضروری"""
    if not value or (isinstance(value, str) and not value.strip()):
        return False, f'{field_name} نمی‌تواند خالی باشد'
    return True, None


def validate_positive_number(value, field_name):
    """اعتبارسنجی عدد مثبت"""
    try:
        num = float(value)
        if num < 0:
            return False, f'{field_name} نمی‌تواند منفی باشد'
        return True, None
    except:
        return False, f'{field_name} باید عدد باشد'


def validate_positive_integer(value, field_name):
    """اعتبارسنجی عدد صحیح مثبت"""
    try:
        num = int(value)
        if num < 0:
            return False, f'{field_name} نمی‌تواند منفی باشد'
        return True, None
    except:
        return False, f'{field_name} باید عدد صحیح باشد'


def validate_date(value, field_name):
    """اعتبارسنجی تاریخ"""
    if isinstance(value, datetime):
        return True, None

    try:
        datetime.strptime(str(value), '%Y-%m-%d')
        return True, None
    except:
        return False, f'{field_name} نامعتبر است'


def validate_username(value):
    """اعتبارسنجی نام کاربری"""
    valid, error = validate_required(value, 'نام کاربری')
    if not valid:
        return False, error

    if len(value) < 3:
        return False, 'نام کاربری باید حداقل ۳ کاراکتر باشد'

    if len(value) > 50:
        return False, 'نام کاربری نمی‌تواند بیشتر از ۵۰ کاراکتر باشد'

    return True, None


def validate_password(value):
    """اعتبارسنجی رمز عبور"""
    valid, error = validate_required(value, 'رمز عبور')
    if not valid:
        return False, error

    if len(value) < 6:
        return False, 'رمز عبور باید حداقل ۶ کاراکتر باشد'

    return True, None


def validate_phone(value):
    """اعتبارسنجی شماره تماس"""
    if not value:
        return True, None  # اختیاری

    import re
    pattern = r'^[0-9+\-\s]{10,15}$'
    if not re.match(pattern, value):
        return False, 'شماره تماس نامعتبر است'

    return True, None