

#from pprint import pprint

TEXT_CELL_PREFIX = "'markdown' cell: "
CODE_CELL_PREFIX = "'code' cell: "
#OUTPUT_PREFIX = " with output: "


def parse_cell_type(cell_content):

    # cell type (they are clearly marked at the beginning)
    if TEXT_CELL_PREFIX in cell_content:
        cell_type = "TEXT"
    elif CODE_CELL_PREFIX in cell_content:
        cell_type = "CODE"
    else:
        cell_type = None
    return cell_type



def split_text_by_substrings(input_text, substring_a=TEXT_CELL_PREFIX, substring_b=CODE_CELL_PREFIX):
    """Source: https://chat.openai.com/share/3af75e94-a455-4fae-94e4-b0a3ce2d7578 """

    result = []
    current_string = ""
    for line in input_text.splitlines():
        if substring_a in line:
            if current_string:
                result.append(current_string.strip())
            current_string = line
        elif substring_b in line:
            if current_string:
                result.append(current_string.strip())
            current_string = line
        else:
            current_string += " " + line

    if current_string:
        result.append(current_string.strip())

    return result


#
#
#import ast
#
#def separate_code_and_output(input_string):
#    # Split the input string into individual cell strings
#    cell_strings = input_string.split(',')
#
#    code_cells = []
#    output_cells = []
#
#    for i in range(0, len(cell_strings), 2):
#        # Extract code cell content
#        code_cell_content = ast.literal_eval(cell_strings[i].split(':')[1].strip())
#        code_cells.append(code_cell_content)
#
#        # Check for output
#        if i + 1 < len(cell_strings):
#            output_index = cell_strings[i + 1].find('with output:')
#            if output_index != -1:
#                # Extract output content
#                output_content = ast.literal_eval(cell_strings[i + 1][output_index + 12:].strip())
#                output_cells.append(output_content)
#
#    return code_cells, output_cells
#
#
#
#if __name__ == "__main__":
#
#
#    input_string = """
#    'markdown' cell: '['Long running python processes can be interrupted. Run the following cell and select **Runtime -> Interrupt execution** (*hotkey: Cmd/Ctrl-M I*) to stop execution.']',
#    'code' cell: '['import time', 'print("Sleeping")', 'time.sleep(30) # sleep for a while; interrupt me!', 'print("Done Sleeping")']' with output: '['Sleeping\\n']',
#    'markdown' cell: '['## System aliases', '', 'Jupyter includes shortcuts for common operations, such as ls:']',
#    'code' cell: '['!ls /bin']' with output: '["'['\\t\\t\\t\\t      mknod\\n", ' 7z\\t\\t\\t\\t      mktemp\\n', ' 7za\\t\\t\\t\\t      mm2gv\\n', ' 7zr\\t\\t\\t\\t      more\\n', ' aclocal\\t\\t\\t      mount\\n', ' aclocal-1.16\\t\\t\\t      mountpoint\\n', ' acyclic\\t\\t\\t      mpexpand\\n', ' add-apt-repository\\t\\t      mpic++\\n', ' addpart\\t\\t\\t      mpicc\\n', ' addr2line\\t\\t\\t      mpiCC\\n']"',
#    'markdown' cell: '['That `!ls` probably generated a large output. You can select the cell and clear the output by either:', '', '1. Clicking on the clear output button (x) in the toolbar above the cell; or', '2. Right clicking the left gutter of the output area and selecting "Clear output" from the context menu.', '', 'Execute any other process using `!` with string interpolation from python variables, and note the result can be assigned to a variable:']',
#    'markdown' cell: '['## Magics', "Colaboratory shares the notion of magics from Jupyter. There are shorthand annotations that change how a cell's text is executed. To learn more, see [Jupyter's magics page](http://nbviewer.jupyter.org/github/ipython/ipython/blob/1.x/examples/notebooks/Cell%20Magics.ipynb)."]'
#    """
#
#    cells = split_text_by_substrings()
#
#    code_cells, output_cells = separate_code_and_output(input_string)
#
#    # Print the separated content
#    print("Code Cells:")
#    for code_cell in code_cells:
#        print(code_cell)
#
#    print("\nOutput Cells:")
#    for output_cell in output_cells:
#        print(output_cell)
#
