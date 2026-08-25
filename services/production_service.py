from datetime import datetime
from database.database import SessionLocal
from database.models import Production, ProductionItem, Contract
from services.inventory_service import consume_fabric, add_product
from services.calculation_service import calculate_total_consumption


def register_production(product_name, contract_id, quantity, fabric_id, fabric_consumption_per_unit, seam_allowance=5,
                        waste_percentage=5):
    """
    ثبت تولید صافی

    product_name: نام صافی
    contract_id: شناسه قرارداد
    quantity: تعداد تولید
    fabric_id: شناسه پارچه
    fabric_consumption_per_unit: مصرف پارچه برای هر صافی
    seam_allowance: اضافه دوخت
    waste_percentage: درصد پرت
    """
    db = SessionLocal()
    try:
        # محاسبه مصرف کل پارچه
        total_consumption, single_consumption = calculate_total_consumption(
            length=0,  # طول از قرارداد خوانده می‌شود
            width=0,  # عرض از قرارداد خوانده می‌شود
            diameter=fabric_consumption_per_unit,  # قطر معادل مصرف
            seam_allowance=seam_allowance,
            quantity=quantity,
            waste_percentage=waste_percentage
        )

        # ثبت تولید
        production = Production(
            product_name=product_name,
            contract_id=contract_id,
            quantity=quantity,
            fabric_consumed=total_consumption,
            production_date=datetime.now()
        )
        db.add(production)
        db.flush()

        # ثبت آیتم تولید
        production_item = ProductionItem(
            production_id=production.id,
            fabric_id=fabric_id,
            quantity=total_consumption
        )
        db.add(production_item)

        # کسر پارچه از انبار
        fabric_result, fabric_error = consume_fabric(
            fabric_id=fabric_id,
            quantity=total_consumption,
            purpose=f'تولید {product_name} - {quantity} عدد'
        )

        if fabric_error:
            db.rollback()
            return None, fabric_error

        # افزودن محصول به انبار
        product_result, product_error = add_product(
            name=product_name,
            length=0,  # از قرارداد
            width=0,  # از قرارداد
            consumer_part='',
            quantity=quantity,
            description=f'تولید {quantity} عدد'
        )

        if product_error:
            db.rollback()
            return None, product_error

        db.commit()
        return production, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت تولید: {str(e)}'
    finally:
        db.close()


def get_all_productions():
    """دریافت همه تولیدات"""
    db = SessionLocal()
    try:
        return db.query(Production).order_by(Production.production_date.desc()).all()
    finally:
        db.close()


def get_productions_by_date(date):
    """دریافت تولیدات یک تاریخ مشخص"""
    db = SessionLocal()
    try:
        return db.query(Production).filter(
            Production.production_date >= date.replace(hour=0, minute=0, second=0),
            Production.production_date <= date.replace(hour=23, minute=59, second=59)
        ).all()
    finally:
        db.close()


def get_productions_by_month(year, month):
    """دریافت تولیدات یک ماه مشخص"""
    db = SessionLocal()
    try:
        from datetime import date
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return db.query(Production).filter(
            Production.production_date >= start_date,
            Production.production_date < end_date
        ).all()
    finally:
        db.close()


def get_today_productions():
    """دریافت تولیدات امروز"""
    today = datetime.now().date()
    return get_productions_by_date(datetime(today.year, today.month, today.day))