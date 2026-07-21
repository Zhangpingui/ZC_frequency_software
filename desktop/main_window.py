from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QProgressBar, QScrollArea, QSpinBox, QVBoxLayout, QWidget

from core.demand_workbook import DEMO_ALGORITHMS, example_demand_dataset, export_optimized_workbook, parse_demand_upload
from desktop.state import DesktopState
from desktop.theme import APP_STYLESHEET


def _panel() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame(objectName="panel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)
    return frame, layout


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.state = DesktopState()
        self.setWindowTitle("战场频谱智能指配系统")
        self.setMinimumSize(1180, 720)
        self.resize(1480, 900)
        self.setStyleSheet(APP_STYLESHEET)
        central = QWidget(); root = QVBoxLayout(central)
        header = QLabel("频谱资源规划 · 冲突分析 · 结果导出\n战场频谱智能指配系统", objectName="title")
        root.addWidget(header)
        columns = QHBoxLayout(); root.addLayout(columns, 1)
        self.left, self.left_layout = _panel(); self.center, self.center_layout = _panel(); self.right, self.right_layout = _panel()
        columns.addWidget(self.left, 24); columns.addWidget(self.center, 43); columns.addWidget(self.right, 33)
        self._build_left(); self._build_center(); self._build_right(); self.setCentralWidget(central); self._refresh()

    def _build_left(self) -> None:
        self.left_layout.addWidget(QLabel("参数配置"))
        parameters, parameter_layout = _panel()
        form = QFormLayout(); parameter_layout.addLayout(form)
        occupancy = QDoubleSpinBox(); occupancy.setRange(0, 100); occupancy.setValue(38); occupancy.setSuffix(" %")
        links = QSpinBox(); links.setRange(1, 100000); links.setValue(15); links.setSuffix(" 条")
        remaining = QSpinBox(); remaining.setRange(0, 100000); remaining.setValue(3); remaining.setSuffix(" 对")
        form.addRow("频道占用率（%）", occupancy); form.addRow("通信链路数量（条）", links); form.addRow("优化后剩余干扰（对）", remaining)
        self.left_layout.addWidget(parameters)
        self.left_layout.addWidget(QLabel("数据接入")); upload = QPushButton("导入用频需求表"); upload.clicked.connect(self._import); self.left_layout.addWidget(upload)
        mock = QPushButton("生成模拟数据"); mock.clicked.connect(self._mock); self.left_layout.addWidget(mock)
        self.source = QLabel("当前数据源：未导入", objectName="muted"); self.left_layout.addWidget(self.source)
        self.left_layout.addWidget(QLabel("优化算法")); self.algorithm = QComboBox(); self.algorithm.addItems(DEMO_ALGORITHMS); self.algorithm.setCurrentText("DQN-GNN"); self.left_layout.addWidget(self.algorithm)
        self.start = QPushButton("启动频率优化", objectName="primary"); self.start.clicked.connect(self._start); self.left_layout.addWidget(self.start)
        self.progress = QProgressBar(); self.progress.setVisible(False); self.left_layout.addWidget(self.progress); self.left_layout.addStretch()

    def _build_center(self) -> None:
        self.center_layout.addWidget(QLabel("用频冲突组合")); self.metrics = QLabel(objectName="metric"); self.center_layout.addWidget(self.metrics)
        self.view = QComboBox(); self.view.addItems(["优化前", "优化后"]); self.view.currentTextChanged.connect(self._refresh_pairs); self.center_layout.addWidget(self.view)
        self.pairs = QVBoxLayout(); holder = QWidget(); holder.setObjectName("pairViewport"); holder.setLayout(self.pairs); scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(holder); self.center_layout.addWidget(scroll, 1)

    def _build_right(self) -> None:
        self.right_layout.addWidget(QLabel("频率指配结果")); self.file_state = QLabel("执行优化后将生成带“建议”列的 Excel 结果文件。", objectName="muted"); self.file_state.setWordWrap(True); self.right_layout.addWidget(self.file_state)
        self.result_metrics = QLabel("调整建议：—\n保持原频率：—", objectName="metric"); self.right_layout.addWidget(self.result_metrics)
        self.download = QPushButton("下载结果 Excel", objectName="primary"); self.download.clicked.connect(self._save); self.right_layout.addWidget(self.download)
        self.compare = QLabel("优化前后冲突对比\n优化前：10 对\n优化后：—\n冲突下降率：—", objectName="metric"); self.right_layout.addWidget(self.compare); self.right_layout.addStretch()

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "导入用频需求表", "", "Excel (*.xlsx)")
        if not path: return
        try: self.state.load_dataset(parse_demand_upload(Path(path).read_bytes(), Path(path).name), Path(path).name); self._refresh()
        except (OSError, ValueError) as error: QMessageBox.warning(self, "导入失败", str(error))

    def _mock(self) -> None:
        self.state.load_dataset(example_demand_dataset(), "系统模拟数据"); self._refresh()

    def _start(self) -> None:
        if self.state.dataset is None: return
        self.start.setEnabled(False); self.progress.setVisible(True); self.progress.setValue(10)
        QTimer.singleShot(1000, lambda: self.progress.setValue(55)); QTimer.singleShot(2000, lambda: self.progress.setValue(85)); QTimer.singleShot(3000, self._finish)

    def _finish(self) -> None:
        self.state.optimize(self.algorithm.currentText()); self.progress.setValue(100); self.progress.setVisible(False); self.start.setEnabled(True); self.view.setCurrentText("优化后"); self._refresh()

    def _save(self) -> None:
        if self.state.result is None: return
        path, _ = QFileDialog.getSaveFileName(self, "保存结果", "用频需求表_优化结果.xlsx", "Excel (*.xlsx)")
        if path: Path(path).write_bytes(export_optimized_workbook(self.state.result))

    def _refresh(self) -> None:
        self.source.setText(f"当前数据源：{self.state.source_name}"); ready = self.state.dataset is not None; self.start.setEnabled(ready); self.download.setEnabled(self.state.result is not None); self.view.setEnabled(ready); self._refresh_pairs()
        if self.state.result:
            result = self.state.result; adjusted = sum(value.startswith("建议调整为 ") for value in result.suggestions.values()); self.file_state.setText("用频需求表_优化结果.xlsx\n已保留原始字段，仅填充“建议”列"); self.result_metrics.setText(f"调整建议：{adjusted} 条\n保持原频率：{len(result.suggestions) - adjusted} 条"); self.compare.setText(f"优化前后冲突对比\n优化前：10 对\n优化后：{result.after_conflict_count} 对\n冲突下降率：{result.reduction_pct:g}%")

    def _refresh_pairs(self) -> None:
        while self.pairs.count():
            item = self.pairs.takeAt(0); widget = item.widget(); widget and widget.deleteLater()
        if self.state.dataset is None: self.metrics.setText("请导入 Excel 或生成模拟数据"); return
        preview = self.state.result or self.state.optimize("DQN-GNN")
        if self.state.result is None: self.state.result = None
        pairs = preview.after_pairs if self.view.currentText() == "优化后" and self.state.result else preview.before_pairs
        self.metrics.setText(f"用频需求 {len(self.state.dataset.frame)} 条 · 原始冲突 10 对 · 优化后 {self.state.result.after_conflict_count if self.state.result else '未执行'}")
        for pair in pairs:
            label = QLabel(f"{pair.left_name}  {'— 冲突 —' if pair.is_conflict else '— 已消解 —'}  {pair.right_name}")
            label.setStyleSheet("padding:10px;border-radius:7px;background:#5b2636;" if pair.is_conflict else "padding:10px;border-radius:7px;background:#126452;")
            self.pairs.addWidget(label)
