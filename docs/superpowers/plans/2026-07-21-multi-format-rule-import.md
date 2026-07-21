# Multi-format Rule Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import demand data and protection rules independently in multiple formats, then calculate through one visible start action.

**Architecture:** Add one focused protection-rule parser that converts supported sources into immutable normalized rules. The calculation and both user interfaces consume the same rule set; they enable calculation only after valid demand and rule sources exist.

**Tech Stack:** Python, pandas, openpyxl, python-docx, Streamlit, PySide6, pytest.

---

### Task 1: Add normalized protection-rule parsing

**Files:**
- Create: `core/protection_rules.py`
- Modify: `core/demand_models.py`
- Test: `tests/test_protection_rules.py`

- [ ] **Step 1: Write the failing parser tests**

```python
def test_parses_mixed_unit_ranges_and_tolerance():
    rules = parse_protection_upload(
        b"频率 | 用途 | 保护要求\n2523-2654MHz, 1.2-1.321GHz | 航空通信 | 禁止占用\n13525±10kHz | 信标 | 严格保护\n",
        "rules.txt",
    )
    assert rules.valid_count == 3
    assert rules.rules[0].lower_mhz == 2523
    assert rules.rules[1].upper_mhz == 1321
    assert rules.rules[2].lower_mhz == pytest.approx(13.515)

def test_parses_json_and_reports_invalid_entries():
    rules = parse_protection_upload(
        b'[{"frequency":"406-406.1MHz"},{"frequency":"bad"}]', "rules.json"
    )
    assert rules.valid_count == 1
    assert rules.invalid_count == 1
```

- [ ] **Step 2: Verify the tests fail**

Run: `pytest tests/test_protection_rules.py -v`  
Expected: FAIL because `core.protection_rules` does not exist.

- [ ] **Step 3: Implement normalized parser models and dispatch**

Add `ProtectionRule(expression, lower_mhz, upper_mhz, category="", requirement="")` plus `ProtectionRuleSet(rules, source_name, warnings=())` in `core/demand_models.py`; the rule set exposes `valid_count` and `invalid_count`. Implement `parse_protection_upload(data, filename)` in `core/protection_rules.py` with `.docx`, `.xlsx`, `.xls`, `.csv`, `.json`, and `.txt` dispatch. Normalize `a-bGHz/MHz/kHz`, comma-separated values, points, and `center±tolerance` to MHz. Read Word paragraphs and tables; require a `频率` or `frequency` column in tabular sources; collect invalid expressions as warnings and raise only when zero valid rules remain.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_protection_rules.py -v`  
Expected: PASS.

Run: `git add core/demand_models.py core/protection_rules.py tests/test_protection_rules.py && git commit -m "feat: parse multi-format protection rules"`

### Task 2: Generalize demand imports and calculation input

**Files:**
- Modify: `core/demand_workbook.py`
- Modify: `core/demand_models.py`
- Modify: `tests/test_demand_workbook.py`

- [ ] **Step 1: Write failing behavior tests**

```python
def test_parse_demand_upload_accepts_csv():
    dataset = parse_demand_upload(example_demand_dataframe().to_csv(index=False).encode(), "需求.csv")
    assert len(dataset.frame) == 23

def test_optimization_records_protection_rule_count():
    result = create_demo_optimization(example_demand_dataset(), example_protection_rules())
    assert result.protection_rule_count > 0
    assert result.algorithm_name == "频率指配计算"
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/test_demand_workbook.py -v`  
Expected: FAIL because CSV is rejected and calculation has no rule input.

- [ ] **Step 3: Implement the shared calculation interface**

Accept `.xlsx`, `.xls`, and `.csv` in `parse_demand_upload`, preserving original bytes only for `.xlsx` export. Change the signature to `create_demo_optimization(dataset, protection_rules)`, set `algorithm_name="频率指配计算"`, add `protection_rule_count` to `DemandOptimizationResult`, and provide `example_protection_rules()` for mock operation. Preserve the current demonstration counts (10 before, 3 after) while using matching protection ranges in adjustment text.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_demand_workbook.py tests/test_protection_rules.py -v`  
Expected: PASS.

Run: `git add core/demand_models.py core/demand_workbook.py tests/test_demand_workbook.py && git commit -m "feat: use protection rules in frequency calculation"`

### Task 3: Implement dual uploads in Streamlit

**Files:**
- Modify: `ui/workbench.py`
- Modify: `app.py` if it owns session defaults
- Modify: `tests/test_workbench.py`

- [ ] **Step 1: Write a failing UI contract test**

```python
def test_workbench_uses_two_imports_without_algorithm_selection():
    source = Path("ui/workbench.py").read_text(encoding="utf-8")
    assert "导入用频需求数据" in source
    assert "导入禁用保护/规则数据" in source
    assert "DEMO_ALGORITHMS" not in source
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/test_workbench.py::test_workbench_uses_two_imports_without_algorithm_selection -v`  
Expected: FAIL because the current page shows algorithm selection.

- [ ] **Step 3: Implement web state and controls**

Store `protection_rules`, `protection_source_name`, and rule warnings in session state. Use demand formats `xlsx/xls/csv`, and rule formats `docx/xlsx/xls/csv/json/txt`, with independent source status lines. Enable `启动频率优化` only if both objects exist; call `create_demo_optimization(dataset, protection_rules)` and retain progress captions “读取双类数据 / 执行频率指配计算 / 生成结果文件”. Mock generation loads both input categories. Keep the center and result panels and add the parsed rule count to their context.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_workbench.py -v`  
Expected: PASS.

Run: `git add ui/workbench.py app.py tests/test_workbench.py && git commit -m "feat: add dual data imports to web workbench"`

### Task 4: Align the PySide6 application

**Files:**
- Modify: `desktop/state.py`
- Modify: `desktop/main_window.py`
- Modify: `tests/test_desktop.py`

- [ ] **Step 1: Write a failing desktop-state test**

```python
def test_desktop_state_requires_both_data_sources():
    state = DesktopState()
    state.load_dataset(example_demand_dataset(), "需求.xlsx")
    assert not state.is_ready
    with pytest.raises(ValueError, match="禁用保护"):
        state.optimize()
    state.load_protection_rules(example_protection_rules(), "规则.docx")
    assert state.is_ready
    assert state.optimize().protection_rule_count > 0
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/test_desktop.py::test_desktop_state_requires_both_data_sources -v`  
Expected: FAIL because the state has no protection-rule source.

- [ ] **Step 3: Implement desktop parity**

Add rule source fields, `load_protection_rules`, `is_ready`, and parameterless `optimize()` to `DesktopState`. Remove the algorithm `QComboBox`; add two separate `QFileDialog` actions with the web-equivalent filters and independent status labels. Enable the primary button from `state.is_ready`; mock data loads both sources. Reuse the current progress experience and show rule count in result context.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_desktop.py -v`  
Expected: PASS.

Run: `git add desktop/state.py desktop/main_window.py tests/test_desktop.py && git commit -m "feat: align desktop dual data imports"`

### Task 5: Verify the whole application

**Files:** Modify only the files above if a test identifies a defect.

- [ ] **Step 1: Run complete suite**

Run: `pytest -q`  
Expected: all tests pass.

- [ ] **Step 2: Validate final state**

Run: `git status --short`  
Expected: no tracked implementation changes; do not stage unrelated `.superpowers/`.

- [ ] **Step 3: Commit only necessary test-driven repair**

Run: `git add core desktop ui tests && git commit -m "fix: verify dual input frequency workflow"`
