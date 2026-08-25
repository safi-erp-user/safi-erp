from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from services.inventory_service import add_fabric, get_all_fabrics, get_fabric_transactions
from utils.validators import validate_required, validate_positive_number
from utils.formatters import format_number
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class FabricScreen(Screen):
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
            text=reshape_text('انبار پارچه'),
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
            text=reshape_text('ثبت ورود پارچه'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        add_button.bind(on_press=self.show_add_form)
        tab_layout.add_widget(add_button)

        list_button = Button(
            text=reshape_text('مشاهده موجودی'),
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

        self.fabric_inputs = {}

        fields = [
            ('name', 'نوع پارچه'),
            ('width', 'عرض پارچه (سانتی‌متر)'),
            ('quantity', 'متراژ'),
            ('supplier', 'تحویل‌دهنده'),
            ('receiver', 'تحویل‌گیرنده'),
            ('purpose', 'مورد مصرف'),
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

            self.fabric_inputs[key] = input_field
            form_layout.add_widget(field_layout)

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
        self.fabric_inputs['description'] = desc_input
        form_layout.add_widget(desc_layout)

        save_button = Button(
            text=reshape_text('ثبت پارچه'),
            font_name=FONT_NAME,
            font_size=dp(16),
            background_color=(0.1, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        save_button.bind(on_press=self.save_fabric)
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

        fabrics = get_all_fabrics()

        if not fabrics:
            empty_label = Label(
                text=reshape_text('هنوز پارچه‌ای ثبت نشده است'),
                font_name=FONT_NAME,
                font_size=dp(16),
                color=(0.4, 0.4, 0.5, 1)
            )
            self.content_layout.add_widget(empty_label)
            return

        scroll = ScrollView()
        table = GridLayout(
            cols=3,
            spacing=dp(5),
            size_hint_y=None
        )
        table.bind(minimum_height=table.setter('height'))

        headers = ['نوع پارچه', 'عرض', 'موجودی']
        for header in headers:
            table.add_widget(Label(
                text=reshape_text(header),
                font_name=FONT_NAME,
                font_size=dp(13),
                bold=True,
                color=(0.1, 0.2, 0.4, 1),
                size_hint_y=None,
                height=dp(40),
                halign='right'
            ))

        for fabric in fabrics:
            table.add_widget(Label(
                text=reshape_text(fabric.name),
                font_name=FONT_NAME,
                font_size=dp(13),
                size_hint_y=None,
                height=dp(35),
                halign='right'
            ))
            table.add_widget(Label(
                text=reshape_text(format_number(fabric.width)),
                font_name=FONT_NAME,
                font_size=dp(13),
                size_hint_y=None,
                height=dp(35),
                halign='right'
            ))
            table.add_widget(Label(
                text=reshape_text(f'{format_number(fabric.current_stock)} متر'),
                font_name=FONT_NAME,
                font_size=dp(13),
                size_hint_y=None,
                height=dp(35),
                halign='right'
            ))

        scroll.add_widget(table)
        self.content_layout.add_widget(scroll)

    def save_fabric(self, instance):
        name = self.fabric_inputs['name'].text.strip()
        width = self.fabric_inputs['width'].text.strip()
        quantity = self.fabric_inputs['quantity'].text.strip()
        supplier = self.fabric_inputs['supplier'].text.strip()
        receiver = self.fabric_inputs['receiver'].text.strip()
        purpose = self.fabric_inputs['purpose'].text.strip()
        description = self.fabric_inputs['description'].text.strip()

        valid, error = validate_required(name, 'نوع پارچه')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(width, 'عرض پارچه')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        valid, error = validate_positive_number(quantity, 'متراژ')
        if not valid:
            self.show_message(reshape_text(error), is_error=True)
            return

        fabric, error = add_fabric(
            name=name,
            width=float(width),
            quantity=float(quantity),
            supplier=supplier,
            receiver=receiver,
            purpose=purpose,
            description=description
        )

        if error:
            self.show_message(reshape_text(error), is_error=True)
        else:
            self.show_message(reshape_text('پارچه با موفقیت ثبت شد'), is_error=False)
            for input_field in self.fabric_inputs.values():
                input_field.text = ''

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'