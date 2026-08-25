from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from datetime import datetime
from services.accounting_service import add_personal_debt, get_all_personal_debts
from utils.validators import validate_required, validate_positive_number
from utils.formatters import format_currency
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class PersonalAccountingScreen(Screen):
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
            text=reshape_text('حسابداری شخصی'),
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
            text=reshape_text('ثبت بدهی/طلب'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        add_button.bind(on_press=self.show_add_form)
        tab_layout.add_widget(add_button)

        list_button = Button(
            text=reshape_text('مشاهده لیست'),
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

        self.debt_inputs = {}
        self.debt_type = 'RECEIVABLE'

        # نام شخص
        name_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(75)
        )
        name_label = Label(
            text=reshape_text('نام شخص'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        name_layout.add_widget(name_label)
        name_input = TextInput(
            hint_text=reshape_text('نام شخص'),
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(50),
            halign='right',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        name_layout.add_widget(name_input)
        self.debt_inputs['person_name'] = name_input
        form_layout.add_widget(name_layout)

        # نوع
        type_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(75)
        )
        type_label = Label(
            text=reshape_text('نوع'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        type_layout.add_widget(type_label)

        type_buttons = BoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(50)
        )

        debt_button = Button(
            text=reshape_text('بدهی'),
            font_name=FONT_NAME,
            font_size=dp(12)
        )
        debt_button.bind(on_press=lambda x: self.set_debt_type('DEBT', debt_button, receivable_button))
        type_buttons.add_widget(debt_button)

        receivable_button = Button(
            text=reshape_text('طلب'),
            font_name=FONT_NAME,
            font_size=dp(12)
        )
        receivable_button.bind(on_press=lambda x: self.set_debt_type('RECEIVABLE', receivable_button, debt_button))
        type_buttons.add_widget(receivable_button)

        type_layout.add_widget(type_buttons)
        form_layout.add_widget(type_layout)

        # مبلغ
        amount_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(75)
        )
        amount_label = Label(
            text=reshape_text('مبلغ (تومان)'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        amount_layout.add_widget(amount_label)
        amount_input = TextInput(
            hint_text=reshape_text('مبلغ'),
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(50),
            halign='right',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        amount_layout.add_widget(amount_input)
        self.debt_inputs['total_amount'] = amount_input
        form_layout.add_widget(amount_layout)

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
            color=(0.2, 0.2, 0.3, 1),
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
        self.debt_inputs['description'] = desc_input
        form_layout.add_widget(desc_layout)

        save_button = Button(
            text=reshape_text('ثبت'),
            font_name=FONT_NAME,
            font_size=dp(16),
            background_color=(0.1, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        save_button.bind(on_press=self.save_debt)
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

    def set_debt_type(self, debt_type, active_button, inactive_button):
        self.debt_type = debt_type
        active_button.background_color = (0.1, 0.4, 0.8, 1)
        inactive_button.background_color = (0.7, 0.7, 0.7, 1)

    def show_list(self, instance=None):
        self.content_layout.clear_widgets()

        debts = get_all_personal_debts()

        if not debts:
            empty_label = Label(
                text=reshape_text('هنوز بدهی یا طلبی ثبت نشده است'),
                font_name=FONT_NAME,
                font_size=dp(16),
                color=(0.4, 0.4, 0.5, 1)
            )
            self.content_layout.add_widget(empty_label)
            return

        debt_list = [d for d in debts if d['debt_type'] == 'DEBT']
        receivable_list = [d for d in debts if d['debt_type'] == 'RECEIVABLE']

        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        if debt_list:
            debt_title = Label(
                text=reshape_text('بدهی‌های من'),
                font_name=FONT_NAME,
                font_size=dp(16),
                bold=True,
                color=(0.8, 0.2, 0.2, 1),
                halign='right',
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(debt_title)

            for debt in debt_list:
                remaining = debt['total_amount'] - debt['paid_amount']
                debt_label = Label(
                    text=reshape_text(f'• {debt["person_name"]}: {format_currency(remaining)}'),
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    halign='right',
                    size_hint_y=None,
                    height=dp(30)
                )
                content.add_widget(debt_label)

        if receivable_list:
            receivable_title = Label(
                text=reshape_text('طلب‌های من'),
                font_name=FONT_NAME,
                font_size=dp(16),
                bold=True,
                color=(0.1, 0.6, 0.3, 1),
                halign='right',
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(receivable_title)

            for debt in receivable_list:
                remaining = debt['total_amount'] - debt['paid_amount']
                debt_label = Label(
                    text=reshape_text(f'• {debt["person_name"]}: {format_currency(remaining)}'),
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    halign='right',
                    size_hint_y=None,
                    height=dp(30)
                )
                content.add_widget(debt_label)

        scroll.add_widget(content)
        self.content_layout.add_widget(scroll)

    def save_debt(self, instance):
        person_name = self.debt_inputs['person_name'].text.strip()
        total_amount = self.debt_inputs['total_amount'].text.strip()
        description = self.debt_inputs['description'].text.strip()

        valid, error = validate_required(person_name, 'نام شخص')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(total_amount, 'مبلغ')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        debt, error = add_personal_debt(
            person_name=person_name,
            debt_type=self.debt_type,
            total_amount=float(total_amount),
            due_date=None,
            description=description
        )

        if error:
            self.show_message(reshape_text(error), is_error=True)
        else:
            self.show_message(reshape_text('با موفقیت ثبت شد'), is_error=False)
            for input_field in self.debt_inputs.values():
                input_field.text = ''

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'