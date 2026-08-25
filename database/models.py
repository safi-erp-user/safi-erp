from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default='USER')  # ADMIN, USER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)


class Fabric(Base):
    __tablename__ = 'fabrics'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)  # نوع پارچه
    width = Column(Float, nullable=False)  # عرض پارچه
    current_stock = Column(Float, default=0)  # موجودی فعلی
    created_at = Column(DateTime, default=datetime.now)


class FabricTransaction(Base):
    __tablename__ = 'fabric_transactions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    fabric_id = Column(String(36), ForeignKey('fabrics.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # IN, OUT, RETURN, ADJUST
    quantity = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.now)
    supplier = Column(String(100))  # تحویل‌دهنده
    receiver = Column(String(100))  # تحویل‌گیرنده
    purpose = Column(String(200))  # مورد مصرف
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    fabric = relationship('Fabric', backref='transactions')


class Product(Base):
    __tablename__ = 'products'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)  # نام صافی
    length = Column(Float)  # طول
    width = Column(Float)  # عرض
    consumer_part = Column(String(100))  # قسمت مصرف‌کننده
    current_stock = Column(Integer, default=0)  # موجودی فعلی
    created_at = Column(DateTime, default=datetime.now)


class ProductTransaction(Base):
    __tablename__ = 'product_transactions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # IN, OUT
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.now)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    product = relationship('Product', backref='transactions')


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filter_name = Column(String(100), nullable=False)  # نام صافی
    length = Column(Float)  # طول
    width = Column(Float)  # عرض
    company_name = Column(String(100))  # نام شرکت کارفرما
    start_date = Column(DateTime)  # تاریخ قرارداد
    end_date = Column(DateTime)  # تاریخ پایان
    quantity = Column(Integer)  # تعداد قرارداد
    price_per_unit = Column(Float)  # قیمت هر صافی
    settlement_limit = Column(Float)  # مبلغ سقف تسویه
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Production(Base):
    __tablename__ = 'productions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_name = Column(String(100), nullable=False)  # نام صافی
    contract_id = Column(String(36), ForeignKey('contracts.id'))
    quantity = Column(Integer, nullable=False)  # تعداد تولید
    fabric_consumed = Column(Float)  # پارچه مصرف شده
    production_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    contract = relationship('Contract', backref='productions')


class ProductionItem(Base):
    __tablename__ = 'production_items'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    production_id = Column(String(36), ForeignKey('productions.id'), nullable=False)
    fabric_id = Column(String(36), ForeignKey('fabrics.id'))
    quantity = Column(Float)  # مقدار پارچه مصرفی
    created_at = Column(DateTime, default=datetime.now)

    production = relationship('Production', backref='items')
    fabric = relationship('Fabric', backref='production_items')


class AccountingPeriod(Base):
    __tablename__ = 'accounting_periods'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    period_number = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    total_income = Column(Float, default=0)
    settlement_limit = Column(Float)  # سقف تسویه
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class Settlement(Base):
    __tablename__ = 'settlements'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    period_id = Column(String(36), ForeignKey('accounting_periods.id'), nullable=False)
    amount = Column(Float, nullable=False)
    settlement_date = Column(DateTime, default=datetime.now)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    period = relationship('AccountingPeriod', backref='settlements')


class PersonalDebt(Base):
    __tablename__ = 'personal_debts'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    person_name = Column(String(100), nullable=False)
    debt_type = Column(String(20), nullable=False)  # DEBT (بدهی), RECEIVABLE (طلب)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0)
    due_date = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Installment(Base):
    __tablename__ = 'installments'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    debt_id = Column(String(36), ForeignKey('personal_debts.id'), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    paid_date = Column(DateTime, nullable=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    debt = relationship('PersonalDebt', backref='installments')


class AppSetting(Base):
    __tablename__ = 'app_settings'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)