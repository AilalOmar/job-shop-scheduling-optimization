"""
Greedy Constructive Heuristic for JSP
Fast deterministic algorithm using SPT (Shortest Processing Time) priority rule
NOT an exact method - does not guarantee optimal solution
"""

from jsp_model import JSPProblem, Schedule, Operation
from typing import Dict, List, Tuple
import time


class GreedySolver:
    """
    Greedy solver using priority dispatching rules
    Uses SPT (Shortest Processing Time) heuristic
    """

    def __init__(self):
        self.name = "Greedy SPT Solver"

    def solve(self, problem: JSPProblem) -> Tuple[Schedule, dict]:
        """
        Solve JSP using greedy SPT (Shortest Processing Time) rule

        Returns:
            (Schedule, statistics)
        """
        start_time = time.time()

        # Create schedule
        schedule = Schedule(problem)

        # Track state
        job_next_op = {j: 0 for j in range(problem.n_jobs)}  # Next operation index for each job
        job_time = {j: 0 for j in range(problem.n_jobs)}     # Completion time of last op for each job
        machine_time = {m: 0 for m in range(problem.n_machines)}  # When each machine becomes available
        machine_orders = {m: [] for m in range(problem.n_machines)}

        # Schedule operations using SPT rule
        total_ops = sum(len(job.operations) for job in problem.jobs)
        scheduled_ops = 0

        while scheduled_ops < total_ops:
            # Find all available operations (next operation of jobs that haven't finished)
            available = []
            for job_id, next_op_idx in job_next_op.items():
                if next_op_idx < len(problem.jobs[job_id].operations):
                    op = problem.jobs[job_id].operations[next_op_idx]
                    # Operation is available if previous operation of same job has completed
                    available.append((job_id, next_op_idx, op))

            if not available:
                break

            # Select operation with shortest processing time (SPT rule)
            # Among those, prioritize the one whose job is ready earliest
            best_op = None
            best_start = float('inf')

            for job_id, op_idx, op in available:
                # Earliest this operation can start
                earliest_start = max(job_time[job_id], machine_time[op.machine_id])

                # SPT: prefer shorter operations, break ties by earliest start
                if best_op is None or (op.duration < best_op[2].duration) or \
                   (op.duration == best_op[2].duration and earliest_start < best_start):
                    best_op = (job_id, op_idx, op)
                    best_start = earliest_start

            # Schedule the selected operation
            job_id, op_idx, op = best_op
            start = max(job_time[job_id], machine_time[op.machine_id])
            end = start + op.duration

            # Update schedule
            schedule.operation_times[(job_id, op_idx)] = (start, end)
            machine_orders[op.machine_id].append((job_id, op_idx))

            # Update state
            job_time[job_id] = end
            machine_time[op.machine_id] = end
            job_next_op[job_id] += 1
            scheduled_ops += 1

        # Set machine orders
        schedule.machine_orders = machine_orders

        # Calculate makespan
        makespan = max(job_time.values()) if job_time else 0
        schedule._makespan = makespan

        cpu_time = time.time() - start_time

        # Statistics
        stats = {
            'algorithm': 'Greedy SPT',
            'makespan': makespan,
            'cpu_time': cpu_time,
            'operations_scheduled': scheduled_ops
        }

        return schedule, stats
