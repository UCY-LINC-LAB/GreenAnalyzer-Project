import pandas as pd


class Model(object):
    dataset: pd.DataFrame = None

    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset

    def train(self):
        raise NotImplementedError

    def predict(self):
        raise NotImplementedError



class LinearRegressionModel(Model):
    name: str = "LinearRegressionModel"
    a: float = None
    b: float = None

    def train(self):
        # ... train the model
        self.a = 0.5
        self.b = 1

    def predict(self, x):
        if self.a is None or self.b is None:
            raise ValueError("Model must be trained before predicting")
        return self.a * x + self.b

class RandomForestModel(Model):
    name: str = "RandomForestModel"
    n_estimators: int = None
    max_depth: int = None

    def train(self):
        self.n_estimators = 100
        self.max_depth = 10


df = pd.DataFrame()
for i in [LinearRegressionModel(df), RandomForestModel(df)]:
    i.train()
    for x in [...]:
        i.predict(x)

def compute_smape(y_true, X, model: Model):
    ...



lr = LinearRegressionModel(df)
lr.a
print(lr.a)
lr.a = 0.6
print(lr.a)
lr.train()
print(lr.a)
lr.predict(6.0)
