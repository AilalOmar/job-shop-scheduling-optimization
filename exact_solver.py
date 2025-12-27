"""
Exact Method for JSP using Complete Enumeration
Explores ALL possible orderings to find OPTIMAL solution
WARNING: Only feasible for small instances (max 4-5 jobs, 4-5 machines)
Based on Metod_exact.py
"""

from jsp_model import JSPProblem, Schedule, Operation
from typing import Dict, List, Tuple, Optional
import time
from itertools import permutations
import logging

logger = logging.getLogger(__name__)


class ExactSolver:
    """
    Exact solver using complete enumeration of all permutations
    Guarantees optimal solution but only feasible for small instances
    """

    def __init__(self, max_size=5):
        self.name = "Exact Enumeration"
        self.max_size = max_size

    def solve(self, problem: JSPProblem) -> Tuple[Schedule, dict]:
        """
        Solve JSP by enumerating all possible operation orderings on machines

        Returns:
            (Schedule, statistics)
        """
        # Check if problem is too large
        total_ops = sum(len(job.operations) for job in problem.jobs)
        ops_per_machine = {}
        for job in problem.jobs:
            for op in job.operations:
                if op.machine_id not in ops_per_machine:
                    ops_per_machine[op.machine_id] = 0
                ops_per_machine[op.machine_id] += 1

        max_ops = max(ops_per_machine.values())

        # Estimate complexity
        import math
        complexity = math.factorial(max_ops) ** problem.n_machines

        if problem.n_jobs > self.max_size or problem.n_machines > self.max_size:
            raise ValueError(
                f"Instance trop grande pour méthode exacte! "
                f"Maximum {self.max_size}x{self.max_size}, trouvé {problem.n_jobs}x{problem.n_machines}. "
                f"Complexité estimée: {complexity:,} permutations à tester."
            )

        if complexity > 1_000_000:
            raise ValueError(
                f"Complexité trop élevée: {complexity:,} permutations à tester. "
                f"Utilisez une instance plus petite ou l'algorithme glouton/recuit simulé."
            )

        start_time = time.time()

        # Get all operations for each machine
        machine_ops = {m: [] for m in range(problem.n_machines)}
        for job in problem.jobs:
            for op in job.operations:
                machine_ops[op.machine_id].append((job.job_id, op.operation_index))

        # Generate all permutations for each machine
        machine_permutations = {}
        for machine_id, ops in machine_ops.items():
            if len(ops) > 0:
                machine_permutations[machine_id] = list(permutations(ops))
            else:
                machine_permutations[machine_id] = [[]]

        # Calculate total number of combinations
        total_combinations = 1
        for machine_id, perms in machine_permutations.items():
            total_combinations *= len(perms)

        logger.info(f"Exploring {total_combinations:,} combinations...")

        # Enumerate all combinations
        best_schedule = None
        best_makespan = float('inf')
        valid_schedules = 0
        invalid_schedules = 0

        def generate_combinations(machine_ids, current_assignment):
            """Recursively generate all combinations"""
            nonlocal best_schedule, best_makespan, valid_schedules, invalid_schedules

            if not machine_ids:
                # All machines assigned, simulate this schedule
                schedule = Schedule(problem)
                schedule.machine_orders = current_assignment.copy()

                # Simulate
                try:
                    self._simulate_schedule(schedule, problem)
                    makespan = schedule.makespan
                    valid_schedules += 1

                    if makespan < best_makespan:
                        best_makespan = makespan
                        best_schedule = schedule.copy()
                except:
                    # Invalid schedule (deadlock)
                    invalid_schedules += 1
                return

            # Get next machine
            machine_id = machine_ids[0]
            remaining = machine_ids[1:]

            # Try all permutations for this machine
            for perm in machine_permutations[machine_id]:
                current_assignment[machine_id] = list(perm)
                generate_combinations(remaining, current_assignment)

        # Start enumeration
        machine_ids = list(machine_permutations.keys())
        generate_combinations(machine_ids, {})

        cpu_time = time.time() - start_time

        if best_schedule is None:
            raise RuntimeError("Aucune solution valide trouvée!")

        # Statistics
        stats = {
            'algorithm': 'Exact Enumeration',
            'makespan': best_makespan,
            'cpu_time': cpu_time,
            'total_combinations': total_combinations,
            'valid_schedules': valid_schedules,
            'invalid_schedules': invalid_schedules,
            'optimal': True
        }

        logger.info(f"Optimal makespan: {best_makespan} (explored {total_combinations:,} combinations in {cpu_time:.2f}s)")

        return best_schedule, stats

    def _simulate_schedule(self, schedule: Schedule, problem: JSPProblem) -> None:
        """
        Simulate schedule execution to calculate operation times
        Adapted from Metod_exact.py
        """
        # Track state
        job_time = {j: 0 for j in range(problem.n_jobs)}
        machine_time = {m: 0 for m in range(problem.n_machines)}
        job_next_op = {j: 0 for j in range(problem.n_jobs)}

        # Process operations in machine order
        total_ops = sum(len(job.operations) for job in problem.jobs)
        scheduled_count = 0
        max_iterations = total_ops * 10  # Safety limit

        for iteration in range(max_iterations):
            progress_made = False

            # Try to schedule operations on each machine
            for machine_id in range(problem.n_machines):
                machine_order = schedule.machine_orders.get(machine_id, [])

                # Find next unscheduled operation for this machine
                for job_id, op_idx in machine_order:
                    # Check if already scheduled
                    if (job_id, op_idx) in schedule.operation_times:
                        continue

                    # Check if this is the next operation for the job
                    if job_next_op[job_id] != op_idx:
                        continue  # Not ready yet

                    job = problem.get_job(job_id)
                    operation = job.operations[op_idx]

                    # Can schedule: job is ready and machine is ready
                    start = max(job_time[job_id], machine_time[machine_id])
                    end = start + operation.duration

                    # Schedule it
                    schedule.operation_times[(job_id, op_idx)] = (start, end)
                    job_time[job_id] = end
                    machine_time[machine_id] = end
                    job_next_op[job_id] += 1
                    scheduled_count += 1
                    progress_made = True
                    break  # Move to next machine

            if scheduled_count == total_ops:
                # All operations scheduled
                break

            if not progress_made:
                # Deadlock detected
                raise RuntimeError("Deadlock detected in schedule")

        if scheduled_count < total_ops:
            raise RuntimeError(f"Failed to schedule all operations ({scheduled_count}/{total_ops})")

        # Calculate makespan
        makespan = max(job_time.values()) if job_time else 0
        schedule._makespan = makespan
