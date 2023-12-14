from warnings import filterwarnings
filterwarnings("ignore")

import os
from pandas import DataFrame, merge
import plotly.express as px

from app import DATA_DIRPATH
from app.submissions_manager import SubmissionsManager
from app.document_processor import DocumentProcessor, print_docs, print_rows
from app.colors import CELL_COLORS_MAP


EMPTY_CODE_CELL = "'code' cell: '[]'"
EMPTY_TEXT_CELL = "'markdown' cell: '[]'"


if __name__ == "__main__":

    sm = SubmissionsManager()
    print(sm.dirpath)
    print(len(sm.filenames))

    # STARTER NOTEBOOK:

    starter_filepath = sm.find_filepath("STARTER")
    print(starter_filepath)
    starter_dp = DocumentProcessor(starter_filepath)
    starter_cells = starter_dp.cells

    # ALL NOTEBOOKS:

    all_cells = []
    records = []
    for filepath in sm.filepaths:
        dp = DocumentProcessor(filepath, verbose=False)
        avg_lengths = dp.cells_df.groupby("cell_type")["cell_length"].mean()
        record = {
            "notebook": dp.filename,
            "length": len(dp.doc.page_content), #dp.docs_df["cell_length"].sum(),
            "cells": len(dp.cells),
            "code_cells": len(dp.code_cells),
            "text_cells": len(dp.text_cells),
            "code_avg_length": avg_lengths["CODE"].round(1),
            "text_avg_length": avg_lengths["TEXT"].round(1),

        }
        records.append(record)
        all_cells += dp.cells
    print("NOTEBOOKS:", len(records))
    print("CELLS:", len(all_cells))

    notebooks_df = DataFrame(records)
    notebooks_df.index = notebooks_df["notebook"]
    notebooks_df.drop(columns=["notebook"], inplace=True)
    notebooks_df.to_csv(os.path.join(DATA_DIRPATH, "notebooks.csv"), index=False)
    #notebooks_df.head()

    chart_df = notebooks_df.copy()
    chart_df["filename"] = chart_df.index
    fig = px.violin(chart_df, x="length", box=True, points="all", height=400,
            title="Document Lengths (All Submissions)",
            hover_data=["filename"]
    )
    #fig.show()

    # ALL CELLS

    cells_df = DataFrame([cell.metadata for cell in all_cells])

    # ... DUPLICATED CONTENT ANALYSIS

    cells_df['dup_content'] = cells_df.duplicated(subset='page_content', keep=False)
    print("------")
    print(cells_df["dup_content"].value_counts())

    # ... STARTER CONTENT DIFFING (~30% of cells are the same as starter cells)

    #starter_rows = cells_df[ cells_df["filename"].str.contains("STARTER") ]
    starter_rows = cells_df[ cells_df["filename"] == starter_dp.filename ]
    cells_df = merge(cells_df, starter_rows[["cell_id", "page_content"]], how='left', on='page_content', suffixes=('', '_starter'))
    cells_df.rename(columns={"cell_id_starter": "starter_cell_id"}, inplace=True)
    cells_df["starter_content"] = cells_df['starter_cell_id'].notna()
    print("------")
    print(cells_df["starter_content"].value_counts())

    # ... EMPTY / BLANK CONTENT FILTERING
    cells_df["is_empty"] = cells_df["page_content"].map(lambda page_content: True if page_content.strip() in [EMPTY_CODE_CELL, EMPTY_TEXT_CELL] else False)
    print("------")
    print(cells_df["is_empty"].value_counts())

    print("------")
    print("DUPLICATE NON-STARTER NON-BLANK CELLS:")
    #dup_rows = cells_df[ (cells_df["starter_content"] == False) & (cells_df["dup_content"] == True) & (cells_df["is_empty"] == False)]
    dup_rows = cells_df[ (cells_df["starter_content"] == False) & (cells_df["dup_content"] == True) & (cells_df["is_empty"] == False)].sort_values(by="page_content")
    #for row in dup_rows:
    #    print(row)
    print_rows(dup_rows)

    cells_df.to_csv(os.path.join(DATA_DIRPATH, "all_cells.csv"), index=False)



    # PLOTTING...

    #print("NON-STARTER DUP CELLS:")
    #nonstarter_dups = cells_df[ (cells_df["dup_content"] == True) & (cells_df["starter_content"] == False) ]
    #for i, row in nonstarter_dups.iterrows():
    #    if row["page_content"].strip() not in [EMPTY_CODE_CELL, EMPTY_TEXT_CELL]:
    #        print("----")
    #        #print(row["filename"][0:25], row["cell_id"])
    #        print(row["page_content"][0:250])

    #cells_df.to_csv("cells.csv", index=False)
    #print(all_cells_df.shape)
    #all_cells_df.head()

    chart_df = cells_df.copy()
    chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
    fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500,
            title="Cell Lengths (All Submissions)",
            hover_data=["page_content"], facet_row="cell_type",
            color="cell_type", color_discrete_map=CELL_COLORS_MAP
    )
    fig.show()

    # cells_df[cells_df["page_content"].str.contains("  with output: ") ]

    # NON-STARTER CELLS:

    chart_df = cells_df.copy()
    chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
    chart_df = chart_df[chart_df["starter_content"] == False]
    fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500,
            title="Non-Starter Cell Lengths (All Submissions)",
            hover_data=["page_content"], facet_row="cell_type",
            color="cell_type", color_discrete_map=CELL_COLORS_MAP
    )
    fig.show()

    # UNIQUE CELLS

    #cells_df.groupby(["cell_type", "dup_content"])["cell_length"].describe()

    chart_df = cells_df.copy()
    chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
    chart_df = chart_df[chart_df["dup_content"] == False]
    fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500,
            title="Unique Cell Lengths (All Submissions)",
            hover_data=["page_content"], facet_row="cell_type",
            color="cell_type", color_discrete_map=CELL_COLORS_MAP
    )
    fig.show()
