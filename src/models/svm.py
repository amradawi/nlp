from data_loader import DataLoader
from sklearn.svm import SVC

class SVMCLassifier:
    def __init__(self, input_file):
        self.input_file = input_file
        self.model = SVC()
        self.data, self.labels = DataLoader.load_data(input_file)

    def train_model(self):
        return self.model.fit(self.data, self.labels)