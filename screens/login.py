from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from services.auth_service import authenticate_user
from utils.validators import validate_username, validate_password
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main_layout = FloatLayout()

        card = BoxLayout(
            orientation='vertical',
            padding=dp(25),
            spacing=dp(15),
            size_hint=(None, None),
            size=(dp(350), dp(450)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[20])
        card.bind(pos=lambda *a: self._update_card_bg(card),
                  size=lambda *a: self._update_card_bg(card))

        logo_box = BoxLayout(
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            pos_hint={'center_x': 0.5}
        )
        with logo_box.canvas.before:
            Color(0.1, 0.4, 0.8, 1)
            RoundedRectangle(pos=logo_box.pos, size=logo_box.size, radius=[40])
        logo_box.bind(pos=lambda *a: self._update_logo_bg(logo_box),
                      size=lambda *a: self._update_logo_bg(logo_box))

        logo_label = Label(
            text='⚙',
            font_size=dp(40),
            color=(1, 1, 1, 1)
        )
        logo_box.add_widget(logo_label)
        card.add_widget(logo_box)

        title_label = Label(
            text=reshape_text('مدیریت تولید صافی'),
            font_name=FONT_NAME,
            font_size=dp(22),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        card.add_widget(title_label)

        subtitle_label = Label(
            text=reshape_text('ورود به حساب کاربری'),
            font_name=FONT_NAME,
            font_size=dp(15),
            color=(0.5, 0.5, 0.6, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        card.add_widget(subtitle_label)

        card.add_widget(Label(size_hint_y=None, height=dp(10)))

        username_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10),
            padding=[dp(15), dp(5)]
        )
        with username_box.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            RoundedRectangle(pos=username_box.pos, size=username_box.size, radius=[15])
        username_box.bind(pos=lambda *a: self._update_input_bg(username_box),
                          size=lambda *a: self._update_input_bg(username_box))

        user_icon = Label(
            text='👤',
            font_size=dp(20),
            size_hint_x=None,
            width=dp(30)
        )
        username_box.add_widget(user_icon)

        self.username_input = TextInput(
            hint_text=reshape_text('نام کاربری'),
            font_name=FONT_NAME,
            multiline=False,
            font_size=dp(15),
            background_color=(0, 0, 0, 0),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1),
            halign='right',
            write_tab=False
        )
        username_box.add_widget(self.username_input)
        card.add_widget(username_box)

        password_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10),
            padding=[dp(15), dp(5)]
        )
        with password_box.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            RoundedRectangle(pos=password_box.pos, size=password_box.size, radius=[15])
        password_box.bind(pos=lambda *a: self._update_input_bg(password_box),
                          size=lambda *a: self._update_input_bg(password_box))

        pass_icon = Label(
            text='🔒',
            font_size=dp(20),
            size_hint_x=None,
            width=dp(30)
        )
        password_box.add_widget(pass_icon)

        self.password_input = TextInput(
            hint_text=reshape_text('رمز عبور'),
            font_name=FONT_NAME,
            password=True,
            multiline=False,
            font_size=dp(15),
            background_color=(0, 0, 0, 0),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1),
            halign='right',
            write_tab=False,
            on_text_validate=self.login
        )
        password_box.add_widget(self.password_input)
        card.add_widget(password_box)

        self.username_input.focus_next = self.password_input

        card.add_widget(Label(size_hint_y=None, height=dp(5)))

        login_button = Button(
            text=reshape_text('ورود به سیستم'),
            font_name=FONT_NAME,
            font_size=dp(17),
            color=(1, 1, 1, 1),
            background_color=(0.1, 0.4, 0.8, 1),
            size_hint_y=None,
            height=dp(55)
        )
        login_button.bind(on_press=self.login)
        card.add_widget(login_button)

        self.error_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(13),
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(25),
            halign='center'
        )
        card.add_widget(self.error_label)

        main_layout.add_widget(card)
        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _update_card_bg(self, card):
        card.canvas.before.clear()
        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[20])

    def _update_logo_bg(self, logo_box):
        logo_box.canvas.before.clear()
        with logo_box.canvas.before:
            Color(0.1, 0.4, 0.8, 1)
            RoundedRectangle(pos=logo_box.pos, size=logo_box.size, radius=[40])

    def _update_input_bg(self, input_box):
        input_box.canvas.before.clear()
        with input_box.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            RoundedRectangle(pos=input_box.pos, size=input_box.size, radius=[15])

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text

        valid, error = validate_username(username)
        if not valid:
            self.show_error(error)
            return

        valid, error = validate_password(password)
        if not valid:
            self.show_error(error)
            return

        user, error = authenticate_user(username, password)

        if error:
            self.show_error(error)
            return

        self.current_user = user
        self.error_label.text = ''
        self.username_input.text = ''
        self.password_input.text = ''

        self.manager.current = 'dashboard'

    def show_error(self, message):
        self.error_label.text = reshape_text(message)
        Clock.schedule_once(lambda dt: self.clear_error(), 3)

    def clear_error(self):
        self.error_label.text = ''