from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from database.database import SessionLocal
from database.models import Contract, Fabric
from services.production_service import register_production
from services.calculation_service import calculate_total_consumption
from utils.validators import validate_required, validate_positive_integer
from utils.formatters import format_number, format_currency
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class ProductionScreen(Screen):
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
            text=reshape_text('ثبت تولید'),
            font_name=FONT_NAME,
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=0.08,
            halign='right'
        )
        main_layout.add_widget(title_label)

        scroll = ScrollView()
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(5)
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # انتخاب قرارداد
        contract_label = Label(
            text=reshape_text('انتخاب قرارداد'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        form_layout.add_widget(contract_label)

        db = SessionLocal()
        try:
            contracts = db.query(Contract).all()
            contract_names = [f'{c.filter_name} - {c.company_name or "بدون شرکت"}' for c in contracts]
            self.contracts = contracts
        finally:
            db.close()

        self.contract_spinner = Spinner(
            text=reshape_text('انتخاب قرارداد...'),
            font_name=FONT_NAME,
            values=contract_names or [reshape_text('بدون قرارداد')],
            size_hint_y=None,
            height=dp(50)
        )
        form_layout.add_widget(self.contract_spinner)

        # انتخاب پارچه
        fabric_label = Label(
            text=reshape_text('انتخاب پارچه'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        form_layout.add_widget(fabric_label)

        db = SessionLocal()
        try:
            fabrics = db.query(Fabric).all()
            fabric_names = [f'{f.name} - {format_number(f.width)}cm - {format_number(f.current_stock)}m' for f in
                            fabrics]
            self.fabrics = fabrics
        finally:
            db.close()

        self.fabric_spinner = Spinner(
            text=reshape_text('انتخاب پارچه...'),
            font_name=FONT_NAME,
            values=fabric_names or [reshape_text('بدون پارچه')],
            size_hint_y=None,
            height=dp(50)
        )
        form_layout.add_widget(self.fabric_spinner)

        # تعداد تولید
        quantity_label = Label(
            text=reshape_text('تعداد تولید'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        form_layout.add_widget(quantity_label)

        self.quantity_input = TextInput(
            hint_text=reshape_text('مثلاً: 60'),
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(50),
            halign='right',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        form_layout.add_widget(self.quantity_input)

        # اضافه دوخت
        seam_label = Label(
            text=reshape_text('اضافه دوخت (سانتی‌متر)'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        form_layout.add_widget(seam_label)

        self.seam_input = TextInput(
            text='5',
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(50),
            halign='right',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        form_layout.add_widget(self.seam_input)

        # درصد پرت
        waste_label = Label(
            text=reshape_text('درصد پرت'),
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.2, 0.2, 0.3, 1),
            halign='right',
            size_hint_y=None,
            height=dp(25)
        )
        form_layout.add_widget(waste_label)

        self.waste_input = TextInput(
            text='5',
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(50),
            halign='right',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        form_layout.add_widget(self.waste_input)

        # دکمه ثبت تولید
        production_button = Button(
            text=reshape_text('ثبت تولید'),
            font_name=FONT_NAME,
            font_size=dp(17),
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        production_button.bind(on_press=self.register_production)
        form_layout.add_widget(production_button)

        # پیام
        self.message_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        form_layout.add_widget(self.message_label)

        scroll.add_widget(form_layout)
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

    def register_production(self, instance):
        if not self.contract_spinner.text or self.contract_spinner.text == reshape_text('انتخاب قرارداد...'):
            self.show_message(reshape_text('لطفاً قرارداد را انتخاب کنید'), is_error=True)
            return

        if not self.fabric_spinner.text or self.fabric_spinner.text == reshape_text('انتخاب پارچه...'):
            self.show_message(reshape_text('لطفاً پارچه را انتخاب کنید'), is_error=True)
            return

        quantity = self.quantity_input.text.strip()
        seam_allowance = self.seam_input.text.strip()
        waste_percentage = self.waste_input.text.strip()

        valid, error = validate_positive_integer(quantity, 'تعداد')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        try:
            contract_index = self.contract_spinner.values.index(self.contract_spinner.text)
            fabric_index = self.fabric_spinner.values.index(self.fabric_spinner.text)

            contract = self.contracts[contract_index]
            fabric = self.fabrics[fabric_index]

            seam = float(seam_allowance) if seam_allowance else 5
            waste = float(waste_percentage) if waste_percentage else 5

            production, error = register_production(
                product_name=contract.filter_name,
                contract_id=contract.id,
                quantity=int(quantity),
                fabric_id=fabric.id,
                fabric_consumption_per_unit=contract.width or 0,
                seam_allowance=seam,
                waste_percentage=waste
            )

            if error:
                self.show_message(reshape_text(error), is_error=True)
            else:
                self.show_message(reshape_text('تولید با موفقیت ثبت شد'), is_error=False)
                self.quantity_input.text = ''

        except Exception as e:
            self.show_message(reshape_text(f'خطا در ثبت تولید: {str(e)}'), is_error=True)

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'