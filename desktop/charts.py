from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from visualization.colors import FREQUENCY_STOPS, frequency_to_hex


class TopologyCanvas(QWidget):
    def __init__(self):
        super().__init__(); self.links = []; self.setMinimumSize(620, 520)

    def set_links(self, links):
        self.links = list(links); self.update()

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#171f2b"))
        plot = QRectF(72, 42, max(100, self.width()-120), max(100, self.height()-105))
        painter.setPen(QPen(QColor("#35424b"), 1))
        for value in range(0, 101, 20):
            point = self._point(value, value, plot)
            painter.drawLine(QPointF(plot.left(), point.y()), QPointF(plot.right(), point.y()))
            painter.drawText(QRectF(10, point.y()-10, 52, 20), Qt.AlignRight|Qt.AlignVCenter, str(value))
            painter.drawText(QRectF(point.x()-20, plot.bottom()+8, 40, 20), Qt.AlignCenter, str(value))
        painter.setPen(QColor("#dfe4e2")); painter.drawText(QRectF(plot.left(), self.height()-30, plot.width(), 22), Qt.AlignCenter, "X 坐标 (km)")
        painter.save(); painter.translate(20, plot.center().y()); painter.rotate(-90); painter.drawText(QRectF(-plot.height()/2, -12, plot.height(), 24), Qt.AlignCenter, "Y 坐标 (km)"); painter.restore()
        painter.setPen(QPen(QColor("#2d789c"), 3))
        for link in self.links:
            painter.drawLine(self._point(link.transmitter.x_km, link.transmitter.y_km, plot), self._point(link.receiver.x_km, link.receiver.y_km, plot))
        devices = {d.device_id: d for link in self.links for d in (link.transmitter, link.receiver)}
        for device in devices.values():
            point = self._point(device.x_km, device.y_km, plot)
            painter.setBrush(QColor("#e3e7e5")); painter.setPen(QPen(QColor("#38bdf8"), 2)); painter.drawEllipse(point, 6, 6)
            painter.setPen(QColor("#d7dcda")); painter.setFont(QFont("PingFang SC", 8))
            painter.drawText(QRectF(point.x()-55, point.y()-25, 110, 18), Qt.AlignCenter, f"{device.device_id} ({device.x_km:.1f}, {device.y_km:.1f})")
        if not self.links:
            painter.setPen(QColor("#9aa5a5")); painter.drawText(self.rect(), Qt.AlignCenter, "尚未建立通信拓扑")

    @staticmethod
    def _point(x, y, plot):
        return QPointF(plot.left()+float(x)/100*plot.width(), plot.bottom()-float(y)/100*plot.height())


class ConflictCanvas(QWidget):
    def __init__(self):
        super().__init__(); self.records = []; self.setMinimumSize(620, 520)

    def set_records(self, records, only_conflicts=True, search="", page=1, page_size=20):
        filtered = list(records)
        if search:
            query = search.strip().lower()
            filtered = [record for record in filtered if query in record.left.link_id.lower() or query in record.right.link_id.lower()]
        if only_conflicts:
            filtered = [record for record in filtered if record.is_conflict]
        self.total_records = len(filtered)
        self.total_pages = max(1, (self.total_records + page_size - 1) // page_size)
        self.page = min(max(1, page), self.total_pages)
        start = (self.page - 1) * page_size
        self.records = filtered[start:start + page_size]
        self.update()
        return self.total_records, self.total_pages, self.page

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing); painter.fillRect(self.rect(), QColor("#171f2b"))
        top, bottom = 35, self.height()-100; row_height = max(32, (bottom-top)/max(1, len(self.records)))
        left_x, right_x = 130, self.width()-130
        for index, record in enumerate(self.records):
            y = top + (index+.5)*row_height
            painter.setPen(QPen(QColor("#39454e"), 1)); painter.drawLine(20, int(y+row_height/2), self.width()-20, int(y+row_height/2))
            if record.is_conflict:
                painter.setPen(QPen(QColor("#ff3344"), 4)); painter.drawLine(left_x, int(y), right_x, int(y))
            for x, link, align in ((left_x, record.left, Qt.AlignRight), (right_x, record.right, Qt.AlignLeft)):
                painter.setBrush(QColor(frequency_to_hex(link.frequency_ghz))); painter.setPen(QPen(QColor("#eef1ef"), 1)); painter.drawEllipse(QPointF(x, y), 16, 16)
                label = f"{link.transmitter.device_id}–{link.receiver.device_id}  {link.frequency_ghz:.2f}G"
                rect = QRectF(x-125 if x == left_x else x+22, y-11, 100, 22)
                painter.setPen(QColor("#e3e7e5")); painter.drawText(rect, align|Qt.AlignVCenter, label)
        legend = QRectF(55, self.height()-55, self.width()-110, 18); gradient = QLinearGradient(legend.left(), 0, legend.right(), 0)
        for index, color in enumerate(FREQUENCY_STOPS): gradient.setColorAt(index/(len(FREQUENCY_STOPS)-1), QColor(color))
        painter.fillRect(legend, gradient); painter.setPen(QColor("#e3e7e5"))
        for value in range(1, 10):
            x = legend.left()+(value-1)/8*legend.width(); painter.drawText(QRectF(x-15, legend.bottom()+4, 30, 18), Qt.AlignCenter, f"{value}G")
        painter.drawText(QRectF(legend.left(), legend.top()-24, legend.width(), 20), Qt.AlignCenter, "频率 (GHz)")
        if not self.records:
            painter.setPen(QColor("#9aa5a5")); painter.drawText(QRectF(0, 0, self.width(), self.height()-75), Qt.AlignCenter, "暂无冲突")
