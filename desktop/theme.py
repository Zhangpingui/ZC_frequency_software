APP_STYLESHEET = """
QMainWindow { background:#06182f; color:#e5f4ff; }
QWidget { background:#06182f; color:#d8ecfb; font-family: PingFang SC, Arial; }
QFrame#panel { background:#082441; border:1px solid #245274; border-radius:9px; }
QLabel#title { background:transparent; font-size:20px; font-weight:700; color:#effaff; }
QLabel#muted { background:transparent; color:#86abc5; }
QLabel#metric { background:#071f3a; border:1px solid #245678; border-radius:7px; color:#a8dbf7; font-size:13px; padding:10px; }
QPushButton { background:#103b60; border:1px solid #33729b; border-radius:6px; color:#d9f1ff; padding:9px; }
QPushButton:hover { background:#19547e; }
QPushButton#primary { background:#087db7; border-color:#45d2dd; color:#ffffff; font-weight:700; }
QComboBox, QAbstractSpinBox { background:#0a2947; border:1px solid #33739b; border-radius:5px; color:#e5f4ff; min-height:28px; padding:4px 8px; }
QComboBox::drop-down, QAbstractSpinBox::up-button, QAbstractSpinBox::down-button { background:#103b60; border:0; width:22px; }
QComboBox QAbstractItemView { background:#0a2947; border:1px solid #33739b; color:#e5f4ff; selection-background-color:#19547e; }
QScrollArea { background:#06182f; border:1px solid #245274; border-radius:7px; }
QScrollArea > QWidget > QWidget { background:#06182f; }
QScrollBar:vertical { background:#06182f; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:#245678; border-radius:5px; min-height:30px; }
QProgressBar { background:#071f3a; border:1px solid #33739b; border-radius:5px; color:#e5f4ff; text-align:center; }
QProgressBar::chunk { background:#18a9bd; border-radius:4px; }
"""
