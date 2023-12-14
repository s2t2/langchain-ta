
from pandas import DataFrame


from app.submissions_processor import SubmissionsProcessor

from conftest import TEST_DOCS_DIRPATH, TEST_RESULTS_DIRPATH


EXPECTED_NOTEBOOK_RECORDS = [
    {
        'filename': 'Making_the_Most_of_your_Colab_Subscription.ipynb',
        'file_id': 'the', # default id not the best for the test files. it's ok. todo: revisit
        'length': 6497,
        'cells': 11,
        'code_cells': 2,
        'text_cells': 9,
        'avg_code_cell_length': 329.0,
        'avg_text_cell_length': 645.2,
    },
    {
        'filename': 'Overview_of_Colaboratory_Features.ipynb',
        'file_id': 'of', # default id not the best for the test files. it's ok. todo: revisit
        'length': 6888,
        'cells': 22,
        'code_cells': 4,
        'text_cells': 18,
        'avg_code_cell_length': 169.0,
        'avg_text_cell_length': 341.1,

    }
]

def test_submissions_processor():

    sp = SubmissionsProcessor(dirpath=TEST_DOCS_DIRPATH, results_dirpath=TEST_RESULTS_DIRPATH, starter_filename="Overview_of_Colaboratory_Features.ipynb")
    sp.perform()

    assert isinstance(sp.notebooks_df, DataFrame)
    assert sp.notebooks_df.to_dict("records") == EXPECTED_NOTEBOOK_RECORDS

    assert isinstance(sp.cells_df, DataFrame)
    assert len(sp.cells_df) == 33
    assert sp.cells_df.columns.tolist() == ['file_id', 'filename', 'cell_id', 'cell_length', 'cell_type', 'is_empty', 'page_content', 'dup_content', 'starter_cell_id', 'starter_content']
    assert sp.cells_df["is_empty"].sum() == 0 # there are no blank cells in the test notebooks
    assert sp.cells_df["dup_content"].sum() == 0 # there are no overlapping cells in the test notebooks
    assert sp.cells_df["starter_content"].sum() == 22

    starter_cells = sp.cells_df[sp.cells_df["filename"] == sp.starter_filename]
    other_cells = sp.cells_df[sp.cells_df["filename"] != sp.starter_filename]
    assert len(starter_cells) == 22
    assert len(other_cells) == 11



def test_submissions_processor_without_starter():

    sp = SubmissionsProcessor(dirpath=TEST_DOCS_DIRPATH, results_dirpath=TEST_RESULTS_DIRPATH, starter_filename=None)
    sp.perform()

    assert isinstance(sp.notebooks_df, DataFrame)
    assert sp.notebooks_df.to_dict("records") == EXPECTED_NOTEBOOK_RECORDS

    assert isinstance(sp.cells_df, DataFrame)
    assert len(sp.cells_df) == 33
    assert sp.cells_df.columns.tolist() == ['file_id', 'filename', 'cell_id', 'cell_length', 'cell_type', 'is_empty', 'page_content', 'dup_content', 'starter_cell_id', 'starter_content']
    assert sp.cells_df["is_empty"].sum() == 0 # there are no blank cells in the test notebooks
    assert sp.cells_df["dup_content"].sum() == 0 # there are no overlapping cells in the test notebooks
    assert sp.cells_df["starter_content"].sum() == 0 # no starter if we don't want it
