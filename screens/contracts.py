from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from datetime import datetime
from database.database import SessionLocal
from database.models import Contract
from utils.validators import validate_required, validate_positive_number, validate_positive_integer
from utils.formatters import format_number, format_currency
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class ContractsScreen(Screen):
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
            text=reshape_text('قراردادها'),
            font_name=FONT_NAME,
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=0.08,
            halign='right'
        )
        main_layout.add_widget(title_label)

        tab_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.08,
            spacing=dp(5)
        )

        add_button = Button(
            text=reshape_text('ثبت قرارداد'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        add_button.bind(on_press=self.show_add_form)
        tab_layout.add_widget(add_button)

        list_button = Button(
            text=reshape_text('مشاهده قراردادها'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        list_button.bind(on_press=self.show_list)
        tab_layout.add_widget(list_button)

        main_layout.add_widget(tab_layout)

        self.content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        main_layout.add_widget(self.content_layout)

        self.show_list()

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

    def show_add_form(self, instance=None):
        self.content_layout.clear_widgets()

        form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))

        self.contract_inputs = {}

        fields = [
            ('filter_name', 'نام صافی'),
            ('length', 'طول (سانتی‌متر)'),
            ('width', 'عرض (سانتی‌متر)'),
            ('company_name', 'نام شرکت کارفرما'),
            ('quantity', 'تعداد قرارداد'),
            ('price_per_unit', 'قیمت هر صافی (تومان)'),
            ('settlement_limit', 'مبلغ سقف تسویه (تومان)'),
        ]

        for key, label_text in fields:
            field_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(5),
                size_hint_y=None,
                height=dp(75)
            )

            label = Label(
                text=reshape_text(label_text),
                font_name=FONT_NAME,
                font_size=dp(14),
                color=(0.2, 0.2, 0.3, 1),
                halign='right',
                size_hint_y=None,
                height=dp(25)
            )
            field_layout.add_widget(label)

            input_field = TextInput(
                hint_text=reshape_text(label_text),
                font_name=FONT_NAME,
                multiline=False,
                font_size=dp(15),
                size_hint_y=None,
                height=dp(50),
                halign='right',
                background_color=(1, 1, 1, 1),
                foreground_color=(0.1, 0.1, 0.1, 1)
            )
            field_layout.add_widget(input_field)

            self.contract_inputs[key] = input_field
            form_layout.add_widget(field_layout)

        # توضیحات
        desc_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(100)
        )
        desc_label = Label(
            text=reshape_text('توضیحات'),
            font_name=FONT_NAME,
            font_size=dp(14),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        desc_layout.add_widget(desc_label)

        desc_input = TextInput(
            hint_text=reshape_text('توضیحات اضافی'),
            font_name=FONT_NAME,
            multiline=True,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(75)
        )
        desc_layout.add_widget(desc_input)
        self.contract_inputs['description'] = desc_input
        form_layout.add_widget(desc_layout)

        save_button = Button(
            text=reshape_text('ثبت قرارداد'),
            font_name=FONT_NAME,
            font_size=dp(16),
            background_color=(0.1, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        save_button.bind(on_press=self.save_contract)
        form_layout.add_widget(save_button)

        self.message_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )
        form_layout.add_widget(self.message_label)

        scroll = ScrollView()
        scroll.add_widget(form_layout)
        self.content_layout.add_widget(scroll)

    def show_list(self, instance=None):
        self.content_layout.clear_widgets()

        db = SessionLocal()
        try:
            contracts = db.query(Contract).order_by(Contract.created_at.desc()).all()
        finally:
            db.close()

        if not contracts:
            empty_label = Label(
                text=reshape_text('هنوز قراردادی ثبت نشده است'),
                font_name=FONT_NAME,
                font_size=dp(16),
                color=(0.4, 0.4, 0.5, 1)
            )
            self.content_layout.add_widget(empty_label)
            return

        scroll = ScrollView()
        contracts_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        contracts_layout.bind(minimum_height=contracts_layout.setter('height'))

        for contract in contracts:
            card = BoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(120)
            )

            name_label = Label(
                text=reshape_text(f'صافی: {contract.filter_name}'),
                font_name=FONT_NAME,
                font_size=dp(14),
                bold=True,
                color=(0.1, 0.2, 0.4, 1),
                halign='right',
                size_hint_y=None,
                height=dp(30)
            )
            card.add_widget(name_label)

            company_label = Label(
                text=reshape_text(f'شرکت: {contract.company_name or "-"}'),
                font_name=FONT_NAME,
                font_size=dp(12),
                halign='right',
                size_hint_y=None,
                height=dp(25)
            )
            card.add_widget(company_label)

            quantity_label = Label(
                text=reshape_text(f'تعداد: {format_number(contract.quantity)} عدد'),
                font_name=FONT_NAME,
                font_size=dp(12),
                halign='right',
                size_hint_y=None,
                height=dp(25)
            )
            card.add_widget(quantity_label)

            price_label = Label(
                text=reshape_text(f'قیمت: {format_currency(contract.price_per_unit)}'),
                font_name=FONT_NAME,
                font_size=dp(12),
                halign='right',
                size_hint_y=None,
                height=dp(25)
            )
            card.add_widget(price_label)

            contracts_layout.add_widget(card)

        scroll.add_widget(contracts_layout)
        self.content_layout.add_widget(scroll)

    def save_contract(self, instance):
        filter_name = self.contract_inputs['filter_name'].text.strip()
        length = self.contract_inputs['length'].text.strip()
        width = self.contract_inputs['width'].text.strip()
        company_name = self.contract_inputs['company_name'].text.strip()
        quantity = self.contract_inputs['quantity'].text.strip()
        price_per_unit = self.contract_inputs['price_per_unit'].text.strip()
        settlement_limit = self.contract_inputs['settlement_limit'].text.strip()
        description = self.contract_inputs['description'].text.strip()

        valid, error = validate_required(filter_name, 'نام صافی')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(length, 'طول')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(width, 'عرض')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_integer(quantity, 'تعداد')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(price_per_unit, 'قیمت')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(settlement_limit, 'سقف تسویه')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        db = SessionLocal()
        try:
            contract = Contract(
                filter_name=filter_name,
                length=float(length),
                width=float(width),
                company_name=company_name,
                quantity=int(quantity),
                price_per_unit=float(price_per_unit),
                settlement_limit=float(settlement_limit),
                description=description,
                start_date=datetime.now(),
                end_date=datetime.now()
            )

            db.add(contract)
            db.commit()

            self.show_message(reshape_text('قرارداد با موفقیت ثبت شد'), is_error=False)
            for input_field in self.contract_inputs.values():
                input_field.text = ''

        except Exception as e:
            db.rollback()
            self.show_message(reshape_text(f'خطا در ثبت قرارداد: {str(e)}'), is_error=True)
        finally:
            db.close()

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'