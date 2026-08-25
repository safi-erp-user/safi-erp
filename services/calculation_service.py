import math


def calculate_circle_area(diameter):
    """محاسبه مساحت دایره"""
    radius = diameter / 2
    return math.pi * radius ** 2


def calculate_circle_circumference(diameter):
    """محاسبه محیط دایره"""
    return math.pi * diameter


def calculate_fabric_consumption(length, width, diameter, seam_allowance):
    """
    محاسبه مصرف پارچه برای یک صافی

    length: طول صافی
    width: عرض صافی
    diameter: قطر صافی
    seam_allowance: اضافه دوخت
    """
    # محیط دایره
    circumference = calculate_circle_circumference(diameter)

    # مصرف پارچه = محیط + اضافه دوخت
    fabric_needed = circumference + (seam_allowance * 2)

    return fabric_needed


def calculate_total_consumption(length, width, diameter, seam_allowance, quantity, waste_percentage=0):
    """
    محاسبه مصرف کل پارچه برای تعداد مشخص

    length: طول صافی
    width: عرض صافی
    diameter: قطر صافی
    seam_allowance: اضافه دوخت
    quantity: تعداد صافی
    waste_percentage: درصد پرت
    """
    # مصرف یک صافی
    single_consumption = calculate_fabric_consumption(length, width, diameter, seam_allowance)

    # مصرف کل بدون پرت
    total = single_consumption * quantity

    # اضافه کردن پرت
    if waste_percentage > 0:
        waste = total * (waste_percentage / 100)
        total += waste

    return total, single_consumption


def calculate_dimensions(length=None, width=None, diameter=None, radius=None):
    """
    محاسبه ابعاد مختلف
    """
    results = {}

    if diameter:
        results['diameter'] = diameter
        results['radius'] = diameter / 2
        results['circumference'] = calculate_circle_circumference(diameter)
        results['area'] = calculate_circle_area(diameter)
    elif radius:
        results['radius'] = radius
        results['diameter'] = radius * 2
        results['circumference'] = calculate_circle_circumference(radius * 2)
        results['area'] = calculate_circle_area(radius * 2)

    if length:
        results['length'] = length
    if width:
        results['width'] = width

    return results