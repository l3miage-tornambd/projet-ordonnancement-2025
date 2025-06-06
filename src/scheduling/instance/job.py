'''
Job. It is composed of several operations.

@author: Vassilissa Lehoux
'''
from typing import List

from src.scheduling.instance.operation import Operation


class Job(object):
    '''
    Job class.
    Contains information on the next operation to schedule for that job
    '''

    def __init__(self, job_id: int):
        '''
        Constructor
        '''
        self._job_id : int = job_id
        self._operations: List[Operation] = []
        self._current_operation_index : int = 0
        self._next_operation_index : int = 0
        
    @property
    def job_id(self) -> int:
        '''
        Returns the id of the job.
        '''
        return self._job_id

    def reset(self):
        '''
        Resets the planned operations
        '''
        for op in self._operations:
            op.reset()

        self._current_operation_index = 0
        self._next_operation_index = 0

    @property
    def operations(self) -> List[Operation]:
        '''
        Returns a list of operations for the job
        '''
        return self._operations

    @property
    def next_operation(self) -> Operation:
        '''
        Returns the next operation to be scheduled
        '''

        # Renvoie la prochaine opération si la list n'est pas vide et que l'index est valide
        return self._operations[self._next_operation_index]

    def schedule_operation(self):
        '''
        Updates the next_operation to schedule
        '''
        if not self.planned:
            self._next_operation_index += 1

    @property
    def planned(self):
        '''
        Returns true if all operations are planned
        '''
        return self._next_operation_index >= len(self._operations)

    @property
    def operation_nb(self) -> int:
        '''
        Returns the nb of operations of the job
        '''
        return len(self._operations)

    def add_operation(self, operation: Operation):
        '''
        Adds an operation to the job at the end of the operation list,
        adds the precedence constraints between job operations.
        '''
        if self._operations:
            predecessor = self._operations[-1]
            operation.add_predecessor(predecessor)
            predecessor.add_successor(operation)

        self._operations.append(operation)

    @property
    def completion_time(self) -> int:
        '''
        Returns the job's completion time
        '''
        # S'il n'y a pas d'opérations, le job est terminé à t=0
        if not self._operations:
            return 0

        last_operation = self._operations[-1]
        return last_operation.end_time


    #def __str__(self):
     #   return f"J{self.job_id}"

    #def __repr__(self):
     #   return str(self)
