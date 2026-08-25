from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from datetime import datetime
from database.database import SessionLocal
from database.models import Fabric, Product, Production, Contract
from services.accounting_service import get_current_period, get_all_periods, get_all_personal_debts
from utils.formatters import format_number, format_currency, to_persian_datetime
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        with self.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )

        title_label = Label(
            text=reshape_text('گزارش‌ها'),
            font_name=FONT_NAME,
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=0.08,
            halign='right'
        )
        main_layout.add_widget(title_label)

        report_buttons = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=0.4
        )

        buttons = [
            ('گزارش موجودی پارچه', self.show_fabric_report),
            ('گزارش موجودی محصول', self.show_product_report),
            ('گزارش تولید', self.show_production_report),
            ('گزارش قراردادها', self.show_contract_report),
            ('گزارش مالی', self.show_financial_report),
            ('گزارش بدهی و طلب', self.show_debt_report),
        ]

        for text, callback in buttons:
            btn = Button(
                text=reshape_text(text),
                font_name=FONT_NAME,
                font_size=dp(13),
                size_hint_y=None,
                height=dp(42)
            )
            btn.bind(on_press=callback)
            report_buttons.add_widget(btn)

        main_layout.add_widget(report_buttons)

        self.report_content = ScrollView()
        self.report_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.report_layout.bind(minimum_height=self.report_layout.setter('height'))
        self.report_content.add_widget(self.report_layout)
        main_layout.add_widget(self.report_content)

        back_button = Button(
            text=reshape_text('بازگشت به داشبورد'),
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=0.08
        )
        back_button.bind(on_press=lambda x: self.go_to_dashboard())
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def clear_report(self):
        self.report_layout.clear_widgets()

    def add_report_line(self, text, is_header=False, is_bold=False):
        label = Label(
            text=reshape_text(text),
            font_name=FONT_NAME,
            font_size=dp(15) if is_header else dp(13),
            bold=is_header or is_bold,
            color=(0.1, 0.2, 0.4, 1) if is_header else (0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(35) if is_header else dp(30)
        )
        self.report_layout.add_widget(label)

    def show_fabric_report(self, instance=None):
        self.clear_report()
        self.add_report_line('📊 گزارش موجودی پارچه', is_header=True)

        db = SessionLocal()
        try:
            fabrics = db.query(Fabric).all()
            total_stock = sum(f.current_stock for f in fabrics)

            self.add_report_line(f'کل موجودی: {format_number(total_stock)} متر', is_bold=True)
            self.add_report_line('')

            for fabric in fabrics:
                self.add_report_line(
                    f'• {fabric.name} (عرض {format_number(fabric.width)}): {format_number(fabric.current_stock)} متر'
                )
        finally:
            db.close()

    def show_product_report(self, instance=None):
        self.clear_report()
        self.add_report_line('📦 گزارش موجودی محصول', is_header=True)

        db = SessionLocal()
        try:
            products = db.query(Product).all()
            total_stock = sum(p.current_stock for p in products)

            self.add_report_line(f'کل موجودی: {format_number(total_stock)} عدد', is_bold=True)
            self.add_report_line('')

            for product in products:
                self.add_report_line(
                    f'• {product.name}: {format_number(product.current_stock)} عدد'
                )
        finally:
            db.close()

    def show_production_report(self, instance=None):
        self.clear_report()
        self.add_report_line('🏭 گزارش تولید', is_header=True)

        db = SessionLocal()
        try:
            productions = db.query(Production).order_by(Production.production_date.desc()).limit(20).all()

            total_produced = sum(p.quantity for p in productions)
            self.add_report_line(f'کل تولید (۲۰ مورد آخر): {format_number(total_produced)} عدد', is_bold=True)
            self.add_report_line('')

            for prod in productions:
                self.add_report_line(
                    f'• {to_persian_datetime(prod.production_date)}: {prod.product_name} - {format_number(prod.quantity)} عدد'
                )
        finally:
            db.close()

    def show_contract_report(self, instance=None):
        self.clear_report()
        self.add_report_line('📑 گزارش قراردادها', is_header=True)

        db = SessionLocal()
        try:
            contracts = db.query(Contract).all()

            self.add_report_line(f'تعداد قراردادها: {len(contracts)}', is_bold=True)
            self.add_report_line('')

            for contract in contracts:
                self.add_report_line(f'• {contract.filter_name} - {contract.company_name or "بدون شرکت"}')
                self.add_report_line(
                    f'  تعداد: {format_number(contract.quantity)} - قیمت: {format_currency(contract.price_per_unit)}')
                self.add_report_line('')
        finally:
            db.close()

    def show_financial_report(self, instance=None):
        self.clear_report()
        self.add_report_line('💰 گزارش مالی', is_header=True)

        current_period = get_current_period()
        if current_period:
            self.add_report_line(f'دوره جاری: شماره {current_period["period_number"]}', is_bold=True)
            self.add_report_line(f'درآمد دوره: {format_currency(current_period["total_income"])}')
            if current_period["settlement_limit"]:
                remaining = current_period["settlement_limit"] - current_period["total_income"]
                self.add_report_line(f'مانده تا سقف: {format_currency(remaining)}')
            self.add_report_line('')

        periods = get_all_periods()
        if periods:
            self.add_report_line('دوره‌های قبلی:', is_bold=True)
            for period in periods:
                if period['is_closed']:
                    self.add_report_line(
                        f'• دوره {period["period_number"]}: {format_currency(period["total_income"])} - بسته شده'
                    )

    def show_debt_report(self, instance=None):
        self.clear_report()
        self.add_report_line('💳 گزارش بدهی و طلب', is_header=True)

        debts = get_all_personal_debts()

        debt_list = [d for d in debts if d['debt_type'] == 'DEBT']
        receivable_list = [d for d in debts if d['debt_type'] == 'RECEIVABLE']

        total_debt = sum(d['total_amount'] - d['paid_amount'] for d in debt_list)
        total_receivable = sum(d['total_amount'] - d['paid_amount'] for d in receivable_list)

        self.add_report_line(f'کل بدهی: {format_currency(total_debt)}', is_bold=True)
        self.add_report_line(f'کل طلب: {format_currency(total_receivable)}', is_bold=True)
        self.add_report_line('')

        if debt_list:
            self.add_report_line('بدهی‌ها:', is_bold=True)
            for debt in debt_list:
                remaining = debt['total_amount'] - debt['paid_amount']
                self.add_report_line(f'• {debt["person_name"]}: {format_currency(remaining)}')

        if receivable_list:
            self.add_report_line('طلب‌ها:', is_bold=True)
            for debt in receivable_list:
                remaining = debt['total_amount'] - debt['paid_amount']
                self.add_report_line(f'• {debt["person_name"]}: {format_currency(remaining)}')

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'