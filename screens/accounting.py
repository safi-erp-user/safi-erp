from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from datetime import datetime
from services.accounting_service import (
    get_current_period, get_all_periods, settle_current_period,
    calculate_contract_income, get_today_income, get_settlement_history
)
from database.database import SessionLocal
from database.models import Contract
from utils.formatters import format_currency, to_persian_datetime
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class AccountingScreen(Screen):
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
            text=reshape_text('حسابداری تولید'),
            font_name=FONT_NAME,
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=0.08,
            halign='right'
        )
        main_layout.add_widget(title_label)

        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(5)
        )
        content.bind(minimum_height=content.setter('height'))

        # دوره جاری
        current_period = get_current_period()
        if current_period:
            period_layout = BoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(150)
            )

            period_title = Label(
                text=reshape_text(f'دوره مالی شماره {current_period["period_number"]}'),
                font_name=FONT_NAME,
                font_size=dp(16),
                bold=True,
                color=(0.1, 0.2, 0.4, 1),
                halign='right',
                size_hint_y=None,
                height=dp(30)
            )
            period_layout.add_widget(period_title)

            income_label = Label(
                text=reshape_text(f'درآمد دوره: {format_currency(current_period["total_income"])}'),
                font_name=FONT_NAME,
                font_size=dp(14),
                halign='right',
                size_hint_y=None,
                height=dp(25)
            )
            period_layout.add_widget(income_label)

            if current_period["settlement_limit"]:
                remaining = current_period["settlement_limit"] - current_period["total_income"]
                remaining_label = Label(
                    text=reshape_text(f'مانده تا سقف تسویه: {format_currency(remaining)}'),
                    font_name=FONT_NAME,
                    font_size=dp(14),
                    halign='right',
                    size_hint_y=None,
                    height=dp(25)
                )
                period_layout.add_widget(remaining_label)

                if remaining <= 0:
                    warning_label = Label(
                        text=reshape_text('⚠️ مبلغ دوره به سقف تسویه رسیده است'),
                        font_name=FONT_NAME,
                        font_size=dp(14),
                        color=(1, 0.5, 0, 1),
                        halign='right',
                        size_hint_y=None,
                        height=dp(30)
                    )
                    period_layout.add_widget(warning_label)

            content.add_widget(period_layout)

            if current_period["total_income"] > 0:
                settle_button = Button(
                    text=reshape_text('ثبت تسویه دوره'),
                    font_name=FONT_NAME,
                    font_size=dp(16),
                    background_color=(0.9, 0.5, 0.2, 1),
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=dp(50)
                )
                settle_button.bind(on_press=self.settle_period)
                content.add_widget(settle_button)

        # درآمد امروز
        today_income = get_today_income()
        today_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(80)
        )

        today_title = Label(
            text=reshape_text('درآمد امروز'),
            font_name=FONT_NAME,
            font_size=dp(14),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        today_layout.add_widget(today_title)

        today_value = Label(
            text=reshape_text(format_currency(today_income)),
            font_name=FONT_NAME,
            font_size=dp(16),
            halign='right',
            size_hint_y=None,
            height=dp(30)
        )
        today_layout.add_widget(today_value)

        content.add_widget(today_layout)

        # درآمد قراردادها
        contracts_title = Label(
            text=reshape_text('درآمد قراردادها'),
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(contracts_title)

        db = SessionLocal()
        try:
            contracts = db.query(Contract).all()
            for contract in contracts:
                income = calculate_contract_income(contract.id)
                contract_layout = BoxLayout(
                    orientation='vertical',
                    padding=dp(10),
                    spacing=dp(3),
                    size_hint_y=None,
                    height=dp(70)
                )

                contract_name = Label(
                    text=reshape_text(f'صافی: {contract.filter_name}'),
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    halign='right',
                    size_hint_y=None,
                    height=dp(25)
                )
                contract_layout.add_widget(contract_name)

                contract_income = Label(
                    text=reshape_text(f'درآمد: {format_currency(income)}'),
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    halign='right',
                    size_hint_y=None,
                    height=dp(25)
                )
                contract_layout.add_widget(contract_income)

                content.add_widget(contract_layout)
        finally:
            db.close()

        # تاریخچه تسویه‌ها
        settlements_title = Label(
            text=reshape_text('تاریخچه تسویه‌ها'),
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(settlements_title)

        settlements = get_settlement_history()
        if settlements:
            for settlement in settlements[:5]:
                settlement_label = Label(
                    text=reshape_text(
                        f'• {format_currency(settlement["amount"])} - {to_persian_datetime(settlement["settlement_date"])}'),
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    halign='right',
                    size_hint_y=None,
                    height=dp(30)
                )
                content.add_widget(settlement_label)
        else:
            no_settlement_label = Label(
                text=reshape_text('هنوز تسویه‌ای ثبت نشده است'),
                font_name=FONT_NAME,
                font_size=dp(13),
                halign='right',
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(no_settlement_label)

        # پیام
        self.message_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(self.message_label)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

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

    def settle_period(self, instance):
        settlement, error = settle_current_period()

        if error:
            self.show_message(reshape_text(error), is_error=True)
        else:
            self.show_message(reshape_text('تسویه دوره با موفقیت ثبت شد'), is_error=False)
            self.build_ui()

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'