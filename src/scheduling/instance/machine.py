'''
Machine on which operation are executed.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.operation import Operation


class Machine(object):
    '''
    Machine class.
    When operations are scheduled on the machine, contains the relative information. 
    '''

    def __init__(self, machine_id: int, set_up_time: int, set_up_energy: int, tear_down_time: int,
                 tear_down_energy:int, min_consumption: int, end_time: int):
        '''
        Constructor
        Machine is stopped at the beginning of the planning and need to
        be started before executing any operation.
        @param end_time: End of the schedule on this machine: the machine must be
          shut down before that time.
        '''
        self._machine_id : int = machine_id
        self._set_up_time : int = set_up_time
        self._set_up_energy : int = set_up_energy
        self._tear_down_time : int = tear_down_time
        self._tear_down_energy : int = tear_down_energy
        self._min_consumption : int = min_consumption
        self._end_time : int = end_time

        self._scheduled_operations : List[Operation] = []
        self._start_times : List[int] = []
        self._stop_times : List[int] = []

        self.reset()

    def reset(self):
        for op in self._scheduled_operations:
            op.reset()

        self._scheduled_operations = []
        self._start_times = []
        self._stop_times = []

    @property
    def set_up_time(self) -> int:
        return self._set_up_time

    @property
    def tear_down_time(self) -> int:
        return self._tear_down_time

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @property
    def scheduled_operations(self) -> List:
        '''
        Returns the list of the scheduled operations on the machine.
        '''
        return self._scheduled_operations

    @property
    def available_time(self) -> int:
        """
        Returns the next time at which the machine is available
        after processing its last operation of after its last set up.
        """
        # Cas la machine a été démarrée mais n'a pas d'opération
        if len(self._start_times) > len(self._stop_times) and not self._scheduled_operations:
            return self._start_times[-1] + self._set_up_time

        # Cas la machine est en marche et a déjà des opérations
        if self._scheduled_operations:
            last_op = self._scheduled_operations[-1]
            return last_op.end_time

        # Cas la machine est éteinte, elle est dispo à partir du dernier arrêt.
        if self._stop_times:
            return self._stop_times[-1]

        # Cas initial, la machine est dispo à t=0
        return 0

    def add_operation(self, operation: Operation, start_time: int) -> int:
        '''
        Adds an operation on the machine, at the end of the schedule,
        as soon as possible after time start_time.
        Returns the actual start time.
        '''

        is_off = len(self._start_times) == len(self._stop_times)

        machine_available_time = self.available_time
        op_ready_time = operation.min_start_time

        # L'opération ne peut commencer qu'après sa disponibilité et celle de la machine
        potential_start_time = max(machine_available_time, op_ready_time, start_time)

        if is_off:
            # Cas ou la machine est éteinte, on doit prendre en compte le temps de démarrage
            actual_start = potential_start_time
            # Le cycle de la machine commence donc avant
            new_machine_start = actual_start - self._set_up_time
            self._start_times.append(new_machine_start)
        else:
            # Cas ou la machine est déjà en marche, on peut commencer l'opération dès que possible
            actual_start = potential_start_time

        # On ajoute l'opération en la lien à la machine
        operation.schedule(self.machine_id, actual_start, check_success=False)

        # On ajoute l'opération à la liste de la machine et pourquoi pas la trié par ordre de début au cas ou (pourrait être utile pour la suite)
        self._scheduled_operations.append(operation)
        self._scheduled_operations.sort(key=lambda op: op.start_time)

        return actual_start

    def stop(self, at_time):
        """
        Stops the machine at time at_time.
        """
        assert self.available_time <= at_time, "On ne peut pas arrêter une machine en cours d'exécution"
        assert len(self._start_times) == len(self._stop_times) + 1, "On ne peut pas arrêter une machine qui n'a pas été démarrée"
        assert at_time + self.tear_down_time <= self._end_time, "On ne peut pas arrêter une machine après la fin du planning"

        self._stop_times.append(at_time)

    @property
    def working_time(self) -> int:
        '''
        Total time during which the machine is running
        '''
        total_time = 0
        # On additionne le temps de fonctionnement de chaque opération
        for i in range(len(self._stop_times)):
            total_time += self._stop_times[i] - self._start_times[i]

        # On traite le cas où la machine est encore en marche à la fin du planning pour ne pas oublier la dernière opération
        if len(self._start_times) > len(self._stop_times):
            total_time += self.available_time - self._start_times[-1]

        return total_time

    @property
    def start_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is started
        in increasing order
        """
        return self._start_times

    @property
    def stop_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is stopped
        in increasing order
        """
        return self._stop_times

    @property
    def total_energy_consumption(self) -> int:
        """
        Total energy consumption of the machine during planning exectution.
        """
        # 1. Il y a le coup de démarrage et d'arrêt de la machine
        energy_setup = len(self.start_times) * self._set_up_energy
        energy_teardown = len(self.stop_times) * self._tear_down_energy

        # 2. Il y a a aussi l'énergie consommée par les opérations
        energy_processing = sum(op.energy for op in self._scheduled_operations)

        # 3. Il y a l'énergie de la machine à vide
        # On calcule le temps de fonctionnement de la machine
        total_on_time = 0
        for i in range(len(self._stop_times)):
            total_on_time += self._stop_times[i] - self._start_times[i]

        # Pareil ici on calcul le temps de fonctionnement de la dernière opération si la machine est encore en marche pour calculer le temps à vide
        total_setup_time = len(self.start_times) * self._set_up_time
        total_teardown_time = len(self.stop_times) * self._tear_down_time

        # Pareil temps total de traitement des opérations pour le calcul du temps à vide
        total_processing_time = sum(op.processing_time for op in self._scheduled_operations)

        # Calcul du temps d'inactivité
        total_idle_time = total_on_time - total_setup_time - total_teardown_time - total_processing_time

        # Calcule de l'énergie consommée à vide
        energy_idle = max(0, total_idle_time) * self._min_consumption

        return energy_setup + energy_teardown + energy_processing + energy_idle

    def __str__(self):
        return f"M{self.machine_id}"

    def __repr__(self):
        return str(self)
