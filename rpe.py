import matplotlib.pyplot as plt
import pygsti
import numpy as np
from qupig import *

from pygsti.modelpacks import smq1Q_XZ

from pyrpe.src.quapack.pyRPE.quantum import Q as RPE_Experiment
from pyrpe.src.quapack.pyRPE import RobustPhaseEstimation
from chipspec import ChipSpec
class RpeX90:
    """
    Class that can:
        1) make RPE circuit experiment designs
        2) fit curves to RPE results
        3) plot curves
    """
    sin_circs: dict

    def __init__(self, chipspec: ChipSpec, target_qubit: str, max_max_depth=7):
        self.qid = target_qubit
        self.max_depths = [2**i for i in range(max_max_depth)]
        self.chipspec = chipspec

    def update_drive_amp(self, drive_amp):
        self.chipspec.update(('Gates', f'{self.qid}X90', 0, 'amp'), drive_amp)

    def update_frequency(self, frequency):
        self.chipspec.update(('Qubits', self.qid, 'freq'), frequency)

    def circuits(self, drive_freq, drive_amp):
        return {circ: self.chipspec.qubic_instructions(circ) for circ in self.all_circuits_needing_data}

    @property
    def all_circuits_needing_data(self):
        return list(self.cos_circs.values())+list(self.sin_circs.values())
    def make_cos_circuit(self, power: int):
        return pygsti.circuits.Circuit([[('Gxpi2', 0)]])*power + pygsti.circuits.Circuit([[('Gxpi2', 0)]])
    def make_sin_circuit(self, power: int):
        return pygsti.circuits.Circuit([[('Gxpi2', 0)]])*power
    def _make_pygsti_circuits(self):
        self.sin_circs = {i: self.make_sin_circuit(i) for i in self.max_depths}
        self.cos_circs = {i: self.make_cos_circuit(i) for i in self.max_depths}
    def simulate_target(self, num_samples):
        """
        Simulate the pygsti circuits at the target model in infinite shot limit
        :return:
        """
        cos_dataset = pygsti.data.simulate_data(self.chipspec.target_model, list(self.cos_circs.values()),
                                                        num_samples=num_samples, sample_error='multinomial', seed=None)
        sin_dataset = pygsti.data.simulate_data(self.chipspec.target_model, list(self.sin_circs.values()),
                                                num_samples=num_samples, sample_error='multinomial', seed=None)
        return cos_dataset, sin_dataset

    def process_rpe(self, cos_dataset, sin_dataset):
        # Post-process the RPE data from the pyGSTi dataset
        the_experiment = RPE_Experiment()
        for i in self.max_depths:
            the_experiment.process_sin(i, (int(sin_dataset[self.sin_circs[i]]['0']), int(sin_dataset[self.sin_circs[i]]['1'])))
            the_experiment.process_cos(i, (int(cos_dataset[self.cos_circs[i]]['0']), int(cos_dataset[self.cos_circs[i]]['1'])))
        return RobustPhaseEstimation(the_experiment)

    def plot_rpe_verbose(self, cos_dataset, sin_dataset):
        # 1st process the dataset -- probably should design so that I don't have to process every time
        fit = self.process_rpe(cos_dataset, sin_dataset)
        fig, axs = plt.subplots(3, 1)
        sin_expectations = [cos_dataset[c]['1'] for c in self.cos_circs.values()]
        cos_expectations = [sin_dataset[c]['1'] for c in self.sin_circs.values()]
        print(cos_expectations)
        axs[0].plot(sin_expectations)
        axs[0].set_ylim([0, 100])
        axs[1].plot(cos_expectations)
        axs[1].set_ylim([0, 100])
        axs[2].plot(fit.angle_estimates)
        axs[2].plot((0, len(fit.angle_estimates)), (np.pi/2, np.pi/2), c='red')
        num_estimates = len(fit.angle_estimates)
        axs[2].fill_between(range(num_estimates),
                            [fit.angle_estimates[i] + 1/(i+1) for i in range(num_estimates)],
                            [fit.angle_estimates[i] - 1/(i+1) for i in range(num_estimates)])
        axs[2].set_ylim([0, np.pi])












