'''
Information for the instance of the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List, Dict, Tuple
import os
import csv

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation
from src.scheduling.instance.machine import Machine


class Instance(object):
    '''
    classdocs
    '''

    def __init__(self, instance_name):
        self._instance_name = instance_name
        self._jobs : dict[int, Job] = {}
        self._machines : dict[int, Machine] = {}
        self._operations: List[Operation] = []
        # self._operations : Dict[Tuple[int, int], Operation] = {} # Note : on pourrait passer par un dictionnaire pour augmenter la performance

    @classmethod
    def from_file(cls, folderpath: str) -> 'Instance':
        """
        Méthode "factory" pour créer une instance à partir d'un dossier de données.
        """
        instance_name = os.path.basename(folderpath)
        inst = cls(instance_name)

        # Lecture des informations sur les machines
        mach_filepath = os.path.join(folderpath, f"{inst._instance_name}_mach.csv")
        with open(mach_filepath, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            for row in csv_reader:
                machine_id, set_up_time, set_up_energy, tear_down_time, \
                    tear_down_energy, min_consumption, end_time = map(int, row)

                new_machine = Machine(machine_id, set_up_time, set_up_energy, tear_down_time,
                                      tear_down_energy, min_consumption, end_time)
                inst._machines[machine_id] = new_machine

        # Lecture des informations sur les opérations
        op_filepath = os.path.join(folderpath, f"{inst._instance_name}_op.csv")
        with open(op_filepath, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            for row in csv_reader:
                job_id, op_id, machine_id, proc_time, energy = map(int, row)

                # Créer le Job s'il n'existe pas encore
                if job_id not in inst._jobs:
                    inst._jobs[job_id] = Job(job_id)

                # On doit chercher dans la liste si l'opération existe déjà
                current_op = None
                for op in inst._operations:
                    if op.job_id == job_id and op.operation_id == op_id:
                        current_op = op
                        break  # On a trouvé l'opération, on arrête la recherche

                # Si on n'a pas trouvé l'opération, il faut la créer
                if current_op is None:
                    current_op = Operation(job_id, op_id)
                    inst._operations.append(current_op)
                    # Ajouter l'opération à son job (crée les contraintes de précédence)
                    inst._jobs[job_id].add_operation(current_op)

                # Ajouter l'option de machine à l'opération (qu'elle soit nouvelle ou trouvée)
                current_op.machine_options[machine_id] = (proc_time, energy)

        return inst

    @property
    def name(self):
        return self._instance_name

    @property
    def machines(self) -> List[Machine]:
        return list(self._machines.values())

    @property
    def jobs(self) -> List[Job]:
        return list(self._jobs.values())

    @property
    def operations(self) -> List[Operation]:
        return self._operations

    @property
    def nb_jobs(self):
        return len(self._jobs)

    @property
    def nb_machines(self):
        return len(self._machines)

    @property
    def nb_operations(self):
        return len(self._operations)

    def __str__(self):
        return f"{self.name}_M{self.nb_machines}_J{self.nb_jobs}_O{self.nb_operations}"

    def get_machine(self, machine_id) -> Machine:
        return self._machines.get(machine_id)

    def get_job(self, job_id) -> Job:
        return self._jobs.get(job_id)

    def get_operation(self, operation_id) -> Operation:
        return self._operations[operation_id] if operation_id < len(self._operations) else None