from datetime import datetime
from database.database import SessionLocal
from database.models import Fabric, FabricTransaction, Product, ProductTransaction


# ==================== FABRIC SERVICES ====================

def add_fabric(name, width, quantity, supplier, receiver, purpose, description=''):
    """ورود پارچه جدید به انبار"""
    db = SessionLocal()
    try:
        # بررسی وجود پارچه با همین نام و عرض
        fabric = db.query(Fabric).filter_by(name=name, width=width).first()

        if not fabric:
            # ایجاد پارچه جدید
            fabric = Fabric(
                name=name,
                width=width,
                current_stock=0
            )
            db.add(fabric)
            db.flush()

        # ثبت تراکنش ورود
        transaction = FabricTransaction(
            fabric_id=fabric.id,
            transaction_type='IN',
            quantity=quantity,
            supplier=supplier,
            receiver=receiver,
            purpose=purpose,
            description=description,
            date=datetime.now()
        )
        db.add(transaction)

        # به‌روزرسانی موجودی
        fabric.current_stock += quantity

        db.commit()
        return fabric, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت پارچه: {str(e)}'
    finally:
        db.close()


def consume_fabric(fabric_id, quantity, purpose, description=''):
    """مصرف پارچه از انبار"""
    db = SessionLocal()
    try:
        fabric = db.query(Fabric).filter_by(id=fabric_id).first()
        if not fabric:
            return None, 'پارچه پیدا نشد'

        if fabric.current_stock < quantity:
            return None, f'موجودی پارچه کافی نیست. موجودی فعلی: {fabric.current_stock}'

        # ثبت تراکنش مصرف
        transaction = FabricTransaction(
            fabric_id=fabric.id,
            transaction_type='OUT',
            quantity=quantity,
            purpose=purpose,
            description=description,
            date=datetime.now()
        )
        db.add(transaction)

        # به‌روزرسانی موجودی
        fabric.current_stock -= quantity

        db.commit()
        return fabric, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در مصرف پارچه: {str(e)}'
    finally:
        db.close()


def get_all_fabrics():
    """دریافت همه پارچه‌ها"""
    db = SessionLocal()
    try:
        return db.query(Fabric).all()
    finally:
        db.close()


def get_fabric_transactions(fabric_id=None):
    """دریافت تراکنش‌های پارچه"""
    db = SessionLocal()
    try:
        query = db.query(FabricTransaction)
        if fabric_id:
            query = query.filter_by(fabric_id=fabric_id)
        return query.order_by(FabricTransaction.date.desc()).all()
    finally:
        db.close()


def get_total_fabric_stock():
    """محاسبه کل موجودی پارچه"""
    db = SessionLocal()
    try:
        fabrics = db.query(Fabric).all()
        total = sum(f.current_stock for f in fabrics)
        return total
    finally:
        db.close()


# ==================== PRODUCT SERVICES ====================

def add_product(name, length, width, consumer_part, quantity, description=''):
    """افزودن محصول به انبار"""
    db = SessionLocal()
    try:
        # بررسی وجود محصول
        product = db.query(Product).filter_by(
            name=name,
            length=length,
            width=width
        ).first()

        if not product:
            # ایجاد محصول جدید
            product = Product(
                name=name,
                length=length,
                width=width,
                consumer_part=consumer_part,
                current_stock=0
            )
            db.add(product)
            db.flush()

        # ثبت تراکنش
        transaction = ProductTransaction(
            product_id=product.id,
            transaction_type='IN',
            quantity=quantity,
            description=description,
            date=datetime.now()
        )
        db.add(transaction)

        # به‌روزرسانی موجودی
        product.current_stock += quantity

        db.commit()
        return product, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت محصول: {str(e)}'
    finally:
        db.close()


def get_all_products():
    """دریافت همه محصولات"""
    db = SessionLocal()
    try:
        return db.query(Product).all()
    finally:
        db.close()


def get_product_transactions(product_id=None):
    """دریافت تراکنش‌های محصول"""
    db = SessionLocal()
    try:
        query = db.query(ProductTransaction)
        if product_id:
            query = query.filter_by(product_id=product_id)
        return query.order_by(ProductTransaction.date.desc()).all()
    finally:
        db.close()


def get_total_product_stock():
    """محاسبه کل موجودی محصولات"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        total = sum(p.current_stock for p in products)
        return total
    finally:
        db.close()