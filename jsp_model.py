"""
Job Shop Scheduling Problem - Data Structures
Core classes for representing JSP problems and solutions.
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from copy import deepcopy


class Operation:
    """Represents a single operation within a job"""

    def __init__(self, machine_id: int, duration: int, job_id: Optional[int] = None,
                 operation_index: Optional[int] = None):
        self.machine_id = machine_id
        self.duration = duration
        self.job_id = job_id
        self.operation_index = operation_index

    def __repr__(self) -> str:
        return f"Op(J{self.job_id}_Op{self.operation_index}, M{self.machine_id}, D{self.duration})"

    def to_dict(self) -> dict:
        return {
            "machine": self.machine_id,
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: dict, job_id: Optional[int] = None,
                  operation_index: Optional[int] = None) -> 'Operation':
        return cls(data["machine"], data["duration"], job_id, operation_index)


class Job:
    """Represents a job with sequential operations"""

    def __init__(self, job_id: int, operations: List[Operation]):
        self.job_id = job_id
        self.operations = operations

        # Set job_id and operation_index for all operations
        for idx, op in enumerate(self.operations):
            op.job_id = job_id
            op.operation_index = idx

    @property
    def n_operations(self) -> int:
        return len(self.operations)

    def add_operation(self, machine_id: int, duration: int) -> None:
        op_index = len(self.operations)
        op = Operation(machine_id, duration, self.job_id, op_index)
        self.operations.append(op)

    def get_operation(self, index: int) -> Operation:
        return self.operations[index]

    def total_processing_time(self) -> int:
        return sum(op.duration for op in self.operations)

    def __repr__(self) -> str:
        return f"Job{self.job_id}(ops={self.n_operations})"

    def to_dict(self) -> dict:
        return {
            "id": self.job_id,
            "operations": [op.to_dict() for op in self.operations]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Job':
        job_id = data["id"]
        operations = [Operation.from_dict(op_data, job_id, idx)
                     for idx, op_data in enumerate(data["operations"])]
        return cls(job_id, operations)


class Machine:
    """Represents a machine resource"""

    def __init__(self, machine_id: int, name: Optional[str] = None):
        self.machine_id = machine_id
        self.name = name if name else f"M{machine_id}"
        self.operations_assigned = []

    def clear(self) -> None:
        self.operations_assigned = []

    def add_operation(self, job_id: int, operation_index: int) -> None:
        self.operations_assigned.append((job_id, operation_index))

    def __repr__(self) -> str:
        return f"Machine({self.name})"


class Schedule:
    """Represents a complete solution schedule"""

    def __init__(self, problem: 'JSPProblem'):
        self.problem = problem
        self.operation_times: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.machine_orders: Dict[int, List[Tuple[int, int]]] = {
            m: [] for m in range(problem.n_machines)
        }
        self._makespan: Optional[int] = None
        self._is_valid: Optional[bool] = None

    def set_operation_time(self, job_id: int, op_index: int, start: int, end: int) -> None:
        self.operation_times[(job_id, op_index)] = (start, end)
        self._makespan = None  # Invalidate cached makespan

    def get_operation_time(self, job_id: int, op_index: int) -> Optional[Tuple[int, int]]:
        return self.operation_times.get((job_id, op_index))

    def calculate_makespan(self) -> int:
        if not self.operation_times:
            return 0
        return max(end for _, end in self.operation_times.values())

    @property
    def makespan(self) -> int:
        if self._makespan is None:
            self._makespan = self.calculate_makespan()
        return self._makespan

    def validate(self) -> bool:
        """Validate schedule against precedence and resource constraints"""
        if not self.operation_times:
            return False

        # Check precedence constraints
        for job in self.problem.jobs:
            for op_idx in range(job.n_operations - 1):
                current_time = self.get_operation_time(job.job_id, op_idx)
                next_time = self.get_operation_time(job.job_id, op_idx + 1)

                if current_time is None or next_time is None:
                    return False

                # Current operation must finish before next starts
                if current_time[1] > next_time[0]:
                    return False

        # Check resource constraints (no overlapping on same machine)
        machine_operations = {m: [] for m in range(self.problem.n_machines)}

        for (job_id, op_idx), (start, end) in self.operation_times.items():
            job = self.problem.get_job(job_id)
            machine_id = job.operations[op_idx].machine_id
            machine_operations[machine_id].append((start, end, job_id, op_idx))

        # Check for overlaps on each machine
        for machine_id, ops in machine_operations.items():
            ops.sort()  # Sort by start time
            for i in range(len(ops) - 1):
                if ops[i][1] > ops[i+1][0]:  # end_i > start_i+1
                    return False

        return True

    def get_machine_utilization(self) -> Dict[int, float]:
        """Calculate utilization rate for each machine"""
        makespan = self.makespan
        if makespan == 0:
            return {m: 0.0 for m in range(self.problem.n_machines)}

        utilization = {}
        for machine_id in range(self.problem.n_machines):
            total_time = 0
            for (job_id, op_idx), (start, end) in self.operation_times.items():
                job = self.problem.get_job(job_id)
                if job.operations[op_idx].machine_id == machine_id:
                    total_time += (end - start)
            utilization[machine_id] = total_time / makespan

        return utilization

    def to_dict(self) -> dict:
        return {
            "operation_times": {
                f"{job_id}_{op_idx}": {"start": start, "end": end}
                for (job_id, op_idx), (start, end) in self.operation_times.items()
            },
            "machine_orders": {
                str(m): [(j, o) for j, o in ops]
                for m, ops in self.machine_orders.items()
            },
            "makespan": self.makespan
        }

    @classmethod
    def from_dict(cls, data: dict, problem: 'JSPProblem') -> 'Schedule':
        schedule = cls(problem)

        # Restore operation times
        for key, times in data["operation_times"].items():
            job_id, op_idx = map(int, key.split("_"))
            schedule.set_operation_time(job_id, op_idx, times["start"], times["end"])

        # Restore machine orders
        schedule.machine_orders = {
            int(m): [(j, o) for j, o in ops]
            for m, ops in data["machine_orders"].items()
        }

        return schedule

    def copy(self) -> 'Schedule':
        """Create a deep copy of the schedule"""
        new_schedule = Schedule(self.problem)
        new_schedule.operation_times = deepcopy(self.operation_times)
        new_schedule.machine_orders = deepcopy(self.machine_orders)
        new_schedule._makespan = self._makespan
        return new_schedule


class JSPProblem:
    """Represents a complete JSP problem instance"""

    def __init__(self, name: str, n_machines: int, n_jobs: int,
                 jobs: List[Job], bks: Optional[int] = None):
        self.name = name
        self.n_machines = n_machines
        self.n_jobs = n_jobs
        self.jobs = jobs
        self.bks = bks
        self.machines = [Machine(i) for i in range(n_machines)]

    def get_job(self, job_id: int) -> Job:
        return self.jobs[job_id]

    def get_operations_for_machine(self, machine_id: int) -> List[Tuple[Job, Operation]]:
        """Get all operations that need to be processed on a specific machine"""
        operations = []
        for job in self.jobs:
            for op in job.operations:
                if op.machine_id == machine_id:
                    operations.append((job, op))
        return operations

    def lower_bound_makespan(self) -> int:
        """Calculate a lower bound for makespan (sum of max job duration)"""
        return max(job.total_processing_time() for job in self.jobs)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "n_machines": self.n_machines,
            "n_jobs": self.n_jobs,
            "bks": self.bks,
            "jobs": [job.to_dict() for job in self.jobs]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'JSPProblem':
        jobs = [Job.from_dict(job_data) for job_data in data["jobs"]]
        return cls(
            name=data.get("name", "unnamed"),
            n_machines=data["n_machines"],
            n_jobs=data["n_jobs"],
            jobs=jobs,
            bks=data.get("bks")
        )

    @classmethod
    def from_json(cls, filepath: str) -> 'JSPProblem':
        """Load JSP problem from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_json(self, filepath: str) -> None:
        """Save JSP problem to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_existing_format(cls, jobs_dict: dict, machines: List[str],
                           name: str = "converted") -> 'JSPProblem':
        """
        Convert from Metod_exact.py format to JSPProblem

        Args:
            jobs_dict: {"J1": [("M1", 3), ("M2", 2)], ...}
            machines: ["M1", "M2", "M3"]
            name: Instance name

        Returns:
            JSPProblem instance
        """
        # Create machine mapping: "M1" -> 0, "M2" -> 1, etc.
        machine_map = {m: idx for idx, m in enumerate(machines)}

        jobs = []
        for job_idx, (job_name, operations_list) in enumerate(jobs_dict.items()):
            operations = []
            for op_idx, (machine_name, duration) in enumerate(operations_list):
                machine_id = machine_map[machine_name]
                op = Operation(machine_id, duration, job_idx, op_idx)
                operations.append(op)
            jobs.append(Job(job_idx, operations))

        return cls(
            name=name,
            n_machines=len(machines),
            n_jobs=len(jobs),
            jobs=jobs
        )

    @classmethod
    def load_benchmark(cls, instance_name: str, benchmark_type: str = "jsp_taillard") -> 'JSPProblem':
        """
        Load a benchmark instance

        Args:
            instance_name: e.g., "ta01", "mk01"
            benchmark_type: e.g., "jsp_taillard", "fjsp_brandimarte"

        Returns:
            JSPProblem instance
        """
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, "benchmarks", benchmark_type, f"{instance_name}.json")
        return cls.from_json(filepath)

    @classmethod
    def get_bks(cls, instance_name: str, benchmark_type: str) -> Optional[int]:
        """Load BKS from bks_reference.json"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bks_file = os.path.join(script_dir, "benchmarks", "bks_reference.json")

        try:
            with open(bks_file, 'r') as f:
                bks_data = json.load(f)
            return bks_data[benchmark_type][instance_name]["bks"]
        except (FileNotFoundError, KeyError):
            return None

    def __repr__(self) -> str:
        return f"JSPProblem({self.name}, {self.n_jobs}x{self.n_machines}, BKS={self.bks})"
