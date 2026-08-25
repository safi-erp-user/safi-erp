from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from services.calculation_service import calculate_total_consumption, calculate_circle_circumference, \
    calculate_circle_area
from utils.validators import validate_positive_number, validate_positive_integer
from utils.formatters import format_float
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class CalculatorScreen(Screen):
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
            text=reshape_text('ماشین حساب صافی'),
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

        self.inputs = {}

        fields = [
            ('length', 'طول (سانتی‌متر)'),
            ('width', 'عرض (سانتی‌متر)'),
            ('diameter', 'قطر (سانتی‌متر)'),
            ('seam_allowance', 'اضافه دوخت (سانتی‌متر)'),
            ('quantity', 'تعداد'),
            ('waste_percentage', 'درصد پرت'),
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

            self.inputs[key] = input_field
            form_layout.add_widget(field_layout)

        calculate_button = Button(
            text=reshape_text('محاسبه'),
            font_name=FONT_NAME,
            font_size=dp(17),
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        calculate_button.bind(on_press=self.calculate)
        form_layout.add_widget(calculate_button)

        self.results_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(200),
            halign='right',
            valign='top'
        )
        form_layout.add_widget(self.results_label)

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

    def calculate(self, instance):
        try:
            length = float(self.inputs['length'].text or 0)
            width = float(self.inputs['width'].text or 0)
            diameter = float(self.inputs['diameter'].text or 0)
            seam_allowance = float(self.inputs['seam_allowance'].text or 5)
            quantity = int(self.inputs['quantity'].text or 0)
            waste_percentage = float(self.inputs['waste_percentage'].text or 0)

            if diameter <= 0:
                self.show_error(reshape_text('قطر باید بزرگتر از صفر باشد'))
                return

            if quantity <= 0:
                self.show_error(reshape_text('تعداد باید بزرگتر از صفر باشد'))
                return

            circumference = calculate_circle_circumference(diameter)
            area = calculate_circle_area(diameter)

            total_consumption, single_consumption = calculate_total_consumption(
                length, width, diameter, seam_allowance, quantity, waste_percentage
            )

            results = f'''
{reshape_text("محاسبات صافی:")}

{reshape_text("قطر:")} {format_float(diameter)} {reshape_text("سانتی‌متر")}
{reshape_text("محیط:")} {format_float(circumference)} {reshape_text("سانتی‌متر")}
{reshape_text("مساحت:")} {format_float(area)} {reshape_text("سانتی‌متر مربع")}

{reshape_text("مصرف پارچه برای یک صافی:")}
{format_float(single_consumption)} {reshape_text("سانتی‌متر")}

{reshape_text("مصرف کل برای")} {quantity} {reshape_text("عدد:")}
{format_float(total_consumption / 100)} {reshape_text("متر")}

{reshape_text("درصد پرت:")} {format_float(waste_percentage)}٪
'''

            self.results_label.text = results

        except Exception as e:
            self.show_error(reshape_text(f'خطا در محاسبه: {str(e)}'))

    def show_error(self, message):
        self.results_label.text = message

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'