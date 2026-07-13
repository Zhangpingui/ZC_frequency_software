from core.solvers.base import Solver, SolverResult
from core.solvers.demo import DemoSolver
from core.solvers.greedy import GreedySolver


def get_solver(name: str) -> Solver:
    if name in {"贪心", "贪心算法", "贪婪算法", "Greedy"}:
        return GreedySolver()
    if name in {"DQN-GNN", "遗传算法", "禁忌搜索"}:
        return DemoSolver(name)
    raise ValueError(f"未知求解器: {name}")


__all__ = ["DemoSolver", "GreedySolver", "Solver", "SolverResult", "get_solver"]
