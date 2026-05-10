import pandas as pd
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer()
df = pd.DataFrame(data.data, columns=data.feature_names)
df['target'] = data.target

df.loc[10, 'mean radius'] = None
df.loc[20, 'mean texture'] = -999.0
df.loc[30, 'target'] = 2

df.to_csv('breast_cancer_data_dirty.csv', index=False)
print("Dirty dataset created: 'breast_cancer_data_dirty.csv'")
