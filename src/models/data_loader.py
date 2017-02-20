import numpy as np


class DataLoader:
    @staticmethod
    def load_data(file_name):
        with open(file_name, 'r') as f:
            data = np.loadtxt(f, delimiter=',')
            return data[:, [0-18]], data[:, [19]]