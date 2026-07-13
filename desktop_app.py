import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication
    from desktop.main_window import MainWindow

    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("战场频谱智能指配系统")
    window = MainWindow()
    available = application.primaryScreen().availableGeometry()
    width = min(1200, int(available.width() * 0.94))
    height = min(820, int(available.height() * 0.9))
    window.resize(width, height)
    window.move(available.center() - window.rect().center())
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
