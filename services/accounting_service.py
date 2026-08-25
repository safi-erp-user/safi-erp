from datetime import datetime
from database.database import SessionLocal
from database.models import (
    AccountingPeriod, Settlement, PersonalDebt, Installment,
    Production, Contract
)


# ==================== ACCOUNTING PERIOD SERVICES ====================

def get_current_period():
    """دریافت دوره مالی جاری"""
    db = SessionLocal()
    try:
        period = db.query(AccountingPeriod).filter_by(is_closed=False).first()
        if not period:
            # ایجاد دوره جدید
            period_number = db.query(AccountingPeriod).count() + 1
            period = AccountingPeriod(
                period_number=period_number,
                total_income=0,
                settlement_limit=20000000,  # پیش‌فرض ۲۰ میلیون
                is_closed=False,
                start_date=datetime.now()
            )
            db.add(period)
            db.commit()
            db.refresh(period)

        # کپی داده‌های لازم قبل از بستن session
        period_data = {
            'id': period.id,
            'period_number': period.period_number,
            'total_income': period.total_income,
            'settlement_limit': period.settlement_limit,
            'is_closed': period.is_closed,
            'start_date': period.start_date
        }
        return period_data
    finally:
        db.close()


def get_all_periods():
    """دریافت همه دوره‌های مالی"""
    db = SessionLocal()
    try:
        periods = db.query(AccountingPeriod).order_by(AccountingPeriod.period_number.desc()).all()
        result = []
        for period in periods:
            result.append({
                'id': period.id,
                'period_number': period.period_number,
                'total_income': period.total_income,
                'settlement_limit': period.settlement_limit,
                'is_closed': period.is_closed,
                'start_date': period.start_date,
                'end_date': period.end_date
            })
        return result
    finally:
        db.close()


def add_income_to_period(amount):
    """افزودن درآمد به دوره جاری"""
    db = SessionLocal()
    try:
        period = db.query(AccountingPeriod).filter_by(is_closed=False).first()
        if not period:
            period = AccountingPeriod(
                period_number=db.query(AccountingPeriod).count() + 1,
                total_income=0,
                settlement_limit=20000000,
                is_closed=False,
                start_date=datetime.now()
            )
            db.add(period)
            db.flush()

        period.total_income += amount
        db.commit()
        return {'id': period.id, 'total_income': period.total_income}, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت درآمد: {str(e)}'
    finally:
        db.close()


def settle_current_period(description=''):
    """تسویه دوره جاری"""
    db = SessionLocal()
    try:
        period = db.query(AccountingPeriod).filter_by(is_closed=False).first()

        if not period:
            return None, 'دوره فعالی وجود ندارد'

        if period.total_income <= 0:
            return None, 'درآمدی برای تسویه وجود ندارد'

        # ثبت تسویه
        settlement = Settlement(
            period_id=period.id,
            amount=period.total_income,
            settlement_date=datetime.now(),
            description=description
        )
        db.add(settlement)

        # بستن دوره
        period.is_closed = True
        period.end_date = datetime.now()

        # ایجاد دوره جدید
        new_period_number = period.period_number + 1
        new_period = AccountingPeriod(
            period_number=new_period_number,
            total_income=0,
            settlement_limit=period.settlement_limit,
            is_closed=False,
            start_date=datetime.now()
        )
        db.add(new_period)

        db.commit()
        return {'amount': settlement.amount, 'date': settlement.settlement_date}, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در تسویه دوره: {str(e)}'
    finally:
        db.close()


def get_settlement_history():
    """دریافت تاریخچه تسویه‌ها"""
    db = SessionLocal()
    try:
        settlements = db.query(Settlement).order_by(Settlement.settlement_date.desc()).all()
        result = []
        for settlement in settlements:
            result.append({
                'id': settlement.id,
                'amount': settlement.amount,
                'settlement_date': settlement.settlement_date,
                'description': settlement.description
            })
        return result
    finally:
        db.close()


# ==================== INCOME CALCULATION ====================

def calculate_contract_income(contract_id):
    """محاسبه درآمد یک قرارداد"""
    db = SessionLocal()
    try:
        contract = db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return 0

        # محاسبه تعداد تولید شده
        productions = db.query(Production).filter_by(contract_id=contract_id).all()
        total_produced = sum(p.quantity for p in productions)

        return total_produced * (contract.price_per_unit or 0)
    finally:
        db.close()


def get_total_income():
    """محاسبه کل درآمد"""
    db = SessionLocal()
    try:
        contracts = db.query(Contract).all()
        total = 0
        for contract in contracts:
            total += calculate_contract_income(contract.id)
        return total
    finally:
        db.close()


def get_today_income():
    """محاسبه درآمد امروز"""
    db = SessionLocal()
    try:
        today = datetime.now().date()
        start = datetime(today.year, today.month, today.day)
        end = datetime(today.year, today.month, today.day, 23, 59, 59)

        productions = db.query(Production).filter(
            Production.production_date >= start,
            Production.production_date <= end
        ).all()

        total = 0
        for prod in productions:
            if prod.contract:
                total += prod.quantity * (prod.contract.price_per_unit or 0)

        return total
    finally:
        db.close()


# ==================== PERSONAL ACCOUNTING ====================

def add_personal_debt(person_name, debt_type, total_amount, due_date=None, description=''):
    """افزودن بدهی یا طلب شخصی"""
    db = SessionLocal()
    try:
        debt = PersonalDebt(
            person_name=person_name,
            debt_type=debt_type,  # DEBT or RECEIVABLE
            total_amount=total_amount,
            paid_amount=0,
            due_date=due_date,
            description=description
        )
        db.add(debt)
        db.commit()
        db.refresh(debt)
        return {'id': debt.id, 'person_name': debt.person_name}, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت بدهی: {str(e)}'
    finally:
        db.close()


def get_all_personal_debts():
    """دریافت همه بدهی‌ها و طلب‌ها"""
    db = SessionLocal()
    try:
        debts = db.query(PersonalDebt).all()
        result = []
        for debt in debts:
            result.append({
                'id': debt.id,
                'person_name': debt.person_name,
                'debt_type': debt.debt_type,
                'total_amount': debt.total_amount,
                'paid_amount': debt.paid_amount,
                'due_date': debt.due_date,
                'description': debt.description
            })
        return result
    finally:
        db.close()


def add_installment(debt_id, amount, due_date, description=''):
    """افزودن قسط"""
    db = SessionLocal()
    try:
        installment = Installment(
            debt_id=debt_id,
            amount=amount,
            due_date=due_date,
            is_paid=False,
            description=description
        )
        db.add(installment)
        db.commit()
        return {'id': installment.id}, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در ثبت قسط: {str(e)}'
    finally:
        db.close()


def pay_installment(installment_id):
    """پرداخت قسط"""
    db = SessionLocal()
    try:
        installment = db.query(Installment).filter_by(id=installment_id).first()
        if not installment:
            return None, 'قسط پیدا نشد'

        installment.is_paid = True
        installment.paid_date = datetime.now()

        # به‌روزرسانی مبلغ پرداخت شده
        debt = db.query(PersonalDebt).filter_by(id=installment.debt_id).first()
        if debt:
            debt.paid_amount += installment.amount

        db.commit()
        return {'id': installment.id}, None
    except Exception as e:
        db.rollback()
        return None, f'خطا در پرداخت قسط: {str(e)}'
    finally:
        db.close()