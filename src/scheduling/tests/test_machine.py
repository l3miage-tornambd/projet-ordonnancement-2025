'''
Tests for the Machine class

@author: Vassilissa Lehoux
'''
import unittest
from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation

class TestMachine(unittest.TestCase):


    def setUp(self):
        self.machine = Machine(
            machine_id=0,
            set_up_time=10,
            set_up_energy=50,
            tear_down_time=5,
            tear_down_energy=20,
            min_consumption=2,  # Énergie par seconde quand la machine est à vide
            end_time=200
        )

        # On crée des opérations prêtes à être planifiées
        self.op1 = Operation(job_id=0, operation_id=0)
        self.op1.machine_options[0] = (15, 100)  # duration=15, energy=100 sur machine 0

        self.op2 = Operation(job_id=1, operation_id=0)
        self.op2.machine_options[0] = (20, 120)  # duration=20, energy=120 sur machine 0

    def tearDown(self):
        self.machine.reset()

    def testWorkingTime(self):
        """Teste le calcul du temps de travail total de la machine."""
        # Au début, le temps de travail est 0
        self.assertEqual(self.machine.working_time, 0)

        # On ajoute une opération. La machine démarre, son temps de travail augmente.
        # L'opération commence après le setup (10s), et dure 15s. Fin à t=25.
        self.machine.add_operation(self.op1)
        # La machine est "ON" de t=0 (pour commencer le setup) à t=25 (fin op1)
        # Note: add_operation définit le début du setup à start_time - setup_time.
        # op1 start_time = 10, setup = 10 -> machine_start_time = 0.
        # Le temps de travail est `available_time - start_time` = 25 - 0 = 25.
        self.assertEqual(self.machine.working_time, 25)

        # On arrête la machine à t=30
        self.machine.stop(at_time=30)
        # Le temps de travail est maintenant fixé par le stop_time : 30 - 0 = 30
        self.assertEqual(self.machine.working_time, 30)

    def testTotalEnergyConsumption(self):
        """Teste le calcul de la consommation totale d'énergie."""
        # On crée un scénario complet : start -> op1 -> op2 -> stop

        # Ajout op1. start_time=10, end_time=25. Machine ON de t=0.
        self.machine.add_operation(self.op1)
        # Ajout op2. start_time=25, end_time=45
        self.machine.add_operation(self.op2)

        # On arrête la machine à t=50 (après la fin de op2 + teardown time)
        self.machine.stop(at_time=50)

        # Calculons l'énergie attendue :
        # 1. Énergie de transition : 1 setup + 1 teardown
        #    E_setup_teardown = 50 + 20 = 70
        e_setup_teardown = self.machine._set_up_energy + self.machine._tear_down_energy
        self.assertEqual(e_setup_teardown, 70)

        # 2. Énergie des opérations : op1 + op2
        #    E_processing = 100 + 120 = 220
        e_processing = self.op1.energy + self.op2.energy
        self.assertEqual(e_processing, 220)

        # 3. Énergie à vide (idle)
        #    Temps total ON = stop_time - start_time = 50 - 0 = 50s
        #    Temps de setup = 10s
        #    Temps de teardown = 5s
        #    Temps de production = op1.duration + op2.duration = 15 + 20 = 35s
        #    Temps idle = 50 - 10 - 5 - 35 = 0s
        #    E_idle = 0 * min_consumption = 0

        # Énergie totale attendue = 70 + 220 + 0 = 290
        self.assertEqual(self.machine.total_energy_consumption, 290)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()