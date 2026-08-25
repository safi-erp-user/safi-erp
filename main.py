from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
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

def register_font():
    font_candidates = [
        (r"C:\Windows\Fonts\BNAZANIN.TTF", "B Nazanin"),
        (r"C:\Windows\Fonts\BNAZANNB.TTF", "B Nazanin Bold"),
        (r"C:\Windows\Fonts\tahoma.ttf", "Tahoma"),
        (r"C:\Windows\Fonts\arial.ttf", "Arial"),
        (r"C:\Windows\Fonts\times.ttf", "Times New Roman"),
    ]

    font_path = None
    font_name = ""
    for path, name in font_candidates:
        if os.path.exists(path):
            font_path = path
            font_name = name
            break

    if not font_path:
        print("هیچ فونتی پیدا نشد")
        return False

    print(f"فونت پیدا شد: {font_name} - {font_path}")

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
        self.title = "مدیریت تولید صافی"

    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
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
        return sm

if __name__ == "__main__":
    register_font()
    init_db()
    create_default_data()
    SafiERPApp().run()
