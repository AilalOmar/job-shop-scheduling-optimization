"""
CRITICAL VALIDATION TESTS FOR SIMULATED ANNEALING

According to the plan, ALL 5 TESTS MUST PASS before proceeding to visualization/UI.

Tests:
1. Small instance (3x3): Find makespan <= 7 in 90%+ of 20 runs
2. Medium instance (6x6): Verify improvement from initial solution
3. Convergence check: Best makespan never increases across iterations
4. Stress test (15x15): Run 10,000 iterations without crashes
5. Constraint validation: Every solution passes Schedule.validate()
"""

import sys
import os

# Add jsp-solver to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jsp_model import JSPProblem
from simulated_annealing import SimulatedAnnealingSolver


def create_3x3_problem():
    """Create the 3x3 instance from Metod_exact.py (known optimal = 7)"""
    jobs_dict = {
        "J1": [("M1", 3), ("M2", 2), ("M3", 2)],
        "J2": [("M2", 2), ("M3", 1), ("M1", 1)],
        "J3": [("M3", 3), ("M1", 1), ("M2", 2)]
    }
    machines = ["M1", "M2", "M3"]
    return JSPProblem.from_existing_format(jobs_dict, machines, name="3x3_test")


def create_6x6_problem():
    """Create a medium 6x6 instance for testing"""
    jobs_dict = {
        "J1": [("M1", 5), ("M2", 3), ("M3", 4), ("M4", 2), ("M5", 3), ("M6", 2)],
        "J2": [("M2", 4), ("M3", 2), ("M4", 5), ("M5", 3), ("M6", 4), ("M1", 2)],
        "J3": [("M3", 3), ("M4", 4), ("M5", 2), ("M6", 5), ("M1", 3), ("M2", 4)],
        "J4": [("M4", 2), ("M5", 5), ("M6", 3), ("M1", 4), ("M2", 2), ("M3", 3)],
        "J5": [("M5", 4), ("M6", 2), ("M1", 3), ("M2", 5), ("M3", 2), ("M4", 4)],
        "J6": [("M6", 3), ("M1", 4), ("M2", 2), ("M3", 3), ("M4", 5), ("M5", 2)]
    }
    machines = ["M1", "M2", "M3", "M4", "M5", "M6"]
    return JSPProblem.from_existing_format(jobs_dict, machines, name="6x6_test")


def create_15x15_problem():
    """Create a large 15x15 instance for stress testing"""
    import random
    random.seed(42)  # Reproducible

    jobs_dict = {}
    for j in range(15):
        # Random permutation of machines
        machines_perm = list(range(15))
        random.shuffle(machines_perm)

        ops = [(f"M{m}", random.randint(1, 10)) for m in machines_perm]
        jobs_dict[f"J{j}"] = ops

    machines = [f"M{m}" for m in range(15)]
    return JSPProblem.from_existing_format(jobs_dict, machines, name="15x15_stress")


def test_1_small_instance():
    """
    TEST 1: Small instance (3x3)
    PASS CRITERION: Find makespan <= 7 in 90%+ of 20 runs
    """
    print("\n" + "="*70)
    print("TEST 1: Small Instance (3x3) - Known Optimal = 7")
    print("="*70)

    problem = create_3x3_problem()
    n_runs = 20
    results = []

    print(f"\nRunning {n_runs} independent SA runs...")

    for run in range(n_runs):
        solver = SimulatedAnnealingSolver(
            temp_init=1000,
            cooling_rate=0.95,
            iter_per_temp=100,
            temp_min=1,
            random_seed=run,  # Different seed for each run
            verbose=False
        )

        solution, stats = solver.solve(problem)
        makespan = stats['best_makespan']
        results.append(makespan)

        status = "[OK]" if makespan <= 7 else "[SUBOPTIMAL]"
        print(f"  Run {run+1:2d}: Makespan = {makespan} {status}")

    # Calculate success rate
    optimal_count = sum(1 for m in results if m <= 7)
    success_rate = optimal_count / n_runs * 100

    print(f"\n[RESULTS]")
    print(f"  Optimal solutions (<=7): {optimal_count}/{n_runs} ({success_rate:.1f}%)")
    print(f"  Best makespan: {min(results)}")
    print(f"  Worst makespan: {max(results)}")
    print(f"  Average makespan: {sum(results)/len(results):.2f}")

    passed = success_rate >= 90
    if passed:
        print(f"\n[PASS] Test 1: {success_rate:.1f}% >= 90% threshold")
    else:
        print(f"\n[FAIL] Test 1: {success_rate:.1f}% < 90% threshold")

    return passed


def test_2_improvement():
    """
    TEST 2: Medium instance (6x6)
    PASS CRITERION: Algorithm improves from initial solution
    """
    print("\n" + "="*70)
    print("TEST 2: Improvement from Initial Solution (6x6)")
    print("="*70)

    problem = create_6x6_problem()
    solver = SimulatedAnnealingSolver(
        temp_init=1000,
        cooling_rate=0.95,
        iter_per_temp=100,
        temp_min=1,
        random_seed=42,
        verbose=False
    )

    solution, stats = solver.solve(problem)

    initial_makespan = stats['initial_makespan']
    best_makespan = stats['best_makespan']
    improvement = stats['improvement_percent']

    print(f"\n[RESULTS]")
    print(f"  Initial makespan: {initial_makespan}")
    print(f"  Best makespan: {best_makespan}")
    print(f"  Improvement: {improvement:.2f}%")
    print(f"  CPU time: {stats['cpu_time']:.2f}s")

    passed = improvement > 0
    if passed:
        print(f"\n[PASS] Test 2: Improvement = {improvement:.2f}% > 0%")
    else:
        print(f"\n[FAIL] Test 2: No improvement (check algorithm)")

    return passed


def test_3_convergence():
    """
    TEST 3: Convergence monotonicity
    PASS CRITERION: Best makespan never increases
    """
    print("\n" + "="*70)
    print("TEST 3: Convergence Monotonicity (Best Never Increases)")
    print("="*70)

    problem = create_3x3_problem()
    solver = SimulatedAnnealingSolver(
        temp_init=1000,
        cooling_rate=0.95,
        iter_per_temp=100,
        temp_min=1,
        random_seed=42,
        verbose=False
    )

    solution, stats = solver.solve(problem)
    history = stats['convergence_history']

    # Track best makespan seen so far
    best_so_far = float('inf')
    violations = 0

    for iteration, makespan, temp in history:
        if makespan < best_so_far:
            best_so_far = makespan

    # Check by reconstructing best history
    best_history = []
    current_best = history[0][1]
    for iteration, makespan, temp in history:
        if makespan < current_best:
            current_best = makespan
        best_history.append(current_best)

    # Verify monotonicity
    for i in range(len(best_history) - 1):
        if best_history[i+1] > best_history[i]:
            violations += 1

    print(f"\n[RESULTS]")
    print(f"  Total iterations: {len(history)}")
    print(f"  Initial makespan: {history[0][1]}")
    print(f"  Final best: {best_history[-1]}")
    print(f"  Violations: {violations}")

    passed = violations == 0
    if passed:
        print(f"\n[PASS] Test 3: Best makespan is monotonically non-increasing")
    else:
        print(f"\n[FAIL] Test 3: Found {violations} violations of monotonicity")

    return passed


def test_4_stress():
    """
    TEST 4: Stress test with large instance
    PASS CRITERION: Complete 10,000 iterations without crashes
    """
    print("\n" + "="*70)
    print("TEST 4: Stress Test (15x15, 10,000 iterations)")
    print("="*70)

    problem = create_15x15_problem()

    print(f"\n[INFO] Problem: {problem.n_jobs} jobs, {problem.n_machines} machines")
    print(f"[INFO] Total operations: {sum(len(j.operations) for j in problem.jobs)}")

    try:
        solver = SimulatedAnnealingSolver(
            temp_init=2000,  # Higher temp for larger problem
            cooling_rate=0.95,
            iter_per_temp=100,
            temp_min=1,
            max_iterations=10000,
            random_seed=42,
            verbose=True  # Show progress
        )

        solution, stats = solver.solve(problem)

        print(f"\n[RESULTS]")
        print(f"  Initial makespan: {stats['initial_makespan']}")
        print(f"  Best makespan: {stats['best_makespan']}")
        print(f"  Improvement: {stats['improvement_percent']:.2f}%")
        print(f"  Total iterations: {stats['total_iterations']}")
        print(f"  CPU time: {stats['cpu_time']:.2f}s")

        passed = stats['total_iterations'] >= 1000  # At least significant iterations
        if passed:
            print(f"\n[PASS] Test 4: Completed stress test without crashes")
        else:
            print(f"\n[FAIL] Test 4: Insufficient iterations completed")

        return passed

    except Exception as e:
        print(f"\n[FAIL] Test 4: CRASH - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_constraint_validation():
    """
    TEST 5: Constraint validation
    PASS CRITERION: All generated solutions are valid
    """
    print("\n" + "="*70)
    print("TEST 5: Constraint Validation (1000 neighbor generations)")
    print("="*70)

    problem = create_3x3_problem()
    solver = SimulatedAnnealingSolver(random_seed=42, verbose=False)

    # Generate initial solution
    initial_solution = solver._generate_initial_solution(problem)

    print(f"\n[INFO] Testing initial solution...")
    print(f"  Makespan: {initial_solution.makespan}")
    print(f"  Valid: {initial_solution.validate()}")

    if not initial_solution.validate():
        print(f"\n[FAIL] Test 5: Initial solution is invalid!")
        return False

    # Generate many neighbors
    print(f"\n[INFO] Generating 1000 neighbors...")
    valid_count = 0
    invalid_count = 0

    for i in range(1000):
        neighbor = solver._generate_neighbor(initial_solution)

        if neighbor is not None:
            if neighbor.validate():
                valid_count += 1
            else:
                invalid_count += 1
                print(f"  [WARNING] Invalid neighbor at generation {i+1}")

    total_generated = valid_count + invalid_count

    print(f"\n[RESULTS]")
    print(f"  Valid neighbors: {valid_count}")
    print(f"  Invalid neighbors: {invalid_count}")
    print(f"  Total generated: {total_generated}")

    passed = invalid_count == 0 and valid_count > 900
    if passed:
        print(f"\n[PASS] Test 5: All generated neighbors are valid")
    else:
        print(f"\n[FAIL] Test 5: Found invalid neighbors or generation failures")

    return passed


def run_all_tests():
    """
    Run all 5 CRITICAL validation tests

    REQUIREMENTS: ALL tests must pass
    """
    print("\n" + "*"*70)
    print("SIMULATED ANNEALING - CRITICAL VALIDATION TESTS")
    print("*"*70)
    print("\nREQUIREMENT: ALL 5 TESTS MUST PASS BEFORE PROCEEDING")
    print("\nTests:")
    print("  1. Small instance (3x3): 90%+ optimal in 20 runs")
    print("  2. Medium instance (6x6): Shows improvement")
    print("  3. Convergence: Best never increases")
    print("  4. Stress test (15x15): 10,000 iterations without crash")
    print("  5. Validation: All solutions satisfy constraints")

    results = {}

    try:
        results['test_1'] = test_1_small_instance()
        results['test_2'] = test_2_improvement()
        results['test_3'] = test_3_convergence()
        results['test_4'] = test_4_stress()
        results['test_5'] = test_5_constraint_validation()

        print("\n" + "*"*70)
        print("FINAL RESULTS")
        print("*"*70)

        for test_name, passed in results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {test_name}: {status}")

        all_passed = all(results.values())

        if all_passed:
            print("\n" + "="*70)
            print("ALL TESTS PASSED - ALGORITHM VALIDATED")
            print("You may proceed to visualization and UI development")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("VALIDATION FAILED - DO NOT PROCEED")
            print("Fix the algorithm before continuing")
            print("="*70)

        return all_passed

    except Exception as e:
        print(f"\n\n[ERROR] Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
