
from app.submissions_manager import SubmissionsManager

from conftest import TEST_DOCS_DIRPATH

def test_submissions_manager():

    # WITHOUT STARTER FILE:

    sm = SubmissionsManager(dirpath=TEST_DOCS_DIRPATH, starter_filename=None)
    assert sm.dirpath == TEST_DOCS_DIRPATH
    assert len(sm.filenames) == 2
    assert len(sm.filepaths) == 2
    assert sm.starter_filepath == None

    assert sm.find_filepath("OOPS") == None
    #assert sm.find_filepath("Subscription") == "test/documents/Making_the_Most_of_your_Colab_Subscription.ipynb"
    assert "test/documents/Making_the_Most_of_your_Colab_Subscription.ipynb" in sm.find_filepath("Subscription")

    # WITH STARTER FILE:

    sm = SubmissionsManager(dirpath=TEST_DOCS_DIRPATH, starter_filename="Overview_of_Colaboratory_Features.ipynb")
    assert sm.dirpath == TEST_DOCS_DIRPATH
    assert len(sm.filenames) == 2
    assert len(sm.filepaths) == 2
    #assert sm.starter_filepath == "test/documents/Overview_of_Colaboratory_Features.ipynb"
    assert "test/documents/Overview_of_Colaboratory_Features.ipynb" in sm.starter_filepath
