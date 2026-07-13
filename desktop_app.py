import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication
    from desktop.main_window import MainWindow

    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("战场频谱智能指配系统")
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
