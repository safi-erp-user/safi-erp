from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from database.database import SessionLocal
from database.models import AppSetting, User
from services.auth_service import create_user, get_all_users, update_user
from utils.validators import validate_required, validate_positive_number
from utils.persian_text import reshape_text

FONT_NAME = 'Persian'


class SettingsScreen(Screen):
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
            text=reshape_text('تنظیمات'),
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

        settings_button = Button(
            text=reshape_text('تنظیمات'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        settings_button.bind(on_press=self.show_settings)
        tab_layout.add_widget(settings_button)

        users_button = Button(
            text=reshape_text('مدیریت کاربران'),
            font_name=FONT_NAME,
            font_size=dp(13)
        )
        users_button.bind(on_press=self.show_users)
        tab_layout.add_widget(users_button)

        main_layout.add_widget(tab_layout)

        self.content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        main_layout.add_widget(self.content_layout)

        self.show_settings()

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

    def show_settings(self, instance=None):
        self.content_layout.clear_widgets()

        db = SessionLocal()
        try:
            settings = {}
            all_settings = db.query(AppSetting).all()
            for setting in all_settings:
                settings[setting.key] = setting.value
        finally:
            db.close()

        scroll = ScrollView()
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))

        self.setting_inputs = {}

        setting_fields = [
            ('workshop_name', 'نام کارگاه', settings.get('workshop_name', '')),
            ('manager_name', 'نام مدیر', settings.get('manager_name', '')),
            ('currency', 'واحد پول', settings.get('currency', 'تومان')),
            ('settlement_limit', 'سقف تسویه (تومان)', settings.get('settlement_limit', '20000000')),
        ]

        for key, label_text, value in setting_fields:
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
                text=value,
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

            self.setting_inputs[key] = input_field
            form_layout.add_widget(field_layout)

        save_button = Button(
            text=reshape_text('ذخیره تنظیمات'),
            font_name=FONT_NAME,
            font_size=dp(16),
            background_color=(0.1, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        save_button.bind(on_press=self.save_settings)
        form_layout.add_widget(save_button)

        self.message_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )
        form_layout.add_widget(self.message_label)

        scroll.add_widget(form_layout)
        self.content_layout.add_widget(scroll)

    def show_users(self, instance=None):
        self.content_layout.clear_widgets()

        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        create_title = Label(
            text=reshape_text('ایجاد کاربر جدید'),
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(create_title)

        self.user_inputs = {}

        user_fields = [
            ('username', 'نام کاربری'),
            ('password', 'رمز عبور'),
            ('full_name', 'نام کامل'),
        ]

        for key, label_text in user_fields:
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
                password=(key == 'password'),
                font_size=dp(15),
                size_hint_y=None,
                height=dp(50),
                halign='right',
                background_color=(1, 1, 1, 1),
                foreground_color=(0.1, 0.1, 0.1, 1)
            )
            field_layout.add_widget(input_field)

            self.user_inputs[key] = input_field
            content.add_widget(field_layout)

        create_button = Button(
            text=reshape_text('ایجاد کاربر'),
            font_name=FONT_NAME,
            font_size=dp(14),
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )
        create_button.bind(on_press=self.create_user)
        content.add_widget(create_button)

        users_title = Label(
            text=reshape_text('کاربران موجود'),
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(users_title)

        users = get_all_users()
        for user in users:
            user_layout = BoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_y=None,
                height=dp(40)
            )

            user_info = Label(
                text=reshape_text(f'{user.full_name} ({user.username}) - {user.role}'),
                font_name=FONT_NAME,
                font_size=dp(12),
                halign='right',
                size_hint_x=0.7
            )
            user_layout.add_widget(user_info)

            status_button = Button(
                text=reshape_text('فعال' if user.is_active else 'غیرفعال'),
                font_name=FONT_NAME,
                font_size=dp(11),
                size_hint_x=0.3
            )
            status_button.bind(on_press=lambda x, u=user: self.toggle_user_status(u))
            user_layout.add_widget(status_button)

            content.add_widget(user_layout)

        self.user_message_label = Label(
            text='',
            font_name=FONT_NAME,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(self.user_message_label)

        scroll.add_widget(content)
        self.content_layout.add_widget(scroll)

    def save_settings(self, instance):
        db = SessionLocal()
        try:
            for key, input_field in self.setting_inputs.items():
                value = input_field.text.strip()

                if key == 'settlement_limit':
                    valid, error = validate_positive_number(value, 'سقف تسویه')
                    if not valid:
                        self.show_message(reshape_text(error), is_error=True)
                        return

                setting = db.query(AppSetting).filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    db.add(AppSetting(key=key, value=value))

            db.commit()
            self.show_message(reshape_text('تنظیمات با موفقیت ذخیره شد'), is_error=False)
        except Exception as e:
            db.rollback()
            self.show_message(reshape_text(f'خطا در ذخیره تنظیمات: {str(e)}'), is_error=True)
        finally:
            db.close()

    def create_user(self, instance):
        username = self.user_inputs['username'].text.strip()
        password = self.user_inputs['password'].text.strip()
        full_name = self.user_inputs['full_name'].text.strip()

        valid, error = validate_required(username, 'نام کاربری')
        if not valid:
            self.user_message_label.text = reshape_text(error)
            return

        valid, error = validate_required(password, 'رمز عبور')
        if not valid:
            self.user_message_label.text = reshape_text(error)
            return

        valid, error = validate_required(full_name, 'نام کامل')
        if not valid:
            self.user_message_label.text = reshape_text(error)
            return

        user, error = create_user(username, password, full_name, role='USER')

        if error:
            self.user_message_label.text = reshape_text(error)
        else:
            self.user_message_label.text = reshape_text('کاربر با موفقیت ایجاد شد')
            for input_field in self.user_inputs.values():
                input_field.text = ''
            self.show_users()

    def toggle_user_status(self, user):
        success, error = update_user(user.id, is_active=not user.is_active)

        if error:
            self.user_message_label.text = reshape_text(error)
        else:
            self.user_message_label.text = reshape_text('وضعیت کاربر تغییر کرد')
            self.show_users()

    def show_message(self, message, is_error=False):
        self.message_label.text = message
        if is_error:
            self.message_label.color = (1, 0, 0, 1)
        else:
            self.message_label.color = (0, 0.8, 0, 1)

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'