from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from services.inventory_service import get_total_fabric_stock, get_total_product_stock
from services.production_service import get_today_productions, get_productions_by_month
from services.accounting_service import get_current_period
from utils.formatters import format_number, format_currency
from utils.persian_text import reshape_text
from datetime import datetime

FONT_NAME = 'Persian'


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        with self.canvas.before:
            Color(0.93, 0.95, 0.98, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )

        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.08,
            spacing=dp(10)
        )

        title_label = Label(
            text=reshape_text('داشبورد'),
            font_name=FONT_NAME,
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='right',
            size_hint_x=0.7
        )
        header.add_widget(title_label)

        logout_button = Button(
            text=reshape_text('خروج'),
            font_name=FONT_NAME,
            font_size=dp(13),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_x=0.3
        )
        logout_button.bind(on_press=self.logout)
        header.add_widget(logout_button)

        main_layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # منوی دکمه‌ها
        menu_grid = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(250)
        )

        menu_items = [
            ('ماشین حساب', 'calculator'),
            ('انبار پارچه', 'fabric'),
            ('انبار محصول', 'products'),
            ('قرارداد', 'contracts'),
            ('تولید', 'production'),
            ('حسابداری', 'accounting'),
            ('شخصی', 'personal_accounting'),
            ('یادداشت', 'notes'),
            ('گزارش‌ها', 'reports'),
            ('تنظیمات', 'settings'),
        ]

        for text, screen_name in menu_items:
            btn = Button(
                text=reshape_text(text),
                font_name=FONT_NAME,
                font_size=dp(14),
                background_color=(0.1, 0.4, 0.8, 1),
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(45)
            )
            btn.bind(on_press=lambda x, sn=screen_name: self.go_to_screen(sn))
            menu_grid.add_widget(btn)

        content.add_widget(menu_grid)

        # کارت‌های آماری
        stats_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(250)
        )

        fabric_stock = get_total_fabric_stock()
        stats_grid.add_widget(self.create_stat_card(
            'موجودی پارچه', f'{format_number(fabric_stock)} متر', (0.1, 0.5, 0.3, 1)
        ))

        product_stock = get_total_product_stock()
        stats_grid.add_widget(self.create_stat_card(
            'موجودی محصول', f'{format_number(product_stock)} عدد', (0.1, 0.4, 0.8, 1)
        ))

        today_total = sum(p.quantity for p in get_today_productions())
        stats_grid.add_widget(self.create_stat_card(
            'تولید امروز', f'{format_number(today_total)} عدد', (0.8, 0.5, 0.1, 1)
        ))

        current_period = get_current_period()
        if current_period:
            stats_grid.add_widget(self.create_stat_card(
                'درآمد دوره', format_currency(current_period['total_income']), (0.1, 0.6, 0.5, 1)
            ))

        content.add_widget(stats_grid)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def create_stat_card(self, title, value, color):
        card = BoxLayout(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(5)
        )

        with card.canvas.before:
            Color(color[0], color[1], color[2], 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.bind(pos=lambda *a: self._update_card_bg(card, color),
                  size=lambda *a: self._update_card_bg(card, color))

        title_label = Label(
            text=reshape_text(title),
            font_name=FONT_NAME,
            font_size=dp(12),
            color=(1, 1, 1, 0.8),
            halign='right'
        )
        card.add_widget(title_label)

        value_label = Label(
            text=reshape_text(value),
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=(1, 1, 1, 1),
            halign='right'
        )
        card.add_widget(value_label)

        return card

    def _update_card_bg(self, card, color):
        card.canvas.before.clear()
        with card.canvas.before:
            Color(color[0], color[1], color[2], 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[12])

    def go_to_screen(self, screen_name):
        if self.manager.has_screen(screen_name):
            self.manager.current = screen_name

    def logout(self, instance):
        self.manager.current = 'login'

    def on_enter(self):
        self.build_ui()