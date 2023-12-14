
import os

from langchain.docstore.document import Document
from pandas import DataFrame

from app.document_processor import DocumentProcessor


def test_document_processor():

    #notebook_filepath = os.path.join(os.path.dirname(__file__), "documents", "Making_the_Most_of_your_Colab_Subscription.ipynb")
    notebook_filepath = os.path.join(os.path.dirname(__file__), "documents", "Overview_of_Colaboratory_Features.ipynb")
    dp = DocumentProcessor(notebook_filepath)
    cells = dp.cells

    assert len(dp.docs) == 1
    assert dp.doc == dp.docs[0]
    assert isinstance(dp.doc, Document)

    # CELLS

    assert len(dp.cells) == 22
    assert len(dp.text_cells) == 18
    assert len(dp.code_cells) == 4

    assert isinstance(dp.cells[0], Document)
    assert dp.cells[0].metadata == {
        'filename': 'Overview_of_Colaboratory_Features.ipynb',
        'cell_id': 1,
        'cell_type': 'TEXT',
        'cell_length': 164
    }
    assert dp.cells[0].page_content == "'markdown' cell: '['# Cells', 'A notebook is a list of cells. Cells contain either explanatory text or executable code and its output. Click a cell to select it.']'"

    assert [cell.page_content for cell in dp.cells] == [
        "'markdown' cell: '['# Cells', 'A notebook is a list of cells. Cells contain either explanatory text or executable code and its output. Click a cell to select it.']'",
        "'markdown' cell: '['## Code cells', 'Below is a **code cell**. Once the toolbar button indicates CONNECTED, click in the cell to select it and execute the contents in the following ways:', '', '* Click the **Play icon** in the left gutter of the cell;', '* Type **Cmd/Ctrl+Enter** to run the cell in place;', '* Type **Shift+Enter** to run the cell and move focus to the next cell (adding one if none exists); or', '* Type **Alt+Enter** to run the cell and insert a new code cell immediately below it.', '', 'There are additional options for running some or all cells in the **Runtime** menu.']'",
        "'markdown' cell: '['## Text cells', 'This is a **text cell**. You can **double-click** to edit this cell. Text cells', 'use markdown syntax. To learn more, see our [markdown', 'guide](/notebooks/markdown_guide.ipynb).', '', 'You can also add math to text cells using [LaTeX](http://www.latex-project.org/)', 'to be rendered by [MathJax](https://www.mathjax.org). Just place the statement', 'within a pair of **\\\\$** signs. For example `$\\\\sqrt{3x-1}+(1+x)^2$` becomes', '$\\\\sqrt{3x-1}+(1+x)^2.$']'",
        '\'markdown\' cell: \'[\'## Adding and moving cells\', \'You can add new cells by using the **+ CODE** and **+ TEXT** buttons that show when you hover between cells. These buttons are also in the toolbar above the notebook where they can be used to add a cell below the currently selected cell.\', \'\', \'You can move a cell by selecting it and clicking **Cell Up** or **Cell Down** in the top toolbar.\', \'\', \'Consecutive cells can be selected by "lasso selection" by dragging from outside one cell and through the group.  Non-adjacent cells can be selected concurrently by clicking one and then holding down Ctrl while clicking another.  Similarly, using Shift instead of Ctrl will select all intermediate cells.\']\'',
        "'markdown' cell: '['# Working with python', 'Colaboratory is built on top of [Jupyter Notebook](https://jupyter.org/). Below are some examples of convenience functions provided.']'",
        "'markdown' cell: '['Long running python processes can be interrupted. Run the following cell and select **Runtime -> Interrupt execution** (*hotkey: Cmd/Ctrl-M I*) to stop execution.']'",
        '\'code\' cell: \'[\'import time\', \'print("Sleeping")\', \'time.sleep(30) # sleep for a while; interrupt me!\', \'print("Done Sleeping")\']\'  with output: \'[\'Sleeping\\n\']\'',
        "'markdown' cell: '['## System aliases', '', 'Jupyter includes shortcuts for common operations, such as ls:']'",
        '\'code\' cell: \'[\'!ls /bin\']\'  with output: \'["\'[\'\\t\\t\\t\\t      mknod\\n", \' 7z\\t\\t\\t\\t      mktemp\\n\', \' 7za\\t\\t\\t\\t      mm2gv\\n\', \' 7zr\\t\\t\\t\\t      more\\n\', \' aclocal\\t\\t\\t      mount\\n\', \' aclocal-1.16\\t\\t\\t      mountpoint\\n\', \' acyclic\\t\\t\\t      mpexpand\\n\', \' add-apt-repository\\t\\t      mpic++\\n\', \' addpart\\t\\t\\t      mpicc\\n\', \' addr2line\\t\\t\\t      mpiCC\\n\']\'',
        '\'markdown\' cell: \'[\'That `!ls` probably generated a large output. You can select the cell and clear the output by either:\', \'\', \'1. Clicking on the clear output button (x) in the toolbar above the cell; or\', \'2. Right clicking the left gutter of the output area and selecting "Clear output" from the context menu.\', \'\', \'Execute any other process using `!` with string interpolation from python variables, and note the result can be assigned to a variable:\']\'',
        '\'markdown\' cell: \'[\'## Magics\', "Colaboratory shares the notion of magics from Jupyter. There are shorthand annotations that change how a cell\'s text is executed. To learn more, see [Jupyter\'s magics page](http://nbviewer.jupyter.org/github/ipython/ipython/blob/1.x/examples/notebooks/Cell%20Magics.ipynb)."]\'',
        "'markdown' cell: '['## Automatic completions and exploring code', '', 'Colab provides automatic completions to explore attributes of Python objects, as well as to quickly view documentation strings. As an example, first run the following cell to import the  [`numpy`](http://www.numpy.org) module.']'",
        "'code' cell: '['import numpy as np']'",
        "'markdown' cell: '['If you now insert your cursor after `np` and press **Period**(`.`), you will see the list of available completions within the `np` module. Completions can be opened again by using **Ctrl+Space**.']'",
        "'markdown' cell: '['If you type an open parenthesis after any function or class in the module, you will see a pop-up of its documentation string:']'",
        "'markdown' cell: '['The documentation can be opened again using **Ctrl+Shift+Space** or you can view the documentation for method by mouse hovering over the method name.', '', 'When hovering over the method name the `Open in tab` link will open the documentation in a persistent pane. The `View source` link will navigate to the source code for the method.']'",
        "'markdown' cell: '['## Exception Formatting']'",
        "'markdown' cell: '['Exceptions are formatted nicely in Colab outputs:']'",
        "'code' cell: '['x = 1', 'y = 4', 'z = y/(1-x)']' , gives error 'ZeroDivisionError',with description 'ignored'",
        "'markdown' cell: '['## Rich, interactive outputs', 'Until now all of the generated outputs have been text, but they can be more interesting, like the chart below.']'",
        '\'markdown\' cell: \'[\'# Integration with Drive\', \'\', \'Colaboratory is integrated with Google Drive. It allows you to share, comment, and collaborate on the same document with multiple people:\', \'\', \'* The **SHARE** button (top-right of the toolbar) allows you to share the notebook and control permissions set on it.\', \'\', \'* **File->Make a Copy** creates a copy of the notebook in Drive.\', \'\', "* **File->Save** saves the File to Drive. **File->Save and checkpoint** pins the version so it doesn\'t get deleted from the revision history.", \'\', "* **File->Revision history** shows the notebook\'s revision history."]\'',
        "'markdown' cell: '['## Commenting on a cell', 'You can comment on a Colaboratory notebook like you would on a Google Document. Comments are attached to cells, and are displayed next to the cell they refer to. If you have **comment-only** permissions, you will see a comment button on the top right of the cell when you hover over it.', '', 'If you have edit or comment permissions you can comment on a cell in one of three ways:', '', '1. Select a cell and click the comment button in the toolbar above the top-right corner of the cell.', '1. Right click a text cell and select **Add a comment** from the context menu.', '3. Use the shortcut **Ctrl+Shift+M** to add a comment to the currently selected cell.', '', 'You can resolve and reply to comments, and you can target comments to specific collaborators by typing *+[email address]* (e.g., `+user@domain.com`). Addressed collaborators will be emailed.', '', 'The Comment button in the top-right corner of the page shows all comments attached to the notebook.']'"
    ]

    assert len(dp.cells_df) == len(dp.cells)
    assert isinstance(dp.cells_df, DataFrame)
    assert sorted(dp.cells_df.columns.tolist()) == ['cell_id', 'cell_length', 'cell_type', 'filename', 'page_content']


    # CHUNKS

    assert len(dp.chunks) == 23 # more than the number of cells
    assert len(dp.chunks_df) == len(dp.chunks)
    assert sorted(dp.chunks_df.columns.tolist()) == ['cell_id', 'cell_length', 'cell_type', 'chunk_id', 'chunk_length', 'filename', 'page_content']
