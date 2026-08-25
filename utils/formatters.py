from persiantools.jdatetime import JalaliDate
from datetime import datetime


def format_number(number):
    """فرمت عدد با جداکننده هزارگان"""
    try:
        return f"{int(number):,}"
    except:
        return str(number)


def format_currency(amount):
    """فرمت مبلغ به تومان"""
    try:
        return f"{format_number(amount)} تومان"
    except:
        return str(amount)


def format_float(value, decimal_places=2):
    """فرمت عدد اعشاری"""
    try:
        return f"{float(value):.{decimal_places}f}"
    except:
        return str(value)


def to_persian_date(date_obj):
    """تبدیل تاریخ میلادی به شمسی"""
    if not date_obj:
        return ''

    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except:
            return date_obj

    try:
        jalali = JalaliDate(date_obj)
        return jalali.strftime('%Y/%m/%d')
    except:
        return str(date_obj)


def to_persian_datetime(datetime_obj):
    """تبدیل تاریخ و ساعت میلادی به شمسی"""
    if not datetime_obj:
        return ''

    try:
        jalali = JalaliDate(datetime_obj)
        time_str = datetime_obj.strftime('%H:%M')
        return f"{jalali.strftime('%Y/%m/%d')} - {time_str}"
    except:
        return str(datetime_obj)


def format_percent(value):
    """فرمت درصد"""
    try:
        return f"%{float(value):.1f}"
    except:
        return str(value)