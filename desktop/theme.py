APP_STYLESHEET = """
QMainWindow, QWidget { background:#171c1f; color:#e5e8e6; font-family:'PingFang SC','Microsoft YaHei'; font-size:14px; }
QFrame#header { background:#22292d; border:1px solid #465156; border-left:4px solid #b8873b; }
QLabel#brand { background:#2d322f; color:#d7b574; border:1px solid #9d7739; font-size:18px; font-weight:700; padding:8px; }
QLabel#title { font-size:20px; font-weight:700; } QLabel#subtitle { color:#baa477; font-size:12px; }
QFrame#panel { background:#20272b; border:1px solid #414c51; border-radius:3px; }
QLabel#pageTitle { font-size:25px; font-weight:700; } QLabel#section { color:#d5ba86; font-weight:700; font-size:16px; }
QLabel#muted { color:#9aa5a5; } QLabel#metric { background:#282f32; border:1px solid #455055; padding:8px; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background:#151a1d; border:1px solid #4a565b; padding:7px; min-height:22px; }
QPushButton { background:#293135; border:1px solid #4c585d; padding:9px 13px; min-height:22px; }
QPushButton:hover { border-color:#b8873b; } QPushButton:checked, QPushButton#primary { background:#745a30; border-color:#b8873b; color:white; }
QPushButton:disabled { color:#687174; background:#22282b; } QTabWidget::pane { border:1px solid #414c51; }
QTabBar::tab { background:#252d31; padding:8px 18px; border:1px solid #414c51; } QTabBar::tab:selected { background:#745a30; }
QStatusBar { background:#20272b; color:#aeb8b5; } QToolTip { background:#f2f2ed; color:#202427; border:1px solid #555; }
"""
