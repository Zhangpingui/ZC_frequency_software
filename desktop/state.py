from dataclasses import dataclass

from core.demand_models import DemandDataset, DemandOptimizationResult, ProtectionRuleSet
from core.demand_workbook import create_demo_optimization


@dataclass
class DesktopState:
    dataset: DemandDataset | None = None
    source_name: str = "未导入"
    protection_rules: ProtectionRuleSet | None = None
    protection_source_name: str = "未导入"
    result: DemandOptimizationResult | None = None

    def load_dataset(self, dataset: DemandDataset, source_name: str) -> None:
        self.dataset = dataset
        self.source_name = source_name
        self.result = None

    def load_protection_rules(
        self, rules: ProtectionRuleSet, source_name: str
    ) -> None:
        self.protection_rules = rules
        self.protection_source_name = source_name
        self.result = None

    @property
    def is_ready(self) -> bool:
        return self.dataset is not None and self.protection_rules is not None

    def optimize(self) -> DemandOptimizationResult:
        if self.dataset is None:
            raise ValueError("请先导入或生成用频需求数据")
        if self.protection_rules is None:
            raise ValueError("请先导入或生成禁用保护/规则数据")
        self.result = create_demo_optimization(self.dataset, self.protection_rules)
        return self.result
