import sys
import os
import PyQt5

# --- 加入與主程式相同的 Qt 路徑修復代碼 ---
try:
    if hasattr(PyQt5, '__file__') and PyQt5.__file__:
        qt_base_path = os.path.dirname(PyQt5.__file__)
    else:
        qt_base_path = PyQt5.__path__[0]
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(qt_base_path, 'Qt5', 'plugins')
except Exception as e:
    pass
# --------------------------------------------------

from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# 啟動 QApplication
app = QApplication(sys.argv)

# 建立畫布與繪製紅點
pixmap = QPixmap(256, 256)
pixmap.fill(Qt.transparent)

painter = QPainter(pixmap)
painter.setRenderHint(QPainter.Antialiasing)
painter.setBrush(QColor(255, 0, 0))
painter.setPen(Qt.NoPen)
painter.drawEllipse(16, 16, 224, 224)
painter.end()

# 存檔
pixmap.save("red_dot.ico", "ICO")
print("✅ 成功生成 red_dot.ico 圖示檔！")
