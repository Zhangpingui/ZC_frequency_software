# 战场频谱智能指配演示系统

基于 Streamlit 的本地频谱工程演示系统，覆盖任务参数配置、链路拓扑建模、冲突检测与频率优化。界面和计算均可离线运行，不依赖网络资源。

## 安装与启动

建议使用 Python 3.11 或更高版本。

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

浏览器默认打开 `http://localhost:8501`。页面底部提供三步导航，会话数据保存在 Streamlit Session State 中；刷新浏览器或服务重启后需重新加载。

### 桌面应用

桌面版使用 PySide6 原生窗口，保留参数配置、物理拓扑、冲突计算和底部导航。macOS 可双击 `run_desktop.command`，或执行：

```bash
.venv/bin/python desktop_app.py
```

物理拓扑页可直接生成模拟数据，也可以导出 `模拟频谱链路数据.xlsx` 后重新上传测试。模拟数据包含 30 台设备（A–AD）、15 条链路和分布于 1–9 GHz 的多组频率冲突。

## 使用流程

1. **参数配置**：编辑七项任务指标，系统通过 `validate_scenario` 校验并保存。
2. **物理拓扑**：上传 `.xlsx`、`.csv` 或 `.json` 数据，亦可生成模拟数据和下载模拟 Excel；左侧画布显示设备名称、二维坐标与通信链路。
3. **冲突计算**：设置空间干扰阈值和保护频差，检测当前方案冲突，再选择算法优化频率。画布支持优化前/优化后切换、冲突过滤、链路搜索和分页，结果可导出 CSV。

## 数据字段

每行代表一条通信链路。字段可使用下列英文名，必填字段也支持模板中的对应中文别名。

| 字段 | 含义 | 必填 | 默认值/约束 |
|---|---|---:|---|
| `link_id` | 链路 ID | 是 | 非空 |
| `tx_id` | 发射机 ID | 是 | 非空 |
| `tx_x_km`, `tx_y_km` | 发射机坐标 | 是 | 数值，单位 km |
| `rx_id` | 接收机 ID | 是 | 非空 |
| `rx_x_km`, `rx_y_km` | 接收机坐标 | 是 | 数值，单位 km |
| `frequency_ghz` | 使用频率 | 是 | 1–9 GHz |
| `bandwidth_mhz` | 信号带宽 | 否 | 默认 20 MHz |
| `tx_power_dbm` | 发射功率 | 否 | 默认 30 dBm |

中文别名为：`链路ID`、`发射机ID`、`发射机X`、`发射机Y`、`接收机ID`、`接收机X`、`接收机Y`、`使用频率GHz`、`带宽MHz`、`发射功率dBm`。

## 算法说明

- **贪婪算法**：当前可执行求解器，按冲突度排序并从 1–9 GHz 候选频点中选择局部最优指配。
- **DQN-GNN、遗传算法、禁忌搜索**：演示模式。为保证界面流程和结果结构完整，当前由贪婪内核生成模拟结果，界面会明确标记“演示模式”，不代表对应算法的真实训练或搜索性能。

冲突判定同时考虑跨链路空间距离、信号带宽与保护频差；固定红色连线表示同频或邻频冲突。

## 验证

```bash
python3 -m compileall app.py desktop_app.py core desktop pages ui visualization
python3 -m pytest
```
