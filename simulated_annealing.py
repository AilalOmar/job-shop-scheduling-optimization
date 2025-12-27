"""
Simulated Annealing Solver for Job Shop Scheduling Problem

CRITICAL: This algorithm MUST be 100% functional and thoroughly tested
before proceeding to visualization and UI development.

Adapted simulation logic from Metod_exact.py (lines 21-63)
"""

import random
import math
import time
import logging
from typing import List, Tuple, Dict, Optional
from copy import deepcopy

from jsp_model import JSPProblem, Schedule, Job, Operation


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatedAnnealingSolver:
    """
    Simulated Annealing solver for Job Shop Scheduling

    Parameters from prompt.md:
    - temp_init: 1000
    - cooling_rate: 0.95
    - iter_per_temp: 100
    - temp_min: 1
    """

    def __init__(self,
                 temp_init: float = 1000,
                 temp_min: float = 1,
                 cooling_rate: float = 0.95,
                 iter_per_temp: int = 100,
                 max_iterations: Optional[int] = None,
                 max_time: Optional[float] = None,
                 random_seed: Optional[int] = None,
                 verbose: bool = True,
                 log_history: bool = True):

        self.temp_init = temp_init
        self.temp_min = temp_min
        self.cooling_rate = cooling_rate
        self.iter_per_temp = iter_per_temp
        self.max_iterations = max_iterations
        self.max_time = max_time
        self.random_seed = random_seed
        self.verbose = verbose
        self.log_history = log_history

        # Internal state
        self.problem: Optional[JSPProblem] = None
        self.current_solution: Optional[Schedule] = None
        self.best_solution: Optional[Schedule] = None
        self.convergence_history: List[Tuple[int, int, float]] = []
        self.acceptance_history: List[bool] = []

        if random_seed is not None:
            random.seed(random_seed)

    def solve(self, problem: JSPProblem) -> Tuple[Schedule, dict]:
        """
        Main Simulated Annealing algorithm

        Returns:
            (best_schedule, statistics_dict)
        """
        self.problem = problem
        start_time = time.time()

        # Generate initial solution
        logger.info(f"Starting SA for problem: {problem.name}")
        self.current_solution = self._generate_initial_solution(problem)
        initial_makespan = self.current_solution.makespan

        self.best_solution = self.current_solution.copy()
        best_makespan = initial_makespan

        logger.info(f"Initial makespan: {initial_makespan}")

        # Initialize tracking
        self.convergence_history = [(0, initial_makespan, self.temp_init)]
        self.acceptance_history = []

        temp = self.temp_init
        iteration = 0
        accepted_moves = 0
        rejected_moves = 0

        # Main SA loop
        while temp > self.temp_min:
            # Check termination conditions
            if self.max_iterations and iteration >= self.max_iterations:
                break
            if self.max_time and (time.time() - start_time) >= self.max_time:
                break

            for _ in range(self.iter_per_temp):
                iteration += 1

                # Generate neighbor
                neighbor = self._generate_neighbor(self.current_solution)

                if neighbor is None:
                    continue

                # Calculate delta
                current_makespan = self.current_solution.makespan
                neighbor_makespan = neighbor.makespan
                delta = neighbor_makespan - current_makespan

                # Acceptance criterion
                if delta < 0:  # Better solution
                    self.current_solution = neighbor
                    accepted_moves += 1
                    self.acceptance_history.append(True)

                    # Update best if necessary
                    if neighbor_makespan < best_makespan:
                        self.best_solution = neighbor.copy()
                        best_makespan = neighbor_makespan
                        if self.verbose and iteration % 100 == 0:
                            logger.info(f"NEW BEST at iteration {iteration}: {best_makespan}")

                else:  # Worse solution
                    accept_prob = self._acceptance_probability(delta, temp)
                    if random.random() < accept_prob:
                        self.current_solution = neighbor
                        accepted_moves += 1
                        self.acceptance_history.append(True)
                    else:
                        rejected_moves += 1
                        self.acceptance_history.append(False)

                # Log iteration
                if self.log_history:
                    self.convergence_history.append(
                        (iteration, self.current_solution.makespan, temp)
                    )

                # Periodic logging
                if self.verbose and iteration % 100 == 0:
                    accept_rate = accepted_moves / iteration * 100 if iteration > 0 else 0
                    logger.info(
                        f"Iter {iteration} | Temp: {temp:.2f} | "
                        f"Current: {self.current_solution.makespan} | "
                        f"Best: {best_makespan} | Accept: {accept_rate:.1f}%"
                    )

            # Cooling schedule
            temp *= self.cooling_rate

        # Final statistics
        end_time = time.time()
        cpu_time = end_time - start_time

        improvement_percent = ((initial_makespan - best_makespan) / initial_makespan * 100
                              if initial_makespan > 0 else 0)

        statistics = {
            "initial_makespan": initial_makespan,
            "best_makespan": best_makespan,
            "final_makespan": self.current_solution.makespan,
            "improvement_percent": improvement_percent,
            "total_iterations": iteration,
            "cpu_time": cpu_time,
            "accepted_moves": accepted_moves,
            "rejected_moves": rejected_moves,
            "convergence_history": self.convergence_history
        }

        logger.info(f"SA completed - Best makespan: {best_makespan}")
        logger.info(f"Improvement: {improvement_percent:.2f}% in {cpu_time:.2f}s")

        return self.best_solution, statistics

    def _generate_initial_solution(self, problem: JSPProblem) -> Schedule:
        """
        Generate random valid initial solution using priority dispatch

        Algorithm:
        1. For each machine, randomly order operations assigned to it
        2. Simulate execution to get valid schedule
        """
        schedule = Schedule(problem)

        # Get all operations for each machine
        machine_ops = {m: [] for m in range(problem.n_machines)}
        for job in problem.jobs:
            for op in job.operations:
                # Validate machine_id is in valid range
                if op.machine_id < 0 or op.machine_id >= problem.n_machines:
                    raise ValueError(f"Invalid machine_id {op.machine_id} for problem with {problem.n_machines} machines. Machine IDs must be 0-indexed (0 to {problem.n_machines-1})")
                machine_ops[op.machine_id].append((job.job_id, op.operation_index))

        # Randomly shuffle operations on each machine
        for machine_id in machine_ops:
            random.shuffle(machine_ops[machine_id])

        schedule.machine_orders = machine_ops

        # Simulate to calculate times
        self._simulate_schedule(schedule)

        return schedule

    def _simulate_schedule(self, schedule: Schedule) -> None:
        """
        Simulate schedule execution and calculate operation times

        ADAPTED FROM Metod_exact.py (lines 21-63)
        Implements greedy dispatch respecting precedence and resource constraints
        """
        problem = schedule.problem

        # Initialize tracking
        job_time = {j: 0 for j in range(problem.n_jobs)}
        machine_time = {m: 0 for m in range(problem.n_machines)}
        job_op_index = {j: 0 for j in range(problem.n_jobs)}

        # Process operations in machine order
        max_iterations = sum(len(ops) for ops in schedule.machine_orders.values()) * 2
        iterations = 0

        while True:
            iterations += 1
            if iterations > max_iterations:
                # Deadlock detection (from Metod_exact.py line 60)
                logger.warning("Deadlock detected in schedule simulation")
                raise RuntimeError("Schedule contains deadlock - invalid machine orders")

            progress = False

            for machine_id, machine_order in schedule.machine_orders.items():
                # Find next operation to execute on this machine
                for job_id, op_index in machine_order:
                    # Check if this operation is ready
                    if job_op_index[job_id] == op_index:
                        job = problem.get_job(job_id)
                        operation = job.operations[op_index]

                        # Calculate start time (from Metod_exact.py lines 49-56)
                        # Must wait for: 1) previous op of same job, 2) machine availability
                        start_time = max(job_time[job_id], machine_time[machine_id])
                        end_time = start_time + operation.duration

                        # Schedule this operation
                        schedule.set_operation_time(job_id, op_index, start_time, end_time)

                        # Update tracking
                        job_time[job_id] = end_time
                        machine_time[machine_id] = end_time
                        job_op_index[job_id] += 1

                        progress = True
                        break

            # Check if all operations scheduled
            if all(job_op_index[j] == len(problem.jobs[j].operations)
                  for j in range(problem.n_jobs)):
                break

            if not progress:
                # No operation could be scheduled - deadlock
                raise RuntimeError("Schedule deadlock - no progress possible")

    def _calculate_makespan(self, schedule: Schedule) -> int:
        """
        Calculate makespan for a schedule

        Uses simulation engine adapted from Metod_exact.py
        """
        try:
            # Clear existing times
            schedule.operation_times = {}

            # Simulate to calculate times
            self._simulate_schedule(schedule)

            return schedule.makespan

        except RuntimeError:
            # Invalid schedule (deadlock)
            return float('inf')

    def _generate_neighbor(self, schedule: Schedule) -> Optional[Schedule]:
        """
        Generate neighboring solution

        Strategy:
        - 70% probability: swap adjacent operations
        - 30% probability: random insertion

        Returns None if unable to generate valid neighbor after retries
        """
        max_retries = 10

        for _ in range(max_retries):
            # Select operator
            if random.random() < 0.7:
                neighbor = self._swap_adjacent_operations(schedule)
            else:
                neighbor = self._random_insert_operation(schedule)

            if neighbor is not None:
                return neighbor

        # Failed to generate valid neighbor
        logger.debug("Failed to generate valid neighbor after retries")
        return None

    def _swap_adjacent_operations(self, schedule: Schedule) -> Optional[Schedule]:
        """
        Swap two adjacent operations on a randomly selected machine

        Algorithm:
        1. Select machine with at least 2 operations
        2. Select random position i
        3. Swap operations at i and i+1
        4. Recalculate schedule
        """
        # Find machines with at least 2 operations
        eligible_machines = [m for m, ops in schedule.machine_orders.items()
                           if len(ops) >= 2]

        if not eligible_machines:
            return None

        # Select random machine
        machine_id = random.choice(eligible_machines)
        ops = schedule.machine_orders[machine_id]

        # Select random position
        i = random.randint(0, len(ops) - 2)

        # Create neighbor
        neighbor = Schedule(schedule.problem)
        neighbor.machine_orders = deepcopy(schedule.machine_orders)

        # Swap adjacent operations
        neighbor.machine_orders[machine_id][i], neighbor.machine_orders[machine_id][i+1] = \
            neighbor.machine_orders[machine_id][i+1], neighbor.machine_orders[machine_id][i]

        # Recalculate schedule
        try:
            self._simulate_schedule(neighbor)
            return neighbor
        except RuntimeError:
            # Invalid schedule
            return None

    def _random_insert_operation(self, schedule: Schedule) -> Optional[Schedule]:
        """
        Remove operation and insert at different position

        Algorithm:
        1. Select machine with at least 2 operations
        2. Select operation at position i
        3. Select new position j (j != i)
        4. Move operation from i to j
        5. Recalculate schedule
        """
        # Find machines with at least 2 operations
        eligible_machines = [m for m, ops in schedule.machine_orders.items()
                           if len(ops) >= 2]

        if not eligible_machines:
            return None

        # Select random machine
        machine_id = random.choice(eligible_machines)
        ops = schedule.machine_orders[machine_id]

        # Select random position to remove
        i = random.randint(0, len(ops) - 1)

        # Select different position to insert
        possible_positions = [j for j in range(len(ops)) if j != i]
        if not possible_positions:
            return None

        j = random.choice(possible_positions)

        # Create neighbor
        neighbor = Schedule(schedule.problem)
        neighbor.machine_orders = deepcopy(schedule.machine_orders)

        # Remove and insert
        op = neighbor.machine_orders[machine_id].pop(i)
        neighbor.machine_orders[machine_id].insert(j, op)

        # Recalculate schedule
        try:
            self._simulate_schedule(neighbor)
            return neighbor
        except RuntimeError:
            # Invalid schedule
            return None

    def _acceptance_probability(self, delta: float, temp: float) -> float:
        """
        Metropolis acceptance criterion

        Args:
            delta: new_makespan - current_makespan
            temp: current temperature

        Returns:
            Probability of acceptance (0.0 to 1.0)
        """
        if delta < 0:
            return 1.0
        else:
            return math.exp(-delta / temp)

    def get_convergence_data(self) -> List[Tuple[int, int, float]]:
        """
        Get convergence history

        Returns:
            List of (iteration, makespan, temperature) tuples
        """
        return self.convergence_history

    def get_statistics(self) -> dict:
        """Get summary statistics from last solve run"""
        if not self.convergence_history:
            return {}

        initial_makespan = self.convergence_history[0][1]
        best_makespan = self.best_solution.makespan if self.best_solution else initial_makespan

        return {
            "initial_makespan": initial_makespan,
            "best_makespan": best_makespan,
            "improvement": initial_makespan - best_makespan,
            "improvement_percent": ((initial_makespan - best_makespan) / initial_makespan * 100
                                  if initial_makespan > 0 else 0),
            "total_iterations": len(self.convergence_history),
            "accepted_moves": sum(self.acceptance_history),
            "rejected_moves": len(self.acceptance_history) - sum(self.acceptance_history)
        }
