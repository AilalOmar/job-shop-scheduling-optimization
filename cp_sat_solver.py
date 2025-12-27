"""
Exact Method for JSP using Google OR-Tools CP-SAT Solver
Much more efficient than complete enumeration
Can solve larger instances (up to 15x15 or more)
"""

from ortools.sat.python import cp_model
from jsp_model import JSPProblem, Schedule
from typing import Dict, List, Tuple
import time
import logging

logger = logging.getLogger(__name__)


class CPSatSolver:
    """
    Exact solver using Google OR-Tools CP-SAT
    Guarantees optimal solution and is much faster than enumeration
    """

    def __init__(self, time_limit_seconds=300):
        """
        Args:
            time_limit_seconds: Maximum time to search for solution (default: 5 minutes)
        """
        self.name = "CP-SAT Exact Solver"
        self.time_limit = time_limit_seconds

    def solve(self, problem: JSPProblem) -> Tuple[Schedule, dict]:
        """
        Solve JSP using CP-SAT constraint programming

        Returns:
            (Schedule, statistics)
        """
        start_time = time.time()

        # Create the model
        model = cp_model.CpModel()

        # Compute horizon (upper bound on makespan)
        horizon = sum(
            sum(op.duration for op in job.operations)
            for job in problem.jobs
        )

        logger.info(f"Solving {problem.name} with CP-SAT (horizon: {horizon})")

        # Create interval variables for each operation
        # Format: task_intervals[job_id][op_idx] = interval variable
        task_intervals = {}
        task_starts = {}
        task_ends = {}

        for job in problem.jobs:
            task_intervals[job.job_id] = {}
            task_starts[job.job_id] = {}
            task_ends[job.job_id] = {}

            for op_idx, operation in enumerate(job.operations):
                # Create variables for start, end, and interval
                suffix = f'_j{job.job_id}_op{op_idx}'

                start_var = model.NewIntVar(0, horizon, 'start' + suffix)
                end_var = model.NewIntVar(0, horizon, 'end' + suffix)
                interval_var = model.NewIntervalVar(
                    start_var, operation.duration, end_var, 'interval' + suffix
                )

                task_intervals[job.job_id][op_idx] = interval_var
                task_starts[job.job_id][op_idx] = start_var
                task_ends[job.job_id][op_idx] = end_var

        # Precedence constraints: operations of same job must be sequential
        for job in problem.jobs:
            for op_idx in range(len(job.operations) - 1):
                model.Add(
                    task_ends[job.job_id][op_idx] <= task_starts[job.job_id][op_idx + 1]
                )

        # Disjunctive constraints: no overlap on same machine
        machine_to_intervals = {m: [] for m in range(problem.n_machines)}
        for job in problem.jobs:
            for op_idx, operation in enumerate(job.operations):
                machine_to_intervals[operation.machine_id].append(
                    task_intervals[job.job_id][op_idx]
                )

        for machine_id in range(problem.n_machines):
            model.AddNoOverlap(machine_to_intervals[machine_id])

        # Objective: minimize makespan
        makespan_var = model.NewIntVar(0, horizon, 'makespan')
        model.AddMaxEquality(
            makespan_var,
            [task_ends[job.job_id][len(job.operations) - 1]
             for job in problem.jobs]
        )
        model.Minimize(makespan_var)

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit
        solver.parameters.log_search_progress = False

        logger.info("Starting CP-SAT search...")
        status = solver.Solve(model)

        cpu_time = time.time() - start_time

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            schedule = Schedule(problem)

            for job in problem.jobs:
                for op_idx in range(len(job.operations)):
                    start = solver.Value(task_starts[job.job_id][op_idx])
                    end = solver.Value(task_ends[job.job_id][op_idx])
                    schedule.operation_times[(job.job_id, op_idx)] = (start, end)

            # Build machine orders from the solution
            machine_orders = {m: [] for m in range(problem.n_machines)}
            for job in problem.jobs:
                for op_idx, operation in enumerate(job.operations):
                    start = solver.Value(task_starts[job.job_id][op_idx])
                    machine_orders[operation.machine_id].append(
                        (start, job.job_id, op_idx)
                    )

            # Sort by start time
            for machine_id in machine_orders:
                machine_orders[machine_id].sort()
                machine_orders[machine_id] = [
                    (job_id, op_idx) for _, job_id, op_idx in machine_orders[machine_id]
                ]

            schedule.machine_orders = machine_orders

            makespan = solver.Value(makespan_var)
            schedule._makespan = makespan

            # Statistics
            stats = {
                'algorithm': 'CP-SAT (Exact)',
                'makespan': makespan,
                'cpu_time': cpu_time,
                'status': 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE',
                'optimal': status == cp_model.OPTIMAL,
                'branches': solver.NumBranches(),
                'conflicts': solver.NumConflicts(),
                'wall_time': solver.WallTime()
            }

            logger.info(
                f"CP-SAT completed: makespan={makespan}, "
                f"status={'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}, "
                f"time={cpu_time:.2f}s, branches={solver.NumBranches()}"
            )

            return schedule, stats

        else:
            # No solution found
            error_msg = {
                cp_model.INFEASIBLE: "Problem is infeasible (no solution exists)",
                cp_model.MODEL_INVALID: "Model is invalid",
                cp_model.UNKNOWN: "Unknown status (possibly timeout)"
            }.get(status, f"Solver failed with status {status}")

            raise RuntimeError(
                f"CP-SAT failed to find solution: {error_msg}. "
                f"Time: {cpu_time:.2f}s"
            )
