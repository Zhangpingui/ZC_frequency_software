from core.solvers import GreedySolver, get_solver


def test_solver_registry_accepts_ui_greedy_label():
    assert isinstance(get_solver("贪婪算法"), GreedySolver)
from core.solvers.demo import DemoSolver
from core.solvers.greedy import GreedySolver


def test_greedy_does_not_increase_conflicts(link_factory):
    links = [link_factory("a", 2.0), link_factory("b", 2.0), link_factory("c", 2.0)]
    result = GreedySolver().solve(links, distance_threshold_km=10)
    assert result.algorithm_name == "贪心算法"
    assert result.after_metrics.conflict_count <= result.before_metrics.conflict_count
    assert not result.is_demo
    assert all(1.0 <= link.frequency_ghz <= 9.0 for link in result.links)


def test_demo_solvers_are_explicit_and_deterministic(link_factory):
    links = [link_factory("a", 2.0), link_factory("b", 2.0)]
    for name in ("DQN-GNN", "遗传算法", "禁忌搜索"):
        solver = get_solver(name)
        assert isinstance(solver, DemoSolver)
        first = solver.solve(links, distance_threshold_km=10)
        second = solver.solve(links, distance_threshold_km=10)
        assert first.is_demo and second.is_demo
        assert first.algorithm_name == name
        assert [link.frequency_ghz for link in first.links] == [link.frequency_ghz for link in second.links]


def test_get_solver_rejects_unknown_name():
    try:
        get_solver("unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown solver must be rejected")
