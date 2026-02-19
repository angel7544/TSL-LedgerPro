
try:
    from ui.settings import SettingsPage
    from auth.ui import LoginWindow
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
