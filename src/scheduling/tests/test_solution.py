'''
Test of the Solution class.

@author: Vassilissa Lehoux
'''
import unittest
import os

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA, TEST_FOLDER


class TestSolution(unittest.TestCase):

    def setUp(self):
        self.inst1 = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")

    def tearDown(self):
        for m in self.inst1.machines:
            m.reset()
        for j in self.inst1.jobs:
            j.reset()

    def test_init_sol(self):
        sol = Solution(self.inst1)
        self.assertEqual(len(sol.all_operations), len(self.inst1.operations),
                         'Nb of operations should be the same between instance and solution')
        self.assertEqual(len(sol.available_operations), len(self.inst1.jobs),
                         'One operation per job should be available for scheduling')

    def test_schedule_op(self):
        sol = Solution(self.inst1)
        operation = self.inst1.operations[0]
        machine = self.inst1.machines[1]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 12, 'wrong operation duration')
        self.assertEqual(operation.energy, 12, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 20, 'wrong set up time for machine')
        self.assertEqual(operation.end_time, 32, 'wrong operation end time')
        self.assertEqual(machine.available_time, 32, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[2]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 9, 'wrong operation duration')
        self.assertEqual(operation.energy, 10, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 41, 'wrong operation end time')
        self.assertEqual(machine.available_time, 41, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[1]
        machine = self.inst1.machines[0]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 5, 'wrong operation duration')
        self.assertEqual(operation.energy, 6, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 37, 'wrong operation end time')
        self.assertEqual(machine.available_time, 37, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        operation = self.inst1.operations[3]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 10, 'wrong operation duration')
        self.assertEqual(operation.energy, 9, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 41, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 51, 'wrong operation end time')
        self.assertEqual(machine.available_time, 51, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        self.assertTrue(sol.is_feasible, 'Solution should be feasible')
        plt = sol.gantt('tab20')
        plt.savefig(TEST_FOLDER + os.path.sep +  'temp.png')

    def test_evaluate(self):
        '''
        Teste l'évaluation d'une solution (makespan et énergie totale).
        On construit manuellement un ordonnancement simple et on vérifie les résultats.
        '''
        # 1. CONSTRUCTION MANUELLE DE L'ORDONNANCEMENT

        # On récupère les objets dont on a besoin depuis l'instance
        op00 = self.inst1.get_operation(0, 0)  # Opération 0 du Job 0
        op01 = self.inst1.get_operation(0, 1)  # Opération 1 du Job 0

        machine0 = self.inst1.get_machine(0)
        machine1 = self.inst1.get_machine(1)

        # Planifions op00 sur machine1
        # setup=20, proc_time=12. Début op: 20, Fin op: 32
        machine1.add_operation(op00, start_time=0)

        # Planifions op01 (successeur de op00) sur machine0
        # op01 est prête à t=32. machine0 a setup=15.
        # machine0 est prête à t=15. op01 commence à max(32, 15)=32.
        # proc_time=5. Début op: 32, Fin op: 37
        machine0.add_operation(op01, start_time=0)

        # On arrête les machines pour finaliser les calculs d'énergie
        machine0.stop(machine0.available_time)
        machine1.stop(machine1.available_time)

        # 2. ÉVALUATION MANUELLE DES RÉSULTATS

        # Makespan = Le moment où la dernière opération se termine
        makespan = op01.end_time  # car 37 > 32
        self.assertEqual(makespan, 37)

        # Énergie Totale = Énergie Machine 0 + Énergie Machine 1

        # --- Calcul Énergie Machine 0 ---
        # Cycle: start=17 (pour être prêt à 32), stop=37. Temps ON = 20
        # E_setup(4) + E_teardown(4) = 8
        # E_processing(op01) = 6
        # T_setup(15) + T_teardown(5) + T_proc(5) = 25.
        # T_idle = 20 - 25 = -5 -> 0. (Le setup a été "mangé" par l'attente)
        # E_idle = 0. Total_M0 = 8 + 6 = 14

        # --- Calcul Énergie Machine 1 ---
        # Cycle: start=0 (pour être prêt à 20), stop=32. Temps ON = 32
        # E_setup(5) + E_teardown(4) = 9
        # E_processing(op00) = 12
        # T_setup(20) + T_teardown(5) + T_proc(12) = 37.
        # T_idle = 32 - 37 = -5 -> 0.
        # E_idle = 0. Total_M1 = 9 + 12 = 21

        total_energy = machine0.total_energy_consumption + machine1.total_energy_consumption
        self.assertEqual(total_energy, 14 + 21, "Le calcul d'énergie totale est incorrect")

    def test_objective(self):
        '''
        Teste la valeur d'une "fonction objectif" spécifique.
        Ici, on va supposer que l'objectif est l'énergie totale.
        '''
        # On peut construire le même scénario ou un autre
        op00 = self.inst1.get_operation(0, 0)
        op12 = self.inst1.get_operation(1, 2)
        machine3 = self.inst1.get_machine(3)

        # Planifier les deux opérations sur la même machine
        machine3.add_operation(op00)  # setup=20, proc=8. Fin op: 28
        machine3.add_operation(op12)  # commence à 28, proc=5. Fin op: 33
        machine3.stop(machine3.available_time)

        # L'objectif est l'énergie totale de la solution.
        # Ici, seule la machine 3 a fonctionné.
        objective_value = machine3.total_energy_consumption

        # --- Calcul manuel pour M3 ---
        # Cycle: start=0, stop=33. Temps ON=33
        # E_setup(6) + E_teardown(5) = 11
        # E_proc(op00) = 15, E_proc(op12) = 7. Total E_proc = 22
        # T_setup(20) + T_teardown(5) + T_proc(8+5=13) = 38
        # T_idle = 33 - 38 = -5 -> 0
        # E_idle = 0.
        # Total M3 = 11 + 22 = 33

        self.assertEqual(objective_value, 33, "La valeur de l'objectif (énergie) est incorrecte")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
