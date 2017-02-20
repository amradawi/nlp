from data_loader import DataLoader
from sklearn import tree


class DTreeClassifier:
    def __init__(self, input_file):
        self.input_file = input_file
        self.dtree = tree.DecisionTreeClassifier()
        self.data, self.labels = DataLoader.load_data(input_file)

    def train_model(self):
        return self.dtree.fit(self.data, self.labels)
