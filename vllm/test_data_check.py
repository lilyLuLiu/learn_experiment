import pandas as pd
from deepchecks.tabular import Dataset
from deepchecks.tabular.checks import DataDuplicates, IsSingleValue, StringMismatch, TrainTestFeatureDrift
from deepchecks.tabular.suites import data_integrity 

def test_data_quality():
    # Load the dirty dataset
    df = pd.read_csv('breast_cancer_data_dirty.csv')
    
    # Create a Deepchecks Dataset
    ds = Dataset(df, label='target', features=[c for c in df.columns if c != 'target'], cat_features=[])

    suite =  data_integrity()
    suite_result = suite.run(ds)
    print(suite_result)
    assert suite_result.passed, f"Data integrity suite failed: {suite_result}"
    print("*****")

    # Run checks
    dup_check = DataDuplicates()
    dup_result = dup_check.run(ds)
    print(dup_result)
    assert dup_result.passed_conditions(), f"DataDuplicates check failed: {dup_result}"

    print("*****")
    const_check = IsSingleValue()
    const_result = const_check.run(ds)
    print(const_result)
    assert const_result.passed_conditions(), f"IsSingleValue check failed: {const_result}"

if __name__ == "__main__":
    test_data_quality()
    print("All checks passed successfully.")