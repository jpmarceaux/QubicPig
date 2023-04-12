import pygsti
from qupig import *


class RPERunnerX90:
    """

    """
    sin_circs: dict

    def __init__(self, target_qubit: str, max_max_depth: int):
        self.qid = target_qubit
        self.max_depths = [2**i for i in range(max_max_depth)]

    def make_cos_circuit(self, power: int):
        return pygsti.circuits.Circuit([[('Gxpi2', self.qid)]])*power
    def make_sin_circuit(self, power: int):
        return (pygsti.circuits.Circuit([[('Gxpi2', self.qid)]])*power + pygsti.circuits.Circuit([[('Gxpi2', self.qid)]]))
    def _make_pygsti_circuits(self):
        self.sin_circs = {i: self.make_sin_circuit(i) for i in self.max_depths}
        self.cos_circs = {i: self.make_cos_circuit(i) for i in self.max_depths}
        self.all_circs_needing_data = list(self.sin_circs.values()) + list(self.cos_circs.values())

    def make_qubic_circuits(self, drive_freq, drive_amp):
        qubic_circuits = []
        for pcirc in self.all_circs_needing_data:
            qcirc = [{'name' : 'delay', 't' : 400.e-6}]
            for layer in pcirc:
                qcirc.append({'name' : pygsti_to_qubic[layer[0]], 'qubit' : [layer[1]],
                              'modi': {(0, 'amp') : drive_amp, (0, 'fcarrier'): drive_freq}})
            qcirc.append({'name': 'read', 'qubit': [self.qid]})
            qubic_circuits.append(qcirc)





