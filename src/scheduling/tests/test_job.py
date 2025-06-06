'''
Tests for the Job class

@author: Vassilissa Lehoux
'''
import unittest
from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation, OperationScheduleInfo

class TestJob(unittest.TestCase):

    # Lancé avant chaque test
    def setUp(self):
        self.job = Job(job_id=0)
        self.op1 = Operation(job_id=0, operation_id=0)
        self.op2 = Operation(job_id=0, operation_id=1)

        self.job.add_operation(self.op1)
        self.job.add_operation(self.op2)

    # Lancé après chaque test
    def tearDown(self):
        pass


    def testCompletionTime(self):
        # Cas 1: Job avec des opérations non planifiées
        # La dernière op n'est pas planifiée, son end_time est -1, donc celui du job aussi.
        self.assertEqual(self.job.completion_time, -1, "Completion time should be -1 for unscheduled job")

        # Cas 2: Job avec opérations planifiées
        # On simule la planification des opérations
        # op1 est planifiée pour se terminer à t=15
        self.op1._schedule_info = OperationScheduleInfo(machine_id=0, schedule_time=10, duration=5,
                                                        energy_consumption=100)

        # Le job n'est toujours pas fini, la dernière op (op2) n'étant pas planifiée
        self.assertEqual(self.job.completion_time, -1, "Completion time should be -1 if last op is not scheduled")

        # op2 est planifiée pour commencer à la fin de op1 (15) et durer 7
        self.op2._schedule_info = OperationScheduleInfo(machine_id=1, schedule_time=15, duration=7,
                                                        energy_consumption=100)
        # Le end_time de op2 est maintenant 15 + 7 = 22. Le job doit se terminer à t=22.
        self.assertEqual(self.job.completion_time, 22, "Completion time should match the last operation's end time")

        # Cas 3: Job vide
        empty_job = Job(job_id=1)
        self.assertEqual(empty_job.completion_time, 0, "Completion time for an empty job should be 0")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
