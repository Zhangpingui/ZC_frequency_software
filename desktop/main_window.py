from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QSpinBox,
    QStackedWidget, QTabWidget, QVBoxLayout, QWidget,
)

from core.io import example_dataframe, parse_uploaded_data, template_xlsx_bytes
from core.metrics import calculate_metrics
from core.models import ScenarioParameters
from core.validation import validate_scenario
from desktop.charts import ConflictCanvas, TopologyCanvas
from desktop.state import DesktopState
from desktop.theme import APP_STYLESHEET


def _panel() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame(objectName="panel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)
    return frame, layout


def _page_heading(title: str, subtitle: str) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(QLabel(title, objectName="pageTitle"))
    layout.addWidget(QLabel(subtitle, objectName="muted"))
    return layout


class ParameterPage(QWidget):
    saved = Signal()

    def __init__(self, state: DesktopState):
        super().__init__()
        self.state = state
        root = QVBoxLayout(self)
        root.addLayout(_page_heading("参数配置", "定义本次频谱指配任务的规模、现状与优化目标。"))
        panel, body = _panel()
        form = QFormLayout()
        self.occupancy = self._double(38, 0, 100, "%")
        self.links = self._integer(15, 1, 100000, " 条")
        self.devices = self._integer(30, 2, 200000, " 台")
        self.interference = self._integer(12, 0, 1000000, " 对")
        self.remaining = self._integer(2, 0, 1000000, " 对")
        self.span = self._double(4.8, 0, 8, " GHz")
        self.ratio = self._double(60, 0, 100, "%")
        fields = (("频道占用率", self.occupancy), ("通信链路数量", self.links),
                  ("用频设备数量", self.devices), ("链路间干扰数量", self.interference),
                  ("优化后剩余干扰数", self.remaining), ("频谱指配实际跨度", self.span),
                  ("频谱指配跨度比例", self.ratio))
        helps = ("示例：38%，表示当前可用频道资源占用水平。", "示例：15 条待指配链路。",
                 "示例：30 台收发设备。", "示例：检测到 12 对潜在干扰。",
                 "示例：优化目标剩余 2 对。", "最高与最低工作频率之差。", "相对于 1–9 GHz 的跨度比例。")
        for (label, widget), help_text in zip(fields, helps):
            widget.setToolTip(help_text)
            form.addRow(label, widget)
        body.addLayout(form)
        save = QPushButton("校验并保存任务场景", objectName="primary")
        save.clicked.connect(self.save_values)
        body.addWidget(save)
        root.addWidget(panel)
        root.addStretch()

    @staticmethod
    def _double(value, minimum, maximum, suffix):
        widget = QDoubleSpinBox(); widget.setRange(minimum, maximum); widget.setValue(value)
        widget.setDecimals(1); widget.setSuffix(suffix); return widget

    @staticmethod
    def _integer(value, minimum, maximum, suffix):
        widget = QSpinBox(); widget.setRange(minimum, maximum); widget.setValue(value)
        widget.setSuffix(suffix); return widget

    def save_values(self):
        try:
            scenario = ScenarioParameters(self.occupancy.value(), self.links.value(), self.devices.value(),
                self.interference.value(), self.remaining.value(), self.span.value(), self.ratio.value())
            validate_scenario(scenario)
            self.state.scenario = scenario
            QMessageBox.information(self, "保存成功", "任务场景已通过校验并保存。")
            self.saved.emit()
        except ValueError as error:
            QMessageBox.warning(self, "参数校验失败", str(error))


class TopologyPage(QWidget):
    data_changed = Signal()

    def __init__(self, state: DesktopState):
        super().__init__(); self.state = state
        root = QVBoxLayout(self)
        root.addLayout(_page_heading("物理拓扑", "导入 Excel、CSV 或 JSON，验证 100 × 100 km 作战区域通信拓扑。"))
        columns = QHBoxLayout(); root.addLayout(columns, 1)
        left, left_body = _panel(); self.chart = TopologyCanvas(); left_body.addWidget(self.chart)
        right, right_body = _panel(); right.setFixedWidth(330)
        right_body.addWidget(QLabel("数据接入", objectName="section"))
        upload = QPushButton("导入本地数据文件", objectName="primary"); upload.clicked.connect(self.import_file)
        mock = QPushButton("生成并加载模拟数据"); mock.clicked.connect(self.load_mock)
        download = QPushButton("导出模拟 Excel 数据"); download.clicked.connect(self.save_mock_excel)
        right_body.addWidget(upload); right_body.addWidget(mock); right_body.addWidget(download)
        self.source = QLabel("数据源：未导入", objectName="muted")
        self.summary = QLabel("设备数 0\n通信链路 0\n字段完整率 0%", objectName="metric")
        right_body.addWidget(self.source); right_body.addWidget(self.summary); right_body.addStretch()
        columns.addWidget(left, 1); columns.addWidget(right)
        self.refresh()

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择链路数据", "", "数据文件 (*.xlsx *.csv *.json)")
        if not path: return
        try:
            frame = parse_uploaded_data(Path(path).read_bytes(), Path(path).name)
            self.state.load_frame(frame, Path(path).name); self.refresh(); self.data_changed.emit()
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "导入失败", str(error))

    def load_mock(self):
        self.state.load_frame(example_dataframe(), "系统模拟数据"); self.refresh(); self.data_changed.emit()

    def save_mock_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存模拟数据", "模拟频谱链路数据.xlsx", "Excel (*.xlsx)")
        if path:
            Path(path).write_bytes(template_xlsx_bytes())

    def refresh(self):
        if self.state.links:
            self.chart.set_links(self.state.links)
        else:
            self.chart.set_links([])
        devices = {d.device_id for link in self.state.links for d in (link.transmitter, link.receiver)}
        self.source.setText(f"数据源：{self.state.source_name}")
        self.summary.setText(f"设备数 {len(devices)}\n通信链路 {len(self.state.links)}\n字段完整率 {'100' if self.state.links else '0'}%")


class AnalysisPage(QWidget):
    result_changed = Signal()

    def __init__(self, state: DesktopState):
        super().__init__(); self.state = state
        root = QVBoxLayout(self)
        root.addLayout(_page_heading("冲突计算", "检测当前方案冲突，并对比算法优化前后的频率指配结果。"))
        columns = QHBoxLayout(); root.addLayout(columns, 1)
        left, left_body = _panel(); self.tabs = QTabWidget()
        self.before_chart = ConflictCanvas(); self.after_chart = ConflictCanvas()
        self.tabs.addTab(self.before_chart, "优化前"); self.tabs.addTab(self.after_chart, "优化后")
        left_body.addWidget(self.tabs)
        self.metrics = QLabel("尚未执行冲突检测", objectName="metric"); left_body.addWidget(self.metrics)
        right, controls = _panel(); right.setFixedWidth(330); controls.addWidget(QLabel("计算控制台", objectName="section"))
        self.threshold = QDoubleSpinBox(); self.threshold.setRange(0, 500); self.threshold.setValue(10); self.threshold.setSuffix(" km")
        self.guard = QDoubleSpinBox(); self.guard.setRange(0, 1000); self.guard.setValue(20); self.guard.setSuffix(" MHz")
        self.algorithm = QComboBox(); self.algorithm.addItems(["贪婪算法", "DQN-GNN", "遗传算法", "禁忌搜索"])
        form = QFormLayout(); form.addRow("空间干扰阈值", self.threshold); form.addRow("保护频差", self.guard); form.addRow("优化算法", self.algorithm)
        controls.addLayout(form)
        detect = QPushButton("1. 检测当前方案冲突", objectName="primary"); detect.clicked.connect(self.detect)
        optimize = QPushButton("2. 选择算法并优化频率"); optimize.clicked.connect(self.optimize)
        controls.addWidget(detect); controls.addWidget(optimize)
        self.mode_note = QLabel("DQN-GNN、遗传算法、禁忌搜索当前为演示适配器。", objectName="muted"); self.mode_note.setWordWrap(True)
        controls.addWidget(self.mode_note); controls.addStretch()
        columns.addWidget(left, 1); columns.addWidget(right)
        self.refresh()

    def _sync_settings(self):
        self.state.distance_threshold = self.threshold.value(); self.state.guard_band = self.guard.value()

    def detect(self):
        if not self.state.links:
            QMessageBox.warning(self, "缺少数据", "请先在数据建模页面导入或生成模拟数据。")
            return
        self._sync_settings(); self.state.detect_conflicts(); self.refresh(); self.result_changed.emit()

    def optimize(self):
        if not self.state.links:
            QMessageBox.warning(self, "缺少数据", "请先在数据建模页面导入或生成模拟数据。")
            return
        self._sync_settings(); result = self.state.optimize(self.algorithm.currentText()); self.refresh(); self.tabs.setCurrentIndex(1)
        suffix = "（演示模式）" if result.is_demo else ""
        QMessageBox.information(self, "计算完成", f"{result.algorithm_name}{suffix} 已完成频率优化。")
        self.result_changed.emit()

    def refresh(self):
        if not self.state.links:
            self.before_chart.set_records([]); self.after_chart.set_records([]); return
        before_records = self.state.detect_conflicts(False)
        self.before_chart.set_records(before_records)
        before_metrics = calculate_metrics(self.state.links, self.state.distance_threshold, self.state.guard_band)
        after_metrics = before_metrics
        if self.state.optimized_links:
            after_records = self.state.detect_conflicts(True)
            self.after_chart.set_records(after_records)
            after_metrics = calculate_metrics(self.state.optimized_links, self.state.distance_threshold, self.state.guard_band)
        else:
            self.after_chart.set_records([])
        reduction = (before_metrics.conflict_count-after_metrics.conflict_count)/before_metrics.conflict_count*100 if before_metrics.conflict_count else 0
        self.metrics.setText(f"冲突：{before_metrics.conflict_count} → {after_metrics.conflict_count} 对    下降率：{reduction:.1f}%    优化后频点数：{after_metrics.unique_frequency_count}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.state = DesktopState(); self.setWindowTitle("战场频谱智能指配系统")
        self.resize(1500, 920); self.setMinimumSize(1100, 720); self.setStyleSheet(APP_STYLESHEET)
        central = QWidget(); root = QVBoxLayout(central); root.setContentsMargins(18, 16, 18, 12); root.setSpacing(12)
        header = QFrame(objectName="header"); header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("ZS", objectName="brand")); titles = QVBoxLayout(); titles.addWidget(QLabel("频谱资源规划与冲突分析", objectName="subtitle")); titles.addWidget(QLabel("战场频谱智能指配系统", objectName="title")); header_layout.addLayout(titles); header_layout.addStretch(); self.task = QLabel("任务编号  ZS-2026-001"); header_layout.addWidget(self.task)
        root.addWidget(header)
        self.stack = QStackedWidget(); self.parameters = ParameterPage(self.state); self.topology = TopologyPage(self.state); self.analysis = AnalysisPage(self.state)
        self.stack.addWidget(self.parameters); self.stack.addWidget(self.topology); self.stack.addWidget(self.analysis); root.addWidget(self.stack, 1)
        navigation = QHBoxLayout(); navigation.addStretch(); self.nav_buttons = []
        for index, label in enumerate(("01  参数配置", "02  物理拓扑", "03  冲突计算")):
            button = QPushButton(label); button.setCheckable(True); button.clicked.connect(lambda checked=False, page=index: self.navigate(page)); navigation.addWidget(button); self.nav_buttons.append(button)
        navigation.addStretch(); root.addLayout(navigation); self.setCentralWidget(central)
        self.topology.data_changed.connect(self._data_updated); self.analysis.result_changed.connect(self._result_updated)
        self.navigate(0); self.statusBar().showMessage("本地计算模式 · 数据仅在当前应用会话处理")

    def navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for button_index, button in enumerate(self.nav_buttons): button.setChecked(button_index == index)
        if index == 1: self.topology.refresh()
        if index == 2: self.analysis.refresh()

    def _data_updated(self):
        self.statusBar().showMessage(f"已加载 {len(self.state.links)} 条通信链路 · 数据源：{self.state.source_name}")

    def _result_updated(self):
        name = self.state.solver_result.algorithm_name if self.state.solver_result else "冲突检测"
        self.statusBar().showMessage(f"{name} 已完成")
