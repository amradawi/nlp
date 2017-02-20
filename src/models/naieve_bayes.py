from sklearn.naive_bayes import MultinomialNB
import argparse
from data_loader import DataLoader
from svm import SVMCLassifier
from decision_tree import DTreeClassifier


class NBClassifier:
    def __init__(self, input_file):
        self.input_file = input_file
        self.mnb = MultinomialNB()
        self.data, self.labels = DataLoader.load_data(input_file)

    def train_model(self):
        return self.mnb.fit(self.data, self.labels)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Naieve Bayes classifier for tweets")
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    npc = NBClassifier(args.input_file)
    model = npc.train_model()
    print model.predict(npc.data[0])

    dt = DTreeClassifier(args.input_file)
    model = dt.train_model()
    print model.predict(dt.data[0])

    sv = SVMCLassifier(args.input_file)
    model = sv.train_model()
    print model.predict(sv.data[0])
