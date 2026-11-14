from sklearn.datasets import load_iris
from iris_project.transformers import validate_data


def test_validate_passes_clean_iris():
    df = load_iris(as_frame=True).frame
    out = validate_data.validate(df)
    validate_data.test_output(out)      # the block's own @test checks (no missing values, 3 classes)