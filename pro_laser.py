import sys
import os
import time
import ctypes
import winreg
import PyQt5

# --- 修復 Qt platform plugin 路徑問題 ---
try:
    if hasattr(PyQt5, '__file__') and PyQt5.__file__:
        qt_base_path = os.path.dirname(PyQt5.__file__)
    else:
        qt_base_path = PyQt5.__path__[0]
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(qt_base_path, 'Qt5', 'plugins')
except Exception as e:
    pass
# --------------------------------------------------

from pynput import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui

# --- 語言記憶與讀取功能 ---
def load_language():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\VirtualLaserPointer", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "Language")
        winreg.CloseKey(key)
        return val if val in ["zh", "en"] else "zh"
    except FileNotFoundError:
        return "zh"

def save_language(lang):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\VirtualLaserPointer")
        winreg.SetValueEx(key, "Language", 0, winreg.REG_SZ, lang)
        winreg.CloseKey(key)
    except Exception:
        pass

# 系統狀態
state = {
    "laser_active": False,
    "drawing_active": False,
    "color": QtGui.QColor(255, 0, 0),  
    "size": 30,
    "lang": load_language() # 啟動時自動讀取上次設定的語言
}

# --- 多國語言字典 (I18N) ---
I18N = {
    "title": {"zh": "簡報虛擬雷射筆", "en": "Virtual Laser Pointer"},
    "btn_lang": {"zh": "🌐 English", "en": "🌐 中文"},
    "inst": {
        "zh": "【F8】 切換雷射筆\n【F9】 切換螢幕畫筆 (關閉時清空線條)\n【F7】 顯示/隱藏此控制面板",
        "en": "[F8] Toggle Laser\n[F9] Toggle Canvas (Clears on close)\n[F7] Show/Hide Panel"
    },
    "startup": {"zh": "開機自動啟動", "en": "Run at startup"},
    "color_label": {"zh": "雷射筆顏色：", "en": "Laser Color:"},
    "size_label": {"zh": "雷射點大小：", "en": "Laser Size:"},
    "btn_about": {"zh": "ℹ️ 關於與使用說明", "en": "ℹ️ About & Guide"},
    "tray_open": {"zh": "打開控制面板 (F7)", "en": "Open Panel (F7)"},
    "tray_about": {"zh": "關於團隊與使用說明", "en": "About & Guide"},
    "tray_quit": {"zh": "完全關閉", "en": "Quit completely"},
    "msg_title": {"zh": "虛擬雷射筆", "en": "Virtual Laser Pointer"},
    "msg_body": {"zh": "程式已縮小至系統匣，快捷鍵仍可使用！", "en": "Minimized to tray. Hotkeys are still active!"},
    "about_title": {"zh": "關於 - 虛擬雷射筆", "en": "About - Virtual Laser Pointer"},
    "laser_on": {"zh": "啟動雷射筆 (F8)", "en": "Laser ON (F8)"},
    "laser_off": {"zh": "關閉雷射筆 (F8)", "en": "Laser OFF (F8)"},
    "draw_on": {"zh": "啟動畫布 (F9)", "en": "Canvas ON (F9)"},
    "draw_off": {"zh": "關閉畫布 (F9)", "en": "Canvas OFF (F9)"}
}

COLORS = [
    {"zh": "🔴 紅色", "en": "🔴 Red", "val": QtGui.QColor(255, 0, 0)},
    {"zh": "🟢 綠色", "en": "🟢 Green", "val": QtGui.QColor(0, 255, 0)},
    {"zh": "🔵 藍色", "en": "🔵 Blue", "val": QtGui.QColor(0, 120, 255)},
    {"zh": "🟡 黃色", "en": "🟡 Yellow", "val": QtGui.QColor(255, 255, 0)},
    {"zh": "🟣 洋紅", "en": "🟣 Magenta", "val": QtGui.QColor(255, 0, 255)},
    {"zh": "🩵 青色", "en": "🩵 Cyan", "val": QtGui.QColor(0, 255, 255)},
    {"zh": "🟠 橘色", "en": "🟠 Orange", "val": QtGui.QColor(255, 120, 0)}
]

ABOUT_HTML = {
    "zh": """
    <h3 style='color: #d9534f;'>團隊 OneWAY</h3>
    <ul style='font-size: 14px;'>
        <li><b>總架構師 :</b> 陳 奕</li>
        <li><b>核心開發者 :</b> 陳 奕</li>
        <li><b>助理工程師 :</b> 林鈺芳</li>
    </ul>
    <hr>
    <h3 style='color: #0275d8;'>功能及操作使用方式</h3>
    <ul style='font-size: 13px; line-height: 1.5;'>
        <li><b>【F8】啟動雷射筆：</b>滑鼠游標轉為醒目的雷射點，適合簡報時指引焦點。</li>
        <li><b>【F9】啟動畫布：</b>凍結當前螢幕，可直接使用滑鼠在螢幕上繪圖標記，關閉時自動清空線條。</li>
        <li><b>【F7】控制面板：</b>快速隱藏或呼叫設定視窗。</li>
        <li><b>自訂外觀：</b>可於面板自由更改雷射點與畫筆的顏色、大小。</li>
        <li><b>系統匣常駐：</b>點擊視窗右上角 X 僅會縮小至系統匣，完全退出請至右下角圖示按右鍵選擇關閉。</li>
    </ul>
    """,
    "en": """
    <h3 style='color: #d9534f;'>Team OneWAY</h3>
    <ul style='font-size: 14px;'>
        <li><b>Lead Architect :</b> Yi Chen</li>
        <li><b>Core Developer :</b> Yi Chen</li>
        <li><b>Assistant Developer :</b> Yu-Fang Lin</li>
    </ul>
    <hr>
    <h3 style='color: #0275d8;'>Features & Usage Guide</h3>
    <ul style='font-size: 13px; line-height: 1.5;'>
        <li><b>[F8] Toggle Laser:</b> Turns cursor into a prominent laser dot for presentations.</li>
        <li><b>[F9] Toggle Canvas:</b> Freezes the screen for drawing/marking. Clears on exit.</li>
        <li><b>[F7] Control Panel:</b> Quickly show or hide the settings window.</li>
        <li><b>Customization:</b> Adjust laser/pen color and size freely in the panel.</li>
        <li><b>System Tray:</b> Clicking X minimizes to tray. Right-click the tray icon to quit completely.</li>
    </ul>
    """
}

class KeySignal(QtCore.QObject):
    f8_pressed = QtCore.pyqtSignal()
    f7_pressed = QtCore.pyqtSignal()
    f9_pressed = QtCore.pyqtSignal()

key_signal = KeySignal()

def on_press(key):
    if key == keyboard.Key.f8:
        key_signal.f8_pressed.emit()
    elif key == keyboard.Key.f7:
        key_signal.f7_pressed.emit()
    elif key == keyboard.Key.f9:
        key_signal.f9_pressed.emit()

class LaserDot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(state["size"], state["size"])
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_state)
        self.timer.start(16)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        color = QtGui.QColor(state["color"])
        color.setAlpha(200)
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, state["size"], state["size"])

    def update_state(self):
        if state["laser_active"] and not state["drawing_active"]:
            if self.width() != state["size"]:
                self.resize(state["size"], state["size"])
            self.show()
            pos = QtGui.QCursor.pos()
            self.move(pos.x() - (state["size"] // 2), pos.y() - (state["size"] // 2))
            self.update() 
        else:
            self.hide()

class DrawingCanvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor) 
        self.strokes = []
        self.current_path = None

    def mousePressEvent(self, event):
        self.current_path = QtGui.QPainterPath()
        self.current_path.moveTo(event.pos())

    def mouseMoveEvent(self, event):
        if self.current_path:
            self.current_path.lineTo(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.current_path:
            self.strokes.append({'path': self.current_path, 'time': time.time()})
            self.current_path = None
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 1))
        pen = QtGui.QPen(state["color"], 6, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        for stroke in self.strokes:
            painter.drawPath(stroke['path'])
        if self.current_path:
            painter.drawPath(self.current_path)

    def toggle_canvas(self):
        if state["drawing_active"]:
            desktop = QtWidgets.QApplication.desktop()
            self.setGeometry(desktop.geometry())
            self.show()
            self.raise_()
            self.strokes.clear()
            self.update()
        else:
            self.hide()

class ControlPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(360, 360)
        
        main_layout = QtWidgets.QVBoxLayout()

        # --- 頂部排版 (標題 + 右上角語言切換按鈕) ---
        top_layout = QtWidgets.QHBoxLayout()
        self.title = QtWidgets.QLabel()
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.btn_lang = QtWidgets.QPushButton()
        self.btn_lang.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_lang.setStyleSheet("font-size: 12px; padding: 4px 8px; border-radius: 4px; background-color: #e0e0e0;")
        self.btn_lang.clicked.connect(self.toggle_language)

        top_layout.addWidget(self.title)
        top_layout.addStretch() # 把按鈕推到最右邊
        top_layout.addWidget(self.btn_lang)
        main_layout.addLayout(top_layout)

        # --- 說明文字 ---
        self.instruction = QtWidgets.QLabel()
        self.instruction.setAlignment(QtCore.Qt.AlignCenter)
        self.instruction.setStyleSheet("font-size: 13px; color: #444; margin-top: 10px;")
        main_layout.addWidget(self.instruction)

        # --- 開機啟動 ---
        self.startup_checkbox = QtWidgets.QCheckBox()
        self.startup_checkbox.setStyleSheet("font-size: 14px; margin-left: 10px; margin-top: 10px;")
        self.startup_checkbox.setChecked(self.check_startup_status())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        main_layout.addWidget(self.startup_checkbox)

        # --- 顏色選擇 ---
        color_layout = QtWidgets.QHBoxLayout()
        self.color_label = QtWidgets.QLabel()
        self.color_label.setStyleSheet("font-size: 14px;")
        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.currentIndexChanged.connect(self.change_color)
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_combo)
        main_layout.addLayout(color_layout)

        # --- 尺寸調整 ---
        size_layout = QtWidgets.QHBoxLayout()
        self.size_label = QtWidgets.QLabel()
        self.size_label.setStyleSheet("font-size: 14px;")
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setMinimum(15)
        self.size_slider.setMaximum(80)
        self.size_slider.setValue(state["size"])
        self.size_slider.valueChanged.connect(self.change_size)
        size_layout.addWidget(self.size_label)
        size_layout.addWidget(self.size_slider)
        main_layout.addLayout(size_layout)

        # --- 互動按鈕區 ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_laser = QtWidgets.QPushButton()
        self.btn_draw = QtWidgets.QPushButton()
        self.btn_laser.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_draw.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_laser.clicked.connect(lambda: key_signal.f8_pressed.emit())
        self.btn_draw.clicked.connect(lambda: key_signal.f9_pressed.emit())
        btn_layout.addWidget(self.btn_laser)
        btn_layout.addWidget(self.btn_draw)
        main_layout.addLayout(btn_layout)

        # --- 關於按鈕 ---
        self.btn_about = QtWidgets.QPushButton()
        self.btn_about.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_about.setStyleSheet("font-size: 13px; padding: 5px; margin-top: 5px;")
        self.btn_about.clicked.connect(self.show_about_dialog)
        main_layout.addWidget(self.btn_about)

        self.setLayout(main_layout)

        # 系統匣圖示 (定義 action 變數以便後續更新語言)
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_menu = QtWidgets.QMenu()
        self.action_open = self.tray_menu.addAction("")
        self.action_about = self.tray_menu.addAction("")
        self.tray_menu.addSeparator()
        self.action_quit = self.tray_menu.addAction("")
        
        self.action_open.triggered.connect(self.toggle_panel)
        self.action_about.triggered.connect(self.show_about_dialog)
        self.action_quit.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_click)

        # 初始化載入文字與圖示
        self.update_texts()
        self.setup_tray_icon_img()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_status_ui)
        self.timer.start(100)

    def toggle_language(self):
        """切換語言並儲存設定"""
        state["lang"] = "en" if state["lang"] == "zh" else "zh"
        save_language(state["lang"])
        self.update_texts()

    def update_texts(self):
        """根據當前語言，一鍵全面更新介面所有文字"""
        lang = state["lang"]
        
        self.setWindowTitle(I18N["title"][lang])
        self.title.setText(I18N["title"][lang])
        self.btn_lang.setText(I18N["btn_lang"][lang])
        self.instruction.setText(I18N["inst"][lang])
        self.startup_checkbox.setText(I18N["startup"][lang])
        self.color_label.setText(I18N["color_label"][lang])
        self.size_label.setText(I18N["size_label"][lang])
        self.btn_about.setText(I18N["btn_about"][lang])

        # 系統匣選單文字
        self.action_open.setText(I18N["tray_open"][lang])
        self.action_about.setText(I18N["tray_about"][lang])
        self.action_quit.setText(I18N["tray_quit"][lang])

        # 重新載入顏色選單 (阻斷訊號以防觸發變色)
        current_idx = self.color_combo.currentIndex()
        self.color_combo.blockSignals(True)
        self.color_combo.clear()
        self.color_combo.addItems([c[lang] for c in COLORS])
        self.color_combo.setCurrentIndex(max(0, current_idx))
        self.color_combo.blockSignals(False)

        # 強制刷新一次按鈕狀態文字
        self.update_status_ui()

    def show_about_dialog(self):
        lang = state["lang"]
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(I18N["about_title"][lang])
        msg_box.setText(ABOUT_HTML[lang])
        msg_box.setWindowIcon(QtWidgets.QApplication.windowIcon())
        msg_box.exec_()

    def _get_app_path(self):
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}"'
        else:
            return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

    def check_startup_status(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "VirtualLaserPointer")
            winreg.CloseKey(key)
            if value == self._get_app_path():
                return True
            return False
        except FileNotFoundError:
            return False

    def toggle_startup(self, state):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "VirtualLaserPointer"
        app_path = self._get_app_path()

        try:
            if state == QtCore.Qt.Checked:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            pass

    def change_color(self, index):
        state["color"] = COLORS[index]["val"]

    def change_size(self, value):
        state["size"] = value

    def setup_tray_icon_img(self):
        self.tray_icon.setIcon(QtWidgets.QApplication.windowIcon())
        self.tray_icon.show()

    def on_tray_click(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def toggle_panel(self):
        if self.isHidden():
            self.showNormal()
            self.activateWindow()
        else:
            self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        lang = state["lang"]
        self.tray_icon.showMessage(I18N["msg_title"][lang], I18N["msg_body"][lang], QtWidgets.QSystemTrayIcon.Information, 2000)

    def quit_application(self):
        global listener
        if listener is not None:
            listener.stop()
        self.tray_icon.hide()
        QtWidgets.QApplication.quit()
        os._exit(0)

    def update_status_ui(self):
        lang = state["lang"]
        if state["laser_active"]:
            self.btn_laser.setText(f"🔴 {I18N['laser_off'][lang]}")
            self.btn_laser.setStyleSheet("background-color: #ffcccc; font-weight: bold; font-size: 14px; padding: 5px;")
        else:
            self.btn_laser.setText(f"⚪ {I18N['laser_on'][lang]}")
            self.btn_laser.setStyleSheet("background-color: #f0f0f0; font-weight: normal; font-size: 14px; padding: 5px;")

        if state["drawing_active"]:
            self.btn_draw.setText(f"🟢 {I18N['draw_off'][lang]}")
            self.btn_draw.setStyleSheet("background-color: #ccffcc; font-weight: bold; font-size: 14px; padding: 5px;")
        else:
            self.btn_draw.setText(f"⚪ {I18N['draw_on'][lang]}")
            self.btn_draw.setStyleSheet("background-color: #f0f0f0; font-weight: normal; font-size: 14px; padding: 5px;")

if __name__ == '__main__':
    if os.name == 'nt':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my_virtual_laser_pointer")

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pixmap = QtGui.QPixmap(64, 64)
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setBrush(QtGui.QColor(255, 0, 0))
    painter.setPen(QtCore.Qt.NoPen)
    painter.drawEllipse(12, 12, 40, 40)
    painter.end()
    app.setWindowIcon(QtGui.QIcon(pixmap))

    dot = LaserDot()
    canvas = DrawingCanvas()
    panel = ControlPanel()
    panel.show()

    def toggle_laser():
        state["laser_active"] = not state["laser_active"]
        
    def toggle_drawing():
        state["drawing_active"] = not state["drawing_active"]
        canvas.toggle_canvas()

    key_signal.f8_pressed.connect(toggle_laser)
    key_signal.f7_pressed.connect(panel.toggle_panel)
    key_signal.f9_pressed.connect(toggle_drawing)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    sys.exit(app.exec_())
