"""
Test script for jsp_model.py
Validates data structures and conversion from Metod_exact.py format
"""

import sys
import os

# Add jsp-solver to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jsp_model import JSPProblem, Job, Operation, Schedule

def test_from_existing_format():
    """Test conversion from Metod_exact.py format"""
    print("=" * 60)
    print("TEST 1: Converting from Metod_exact.py format")
    print("=" * 60)

    # Original format from Metod_exact.py
    jobs_dict = {
        "J1": [("M1", 3), ("M2", 2), ("M3", 2)],
        "J2": [("M2", 2), ("M3", 1), ("M1", 1)],
        "J3": [("M3", 3), ("M1", 1), ("M2", 2)]
    }
    machines = ["M1", "M2", "M3"]

    # Convert to new format
    problem = JSPProblem.from_existing_format(jobs_dict, machines, name="3x3_test")

    print(f"\n[OK] Created problem: {problem}")
    print(f"  - {problem.n_jobs} jobs")
    print(f"  - {problem.n_machines} machines")

    # Verify structure
    assert problem.n_jobs == 3, "Should have 3 jobs"
    assert problem.n_machines == 3, "Should have 3 machines"

    # Check Job 0 (was J1)
    job0 = problem.get_job(0)
    assert job0.n_operations == 3, "Job 0 should have 3 operations"
    assert job0.operations[0].machine_id == 0, "First op should be on M0 (was M1)"
    assert job0.operations[0].duration == 3, "First op duration should be 3"

    print("\n[OK] Data structure validation passed")
    print(f"  - Job 0: {job0}")
    for idx, op in enumerate(job0.operations):
        print(f"    Op {idx}: Machine {op.machine_id}, Duration {op.duration}")

    return problem


def test_json_serialization(problem):
    """Test JSON serialization round-trip"""
    print("\n" + "=" * 60)
    print("TEST 2: JSON Serialization Round-Trip")
    print("=" * 60)

    # Save to JSON
    json_path = "test_instance.json"
    problem.to_json(json_path)
    print(f"\n[OK] Saved to {json_path}")

    # Load from JSON
    loaded_problem = JSPProblem.from_json(json_path)
    print(f"[OK] Loaded from {json_path}")

    # Verify
    assert loaded_problem.n_jobs == problem.n_jobs
    assert loaded_problem.n_machines == problem.n_machines
    assert loaded_problem.name == problem.name

    print(f"\n[OK] Round-trip successful")
    print(f"  - Original: {problem}")
    print(f"  - Loaded: {loaded_problem}")

    # Clean up
    os.remove(json_path)

    return loaded_problem


def test_schedule_creation(problem):
    """Test schedule creation and validation"""
    print("\n" + "=" * 60)
    print("TEST 3: Schedule Creation")
    print("=" * 60)

    schedule = Schedule(problem)
    print(f"\n[OK] Created empty schedule")
    print(f"  - Makespan: {schedule.makespan}")
    print(f"  - Valid: {schedule.validate()}")

    # Create a simple schedule manually (KNOWN OPTIMAL = 7)
    # Job 0 (M0,3), (M1,2), (M2,2): Op0 [0-3], Op1 [3-5], Op2 [5-7]
    # Job 1 (M1,2), (M2,1), (M0,1): Op0 [0-2], Op1 [3-4], Op2 [6-7]
    # Job 2 (M2,3), (M0,1), (M1,2): Op0 [0-3], Op1 [4-5], Op2 [5-7]

    # Job 0
    schedule.set_operation_time(0, 0, 0, 3)   # M0: [0-3]
    schedule.set_operation_time(0, 1, 3, 5)   # M1: [3-5]
    schedule.set_operation_time(0, 2, 5, 7)   # M2: [5-7]

    # Job 1
    schedule.set_operation_time(1, 0, 0, 2)   # M1: [0-2]
    schedule.set_operation_time(1, 1, 3, 4)   # M2: [3-4]
    schedule.set_operation_time(1, 2, 6, 7)   # M0: [6-7]

    # Job 2
    schedule.set_operation_time(2, 0, 0, 3)   # M2: [0-3]
    schedule.set_operation_time(2, 1, 4, 5)   # M0: [4-5]
    schedule.set_operation_time(2, 2, 5, 7)   # M1: [5-7]

    print(f"\n[OK] Added operation times")
    print(f"  - Makespan: {schedule.makespan}")
    print(f"  - Valid: {schedule.validate()}")

    # Verify makespan (should be 7)
    assert schedule.makespan == 7, f"Expected makespan 7, got {schedule.makespan}"
    assert schedule.validate(), "Schedule should be valid"

    print(f"\n[OK] Schedule validation passed")

    # Test machine utilization
    utilization = schedule.get_machine_utilization()
    print(f"\n[OK] Machine utilization:")
    for machine_id, util in utilization.items():
        print(f"  - M{machine_id}: {util * 100:.1f}%")

    return schedule


def test_schedule_copy(schedule):
    """Test schedule copying"""
    print("\n" + "=" * 60)
    print("TEST 4: Schedule Copy")
    print("=" * 60)

    schedule_copy = schedule.copy()
    print(f"\n[OK] Created copy")
    print(f"  - Original makespan: {schedule.makespan}")
    print(f"  - Copy makespan: {schedule_copy.makespan}")

    assert schedule_copy.makespan == schedule.makespan
    assert schedule_copy.validate() == schedule.validate()

    # Modify copy - extend last operation to change makespan
    schedule_copy.set_operation_time(0, 2, 5, 10)  # Change M2 operation to end at 10
    print(f"\n[OK] Modified copy")
    print(f"  - Original makespan: {schedule.makespan}")
    print(f"  - Copy makespan (modified): {schedule_copy.makespan}")

    assert schedule_copy.makespan != schedule.makespan, "Copy should be independent"

    print(f"\n[OK] Copy independence verified")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("JSP MODEL TESTING SUITE")
    print("*" * 60)

    try:
        problem = test_from_existing_format()
        loaded_problem = test_json_serialization(problem)
        schedule = test_schedule_creation(loaded_problem)
        test_schedule_copy(schedule)

        print("\n" + "*" * 60)
        print("ALL TESTS PASSED [OK]")
        print("*" * 60)
        print()

        return True

    except AssertionError as e:
        print(f"\n\n[FAIL] TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
