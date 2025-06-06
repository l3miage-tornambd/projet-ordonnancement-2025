'''
Operation of a job.
Its duration and energy consumption depends on the machine on which it is executed.
When operation is scheduled, its schedule information is updated.

@author: Vassilissa Lehoux
'''
from typing import List, Dict, Tuple


class OperationScheduleInfo(object):
    '''
    Informations known when the operation is scheduled
    '''

    def __init__(self, machine_id: int, schedule_time: int, duration: int, energy_consumption: int):
        self.machine_id : int = machine_id
        self.schedule_time : int = schedule_time
        self.duration : int = duration
        self.energy_consumption : int = energy_consumption


class Operation(object):
    '''
    Operation of the jobs
    '''

    def __init__(self, job_id: int, operation_id: int):
        '''
        Constructor
        '''

        # Bon j'ai vu qu'on pouvait typer les variables avec # type: + le type et j'en abuse car je déteste les langages non typés
        self._job_id : int = job_id
        self._operation_id : int = operation_id
        self._predecessor : List[Operation] = []
        self._successor : List[Operation] = []
        self._schedule_info : OperationScheduleInfo or None  = None

        # On a besoin à un moment d'avoir les informations de processing_time et d'energy condommé pour la méthode schedule (à voir comment on alimente ça)
        self._machine_options: Dict[int, Tuple[int, int]] = {}

    @property
    def machine_options(self) -> Dict[int, Tuple[int, int]]:
        '''
        Returns the machine options for the operation.
        The key is the machine ID and the value is a tuple of (processing_time, energy_consumption)
        '''
        return self._machine_options

    @machine_options.setter
    def machine_options(self, options: Dict[int, Tuple[int, int]]):
        '''
        Sets the machine options for the operation.
        The key is the machine ID and the value is a tuple of (processing_time, energy_consumption)
        '''
        self._machine_options = options

    def reset(self):
        '''
        Removes scheduling informations
        '''
        self._schedule_info = None

    def add_predecessor(self, operation):
        '''
        Adds a predecessor to the operation
        '''
        if operation not in self._predecessor:
            self._predecessor.append(operation)

    def add_successor(self, operation):
        '''
        Adds a successor operation
        '''
        if operation not in self._successor:
            self._successor.append(operation)

    @property
    def operation_id(self) -> int:
        return self._operation_id

    @property
    def job_id(self) -> int:
        return self._job_id

    @property
    def predecessors(self) -> List:
        """
        Returns a list of the predecessor operations
        """
        return self._predecessor

    @property
    def successors(self) -> List:
        '''
        Returns a list of the successor operations
        '''
        return self._successor

    @property
    def assigned(self) -> bool:
        '''
        Returns True if the operation is assigned
        and False otherwise
        '''
        return self._schedule_info is not None

    @property
    def assigned_to(self) -> int:
        '''
        Returns the machine ID it is assigned to if any
        and -1 otherwise
        '''
        return self._schedule_info.machine_id if self.assigned else -1

    @property
    def processing_time(self) -> int:
        '''
        Returns the processing time if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.schedule_time if self.assigned else -1

    @property
    def start_time(self) -> int:
        '''
        Returns the start time if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.schedule_time if self.assigned else -1

    @property
    def end_time(self) -> int:
        '''
        Returns the end time if is assigned,
        -1 otherwise
        '''
        return (self.start_time + self.processing_time) if self.assigned else -1

    @property
    def energy(self) -> int:
        '''
        Returns the energy consumption if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.energy_consumption if self.assigned else -1

    def is_ready(self, at_time) -> bool:
        '''
        Returns True if all the predecessors are assigned
        and processed before at_time.
        False otherwise
        '''
        for pred in self._predecessor:
            if not pred.assigned or pred.end_time > at_time:
                return False

        return True

    def schedule(self, machine_id: int, at_time: int, check_success=True) -> bool:
        '''
        Schedules an operation. Updates the schedule information of the operation
        @param check_success: if True, check if all the preceeding operations have
          been scheduled and if the schedule time is compatible
        '''
        if machine_id not in self.machine_options:
            return False

        if check_success and not self.is_ready(at_time):
            return False

        duration, energy = self.machine_options[machine_id]
        self._schedule_info = OperationScheduleInfo(machine_id, at_time, duration, energy)

        return True

    @property
    def min_start_time(self) -> int:
        '''
        Minimum start time given the precedence constraints
        '''
        if not self.predecessors:
            return 0
        else:
            return max([pred.end_time for pred in self.predecessors if pred.assigned])

    def schedule_at_min_time(self, machine_id: int, min_time: int) -> bool:
        '''
        Try and schedule the operation af or after min_time.
        Return False if not possible
        '''

        calculated_min_time = max(min_time, self.min_start_time)
        return self.schedule(machine_id, calculated_min_time, check_success=False)

    def __str__(self):
        '''
        Returns a string representing the operation.
        '''
        base_str = f"O{self.operation_id}_J{self.job_id}"
        if self._schedule_info:
            return base_str + f"_M{self.assigned_to}_ci{self.processing_time}_e{self.energy}"
        else:
            return base_str

    def __repr__(self):
        return str(self)
