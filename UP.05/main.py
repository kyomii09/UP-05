import sys
from pathlib import Path

try:
    import PyQt5
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parent
    site_packages = project_root / ".venv" / "Lib" / "site-packages"
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))

from PyQt5.QtWidgets import QApplication

from interface import CalorieCalculator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalorieCalculator()
    window.show()
    sys.exit(app.exec_())