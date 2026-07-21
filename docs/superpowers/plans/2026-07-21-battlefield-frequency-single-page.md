# Battlefield Frequency Single-Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared, single-page three-column frequency-assignment workbench for Streamlit and PySide6 that imports the demand workbook, shows demonstrative conflict changes, and downloads an Excel result with completed suggestions.

**Architecture:** Add a demand-workbook domain layer independent of either UI: it validates the 12-column frequency-demand format, creates deterministic demo optimization results, and exports a new workbook with only the `建议` column populated. The Streamlit workbench and the restored PySide6 desktop workbench consume that layer and keep their presentation state local.

**Tech Stack:** Python 3.11+, Streamlit, PySide6-Essentials, pandas, openpyxl, Plotly, pytest.

---

## File Structure

- Create: `core/demand_models.py` — immutable pair/result models shared by both UIs.
- Create: `core/demand_workbook.py` — workbook validation, demo data generation, deterministic result creation, and result export.
- Create: `ui/workbench.py` — Streamlit three-column page and session-state transitions.
- Create: `desktop/__init__.py`, `desktop/state.py`, `desktop/main_window.py`, `desktop/theme.py`, `desktop_app.py` — native desktop entry point and single-window UI.
- Modify: `app.py` — remove page routing and render the new workbench.
- Modify: `ui/shell.py` — replace old multipage defaults with workbench state and retain only header/theme helpers.
- Modify: `assets/theme.css` — replace old multipage styles with dark-blue three-column workbench styling.
- Modify: `requirements.txt` — add the PySide6 desktop runtime dependency.
- Modify: `README.md` — document both startup methods and the 12-column workbook workflow.
- Create: `tests/test_demand_workbook.py` — shared data and export contract tests.
- Create: `tests/test_workbench.py` — Streamlit source-level and state helper smoke tests.
- Create: `tests/test_desktop.py` — desktop state and import-safe entry point tests.

### Task 1: Shared demand-result domain model

**Files:**
- Create: `core/demand_models.py`
- Create: `tests/test_demand_workbook.py`

- [ ] **Step 1: Write failing tests for the deterministic result contract**

```python
from core.demand_workbook import create_demo_optimization, example_demand_dataset


def test_demo_optimization_has_fixed_before_after_counts():
    result = create_demo_optimization(example_demand_dataset(), "DQN-GNN")

    assert result.before_conflict_count == 10
    assert result.after_conflict_count == 3
    assert len(result.suggestions) == len(result.source_frame)
    assert sum("建议调整为" in value for value in result.suggestions.values()) == 7


def test_every_suggestion_is_a_completed_user_facing_value():
    result = create_demo_optimization(example_demand_dataset(), "遗传算法")

    assert set(result.suggestions.values()) <= {
        "保持原工作频率",
        *{value for value in result.suggestions.values() if value.startswith("建议调整为 ")},
    }
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python -m pytest tests/test_demand_workbook.py -v`

Expected: FAIL because `core.demand_workbook` does not exist.

- [ ] **Step 3: Define the shared models in `core/demand_models.py`**

```python
from dataclasses import dataclass
from typing import Mapping

import pandas as pd


@dataclass(frozen=True)
class DemandConflictPair:
    left_row: int
    right_row: int
    left_name: str
    right_name: str
    is_conflict: bool


@dataclass(frozen=True)
class DemandDataset:
    frame: pd.DataFrame
    source_bytes: bytes | None
    sheet_name: str
    header_row: int


@dataclass(frozen=True)
class DemandOptimizationResult:
    algorithm_name: str
    dataset: DemandDataset
    before_pairs: tuple[DemandConflictPair, ...]
    after_pairs: tuple[DemandConflictPair, ...]
    suggestions: Mapping[int, str]
    before_conflict_count: int
    after_conflict_count: int

    @property
    def source_frame(self) -> pd.DataFrame:
        return self.dataset.frame

    @property
    def reduction_pct(self) -> float:
        return round((self.before_conflict_count - self.after_conflict_count) / self.before_conflict_count * 100, 1)
```

- [ ] **Step 4: Implement `create_demo_optimization` minimally in `core/demand_workbook.py`**

```python
DEMAND_COLUMNS = ("序号", "用频单位", "型号名称", "配装平台", "装备数量", "用途", "频段范围", "工作频率", "频点数量", "发射带宽", "发射功率", "建议")
DEMO_ALGORITHMS = ("贪婪算法", "DQN-GNN", "遗传算法", "禁忌搜索")

def create_demo_optimization(dataset: DemandDataset, algorithm_name: str) -> DemandOptimizationResult:
    validate_demand_frame(dataset.frame)
    if algorithm_name not in DEMO_ALGORITHMS:
        raise ValueError(f"不支持的算法：{algorithm_name}")
    rows = dataset.frame.reset_index(drop=True).copy()
    before_pairs = tuple(_pair_rows(rows, 10, True))
    after_pairs = tuple(_pair_rows(rows, 3, True))
    suggestions = {
        index: _suggestion_for_row(rows.iloc[index], index < 7)
        for index in range(len(rows))
    }
    normalized = DemandDataset(rows, dataset.source_bytes, dataset.sheet_name, dataset.header_row)
    return DemandOptimizationResult(algorithm_name, normalized, before_pairs, after_pairs, suggestions, 10, 3)
```

`_pair_rows` must cycle through unique row pairs without duplicate unordered pairs; `_suggestion_for_row` must return seven deterministic `建议调整为 <range>` values derived from the row's `工作频率`, and `保持原工作频率` for all remaining rows.

- [ ] **Step 5: Run the focused test to verify it passes**

Run: `python -m pytest tests/test_demand_workbook.py -v`

Expected: PASS.

- [ ] **Step 6: Commit the shared domain model**

```bash
git add core/demand_models.py core/demand_workbook.py tests/test_demand_workbook.py
git commit -m "feat: add demand optimization demo domain"
```

### Task 2: Demand workbook import, validation, and result export

**Files:**
- Modify: `core/demand_workbook.py`
- Modify: `tests/test_demand_workbook.py`

- [ ] **Step 1: Add failing tests for the 12-column workbook and download bytes**

```python
from io import BytesIO

from openpyxl import load_workbook

from core.demand_workbook import (
    DEMAND_COLUMNS,
    export_optimized_workbook,
    parse_demand_upload,
)


def test_parse_demand_upload_requires_all_expected_columns(tmp_path):
    bad_path = tmp_path / "bad.xlsx"
    example_demand_dataframe().drop(columns=["建议"]).to_excel(bad_path, index=False)

    with pytest.raises(ValueError, match="缺少必填列.*建议"):
        parse_demand_upload(bad_path.read_bytes(), bad_path.name)


def test_exported_workbook_fills_only_suggestion_column():
    result = create_demo_optimization(example_demand_dataset(), "禁忌搜索")
    output = export_optimized_workbook(result)
    workbook = load_workbook(BytesIO(output), data_only=True)
    sheet = workbook.active

    assert [sheet.cell(1, column).value for column in range(1, 13)] == list(DEMAND_COLUMNS)
    assert sheet.cell(result.dataset.header_row + 1, 12).value.startswith(("保持原工作频率", "建议调整为 "))
    assert sheet.cell(result.dataset.header_row + 1, 3).value == result.source_frame.iloc[0]["型号名称"]


def test_export_preserves_the_uploaded_title_and_header_rows(tmp_path):
    source = tmp_path / "需求表.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame([["xx用频需求表（数据未验证）"]]).to_excel(writer, index=False, header=False)
        example_demand_dataframe().to_excel(writer, index=False, startrow=1)
    dataset = parse_demand_upload(source.read_bytes(), source.name)
    output = export_optimized_workbook(create_demo_optimization(dataset, "贪婪算法"))
    sheet = load_workbook(BytesIO(output), data_only=True).active

    assert sheet.cell(1, 1).value == "xx用频需求表（数据未验证）"
    assert sheet.cell(2, 12).value == "建议"
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python -m pytest tests/test_demand_workbook.py -v`

Expected: FAIL because upload and export functions are missing.

- [ ] **Step 3: Implement workbook functions**

```python
def parse_demand_upload(data: bytes, filename: str) -> DemandDataset:
    if Path(filename).suffix.lower() != ".xlsx":
        raise ValueError("当前仅支持 Excel（.xlsx）用频需求表")
    workbook = load_workbook(BytesIO(data), read_only=True, data_only=False)
    sheet = workbook.active
    header_row = _find_header_row(sheet, "建议")
    frame = pd.read_excel(BytesIO(data), sheet_name=sheet.title, header=header_row - 1)
    return DemandDataset(validate_demand_frame(frame), data, sheet.title, header_row)


def validate_demand_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in DEMAND_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"缺少必填列：{', '.join(missing)}")
    return frame.loc[:, DEMAND_COLUMNS].copy()


def export_optimized_workbook(result: DemandOptimizationResult) -> bytes:
    output = BytesIO()
    if result.dataset.source_bytes:
        workbook = load_workbook(BytesIO(result.dataset.source_bytes))
        sheet = workbook[result.dataset.sheet_name]
        suggestion_column = _column_index(sheet, result.dataset.header_row, "建议")
        for index, suggestion in result.suggestions.items():
            sheet.cell(result.dataset.header_row + index + 1, suggestion_column).value = suggestion
        workbook.save(output)
        return output.getvalue()
    result.source_frame.assign(建议=[result.suggestions[index] for index in range(len(result.source_frame))]).to_excel(output, index=False)
    return output.getvalue()
```

`example_demand_dataframe()` must return 23 rows with the exact `DEMAND_COLUMNS` order, copied from the real workbook's field semantics. `example_demand_dataset()` wraps that frame with no source bytes and a header row of 1. `_find_header_row` must scan the first 10 rows and raise `ValueError("未找到包含“建议”列的字段行")` if it cannot find the header; `_column_index` must find the exact header name in that row. When exporting a real imported workbook, preserve the original title row, styles, merges, column widths, and all non-`建议` cell values.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `python -m pytest tests/test_demand_workbook.py -v`

Expected: PASS.

- [ ] **Step 5: Commit the workbook workflow**

```bash
git add core/demand_workbook.py tests/test_demand_workbook.py
git commit -m "feat: add demand workbook import and export"
```

### Task 3: Replace the Streamlit multipage UI with the single workbench

**Files:**
- Create: `ui/workbench.py`
- Modify: `ui/shell.py`
- Modify: `app.py`
- Modify: `assets/theme.css`
- Create: `tests/test_workbench.py`

- [ ] **Step 1: Write failing Streamlit-workbench smoke tests**

```python
from pathlib import Path


def test_app_renders_the_single_workbench_only():
    source = Path("app.py").read_text(encoding="utf-8")
    assert "render_workbench" in source
    assert "render_bottom_navigation" not in source
    assert "pages import" not in source


def test_workbench_includes_required_actions_and_result_comparison():
    source = Path("ui/workbench.py").read_text(encoding="utf-8")
    for label in ("导入用频需求表", "生成模拟数据", "启动频率优化", "下载结果 Excel", "优化前后冲突对比"):
        assert label in source
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python -m pytest tests/test_workbench.py -v`

Expected: FAIL because `ui/workbench.py` and the new app entry are absent.

- [ ] **Step 3: Implement session state and the workbench renderer**

In `ui/shell.py`, replace old page-routing defaults with `demand_frame`, `demand_source_name`, `demand_result`, `is_optimizing`, and `optimization_started_at`. Keep `load_theme()` and render a static header only.

In `ui/workbench.py`, create the one-page flow:

```python
def render_workbench() -> None:
    render_header()
    left, center, right = st.columns([24, 43, 33], gap="medium")
    with left:
        _render_parameters()
        _render_data_controls()
        _render_algorithm_controls()
    with center:
        _render_conflict_workspace()
    with right:
        _render_result_output()
```

`_render_data_controls()` must load `parse_demand_upload(uploaded.getvalue(), uploaded.name)` on upload and `example_demand_dataset()` for mock data, clear prior results, and immediately set a pre-optimization display result. `_render_algorithm_controls()` must disable its button until data exists, render three progress phases with `st.progress`, wait three seconds in total, call `create_demo_optimization`, then rerun. `_render_conflict_workspace()` must show before/after metrics, radio buttons, paginated pair rows, red links for conflicts, and green state for resolved pairs. `_render_result_output()` must hide the table, show counts, offer `st.download_button` with `export_optimized_workbook`, and draw the 10-to-3 comparison with Plotly or native Streamlit metrics.

Update `app.py` to only initialize state, load the theme, and call `render_workbench()`. Update `assets/theme.css` with the dark-blue gradient, panel borders, accessible text contrast, and card classes used by the new renderer.

- [ ] **Step 4: Run focused and existing app tests**

Run: `python -m pytest tests/test_workbench.py tests/test_app_smoke.py -v`

Expected: PASS after updating obsolete multipage assertions in `tests/test_app_smoke.py` to assert `st.set_page_config` remains first and multipage navigation is absent.

- [ ] **Step 5: Commit the Streamlit workbench**

```bash
git add app.py ui/shell.py ui/workbench.py assets/theme.css tests/test_workbench.py tests/test_app_smoke.py
git commit -m "feat: replace web flow with frequency workbench"
```

### Task 4: Restore and align the PySide6 desktop workbench

**Files:**
- Create: `desktop/__init__.py`
- Create: `desktop/state.py`
- Create: `desktop/main_window.py`
- Create: `desktop/theme.py`
- Create: `desktop_app.py`
- Create: `tests/test_desktop.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write failing desktop state and entry-point tests**

```python
from desktop.state import DesktopState
from core.demand_workbook import example_demand_dataset


def test_desktop_state_uses_the_shared_workbook_result():
    state = DesktopState()
    state.load_dataset(example_demand_dataset(), "系统模拟数据")
    result = state.optimize("DQN-GNN")

    assert result.before_conflict_count == 10
    assert result.after_conflict_count == 3
    assert state.source_name == "系统模拟数据"


def test_desktop_entrypoint_is_import_safe():
    import desktop_app

    assert callable(desktop_app.main)
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python -m pytest tests/test_desktop.py -v`

Expected: FAIL because the desktop package is absent from the current branch.

- [ ] **Step 3: Implement `DesktopState` on the shared domain layer**

```python
@dataclass
class DesktopState:
    scenario: ScenarioParameters | None = None
    dataset: DemandDataset | None = None
    source_name: str = "未导入"
    result: DemandOptimizationResult | None = None

    def load_dataset(self, dataset: DemandDataset, source_name: str) -> None:
        self.dataset = dataset
        self.source_name = source_name
        self.result = None

    def optimize(self, algorithm_name: str) -> DemandOptimizationResult:
        if self.dataset is None:
            raise ValueError("请先导入或生成用频需求数据")
        self.result = create_demo_optimization(self.dataset, algorithm_name)
        return self.result
```

- [ ] **Step 4: Implement the single-window desktop UI**

`desktop/main_window.py` must create one `QMainWindow` with a header and `QHBoxLayout` using 24/43/33 stretch factors. Implement:

```python
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.state = DesktopState()
        self.setMinimumSize(1180, 720)
        self._build_left_controls()
        self._build_conflict_panel()
        self._build_result_panel()
        self._refresh()
```

The left panel must have collapsible parameter controls, `QFileDialog` import, mock generation, algorithm selection and a disabled-until-data start button. Use `QTimer.singleShot(3000, finish_optimization)` so the window stays responsive while showing a progress bar. The center panel must render pair rows using Qt layouts with colored labels and red/green link indicators; it must support before/after switching and pagination. The right panel must show result file status, download via `QFileDialog.getSaveFileName`, and a two-row before/after horizontal bar comparison. `desktop/theme.py` must use the same dark-blue gradient, contrast, borders, button, and status colors as the web version. `desktop_app.py` must only create `QApplication`, show `MainWindow`, and return `app.exec()`.

- [ ] **Step 5: Add dependency and run desktop tests**

Add this exact line to `requirements.txt`:

```text
PySide6-Essentials>=6.8,<7
```

Run: `python -m pytest tests/test_desktop.py -v`

Expected: PASS; tests must not create a visible desktop window.

- [ ] **Step 6: Commit the desktop workbench**

```bash
git add desktop desktop_app.py tests/test_desktop.py requirements.txt
git commit -m "feat: add aligned desktop frequency workbench"
```

### Task 5: Documentation, regression verification, and code-only delivery

**Files:**
- Modify: `README.md`
- Modify: `tests/test_io.py` only if existing link-format assertions conflict with the new isolated demand-workbook functions.

- [ ] **Step 1: Update README commands and workflow**

Document both launch commands:

```bash
streamlit run app.py
python desktop_app.py
```

Document the accepted 12-column workbook, three-step flow (import/mock → start algorithm → download output), and that DQN-GNN/遗传算法/禁忌搜索 are currently deterministic demonstration adapters.

- [ ] **Step 2: Run targeted tests**

Run: `python -m pytest tests/test_demand_workbook.py tests/test_workbench.py tests/test_desktop.py -v`

Expected: PASS.

- [ ] **Step 3: Run the full suite and syntax checks**

Run: `python -m compileall app.py desktop_app.py core ui desktop`

Expected: no compilation errors.

Run: `python -m pytest -q`

Expected: PASS with no failures.

- [ ] **Step 4: Manually smoke test both launch paths**

Run: `streamlit run app.py --server.headless true`

Verify: the page opens as one three-column workbench; upload/mock data presents 10 original conflicts; start produces 3 optimized conflicts; the result download is enabled.

Run: `python desktop_app.py`

Verify: the native window opens with three columns; mock data and DQN-GNN enable a 3-second progress state; after completion the right panel can save an Excel result.

- [ ] **Step 5: Commit only source, tests, and README**

```bash
git add README.md app.py assets core desktop desktop_app.py requirements.txt tests ui
git commit -m "docs: document single-page frequency workflow"
```

Do not stage `.superpowers/` or `docs/superpowers/`; they remain local design and planning artifacts in accordance with the user's code-only delivery preference.
