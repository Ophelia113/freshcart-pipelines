# Use Mage's decorators if available, otherwise no-op stand-ins (so pytest/CI can import this file too)
try:
    if 'transformer' not in globals():
        from mage_ai.data_preparation.decorators import transformer
    if 'test' not in globals():
        from mage_ai.data_preparation.decorators import test
except ImportError:
    def transformer(func):
        return func

    def test(func):
        return func


# Passes the table through unchanged, after printing the two facts we care about
@transformer
def validate(df, *args, **kwargs):
    print('Missing values:', int(df.isna().sum().sum()), '| Classes:', df['target'].nunique())
    return df


# Runs right after validate finishes: stops the pipeline if the data is not what we expect
@test
def test_output(output, *args):
    assert output.isna().sum().sum() == 0, 'Missing values found'
    assert output['target'].nunique() == 3, 'Expected exactly 3 classes'
