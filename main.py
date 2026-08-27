from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.core.text import LabelBase
import os

from database.database import init_db, create_default_data
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.calculator import CalculatorScreen
from screens.fabric import FabricScreen
from screens.products import ProductsScreen
from screens.contracts import ContractsScreen
from screens.production import ProductionScreen
from screens.accounting import AccountingScreen
from screens.personal_accounting import PersonalAccountingScreen
from screens.settings import SettingsScreen
from screens.reports import ReportsScreen
from screens.notes import NotesScreen


def register_font():
    """ثبت فونت فارسی"""
    font_candidates = [
        os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'Vazir.ttf'),
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]

    font_path = None
    for font in font_candidates:
        if os.path.exists(font) and os.path.getsize(font) > 50000:
            font_path = font
            break

    if not font_path:
        print("هیچ فونتی پیدا نشد")
        return False

    print(f"فونت پیدا شد: {font_path}")

    try:
        LabelBase.register(name="Persian", fn_regular=font_path)
        LabelBase.register(name="Persian.ttf", fn_regular=font_path)
        print("فونت فارسی با موفقیت ثبت شد")
        return True
    except Exception as e:
        print(f"خطا در ثبت فونت: {str(e)}")
        return False


class SafiERPApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Safi ERP"

    def build(self):
        Window.clearcolor = (0.93, 0.95, 0.98, 1)

        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(CalculatorScreen(name="calculator"))
        sm.add_widget(FabricScreen(name="fabric"))
        sm.add_widget(ProductsScreen(name="products"))
        sm.add_widget(ContractsScreen(name="contracts"))
        sm.add_widget(ProductionScreen(name="production"))
        sm.add_widget(AccountingScreen(name="accounting"))
        sm.add_widget(PersonalAccountingScreen(name="personal_accounting"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(NotesScreen(name="notes"))

        return sm


if __name__ == "__main__":
    register_font()
    init_db()
    create_default_data()
    SafiERPApp().run()