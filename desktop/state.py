from dataclasses import dataclass

from core.demand_models import DemandDataset, DemandOptimizationResult
from core.demand_workbook import create_demo_optimization


@dataclass
class DesktopState:
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
