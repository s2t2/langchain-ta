from warnings import filterwarnings
filterwarnings("ignore")

import os
from pandas import DataFrame, merge
import plotly.express as px

from app import RESULTS_DIRPATH
from app.colors import CELL_COLORS_MAP
from app.submissions_manager import SubmissionsManager, SUBMISSIONS_DIRPATH
from app.document_processor import DocumentProcessor, FIG_SHOW
#from app.document_formatting import print_docs, print_rows


class SubmissionsProcessor:

    def __init__(self, dirpath=SUBMISSIONS_DIRPATH, starter_filename=None, results_dirpath=RESULTS_DIRPATH):
        """Can use a starter file, or not."""

        self.submissions_dirpath = dirpath
        self.starter_filename = starter_filename

        self.results_dirpath = results_dirpath or self.submissions_dirpath
        self.notebooks_csv_filepath = os.path.join(self.results_dirpath, "notebooks.csv")
        self.cells_csv_filepath = os.path.join(self.results_dirpath, "cells.csv")

        # get all submision files (consider passing them in for a looser coupling with the manager class):
        self.sm = SubmissionsManager(self.submissions_dirpath, starter_filename=self.starter_filename)
        print("SUBMISSIONS DIR:", self.sm.dirpath)
        print("FILES:", len(self.sm.filenames))
        self.submission_filepaths = self.sm.filepaths

        # available post processing:
        self.starter_dp = None
        self.notebooks_df = None
        self.cells_df = None


    def perform(self):
        """Processes all submission documents. Compares them relative to eachother and the starter document.
            Produces a CSV file of document statistics, as well as a CSV file of cell contents and metadata.
        """

        all_cells = []
        records = []
        for filepath in self.submission_filepaths:
            dp = DocumentProcessor(filepath, verbose=False)
            avg_lengths = dp.cells_df.groupby("cell_type")["cell_length"].mean()
            record = {
                "filename": dp.filename,
                "file_id": dp.file_id,
                "length": len(dp.doc.page_content), #dp.docs_df["cell_length"].sum(),
                "cells": len(dp.cells),
                "code_cells": len(dp.code_cells),
                "text_cells": len(dp.text_cells),
                "avg_code_cell_length": avg_lengths["CODE"].round(1),
                "avg_text_cell_length": avg_lengths["TEXT"].round(1),
            }
            records.append(record)
            all_cells += dp.cells

        print("------")
        print("NOTEBOOKS:", len(records))
        self.notebooks_df = DataFrame(records)
        #notebooks_df.index = notebooks_df["filename"]
        #notebooks_df["file_id"] = notebooks_df["filename"].apply(lambda filename: filename.split("_")[1]) # todo: regex instead, to be more precise

        self.notebooks_df.to_csv(self.notebooks_csv_filepath, index=False)

        print("------")
        print("CELLS:", len(all_cells))
        self.cells_df = DataFrame([cell.metadata for cell in all_cells])

        print("------")
        print("DUPLICATE CELLS:")
        self.cells_df['dup_content'] = self.cells_df.duplicated(subset='page_content', keep=False)
        print(self.cells_df["dup_content"].value_counts())

        print("------")
        print("STARTER CELLS:") # (~30% of cells are the same as starter cells)
        #starter_rows = cells_df[ cells_df["filename"].str.contains("STARTER") ]
        if self.starter_filename:
            starter_rows = self.cells_df[ self.cells_df["filename"] == self.starter_filename ]
            self.cells_df = merge(self.cells_df, starter_rows[["cell_id", "page_content"]], how='left', on='page_content', suffixes=('', '_starter'))
            self.cells_df.rename(columns={"cell_id_starter": "starter_cell_id"}, inplace=True)
            #self.cells_df["starter_content"] = self.cells_df['starter_cell_id'].notna()
            #print(self.cells_df["starter_content"].value_counts())
        else:
            self.cells_df["starter_cell_id"] = None
            #self.cells_df["starter_content"] = False
        self.cells_df["starter_content"] = self.cells_df['starter_cell_id'].notna()
        print(self.cells_df["starter_content"].value_counts())

        print("------")
        print("EMPTY CELLS:")
        print(self.cells_df["is_empty"].value_counts())

        #print("------")
        #print("NON-DUPLICATE NON-STARTER NON-BLANK CELLS:")
        #dup_rows = self.cells_df[ (self.cells_df["starter_content"] == False) & (self.cells_df["dup_content"] == True) & (self.cells_df["is_empty"] == False)].sort_values(by="page_content")
        #print_rows(dup_rows)

        self.cells_df.to_csv(self.cells_csv_filepath, index=False)


    def plot_documents(self, fig_show=FIG_SHOW):

        print("------")
        print("PLOTTING...")

        # PLOTTING: ORIGINAL DOCUMENTS

        chart_df = self.notebooks_df.copy()
        #chart_df["filename"] = chart_df.index
        avg_length = chart_df.groupby('filename')['length'].mean().mean()
        title = "Document Lengths (All Content)"
        title += f"<br><sup>Documents: {len(chart_df):,.0f} | Avg Length: {avg_length:,.0f} chars</sup>"
        fig = px.violin(chart_df, x="length", box=True, points="all", height=400, title=title,
                hover_data=["file_id", "filename"] # "file_id",
        )
        if fig_show:
            fig.show()

        # PLOTTING: DOCUMENTS (UNIQUE CONTENT ONLY)

        chart_df = self.cells_df.copy()
        chart_df = chart_df[chart_df["dup_content"] == False]
        chart_df = chart_df[chart_df["starter_content"] == False]
        chart_df = chart_df[chart_df["is_empty"] == False]
        #chart_pivot = chart_df.groupby("filename")["cell_length"].sum()
        #chart_pivot = chart_pivot.to_frame().rename(columns={"cell_length": "length"})
        #chart_pivot["filename"] = chart_pivot.index
        chart_pivot = chart_df.groupby(["file_id", "filename"])["cell_length"].sum()
        chart_pivot = chart_pivot.to_frame().rename(columns={"cell_length": "length"})
        chart_pivot.reset_index(inplace=True) # convert multi-index to columns, https://stackoverflow.com/a/25733562/670433
        avg_length = chart_pivot['length'].mean()
        title = "Document Lengths (Unique Content Only)"
        title += f"<br><sup>Documents: {len(chart_pivot):,.0f} | Avg Length: {avg_length:,.0f} chars</sup>"
        fig = px.violin(chart_pivot, x="length", box=True, points="all", height=400, title=title,
                hover_data=["file_id", "filename"]
        )
        if fig_show:
            fig.show()


    def plot_cells(self, fig_show=FIG_SHOW):

        # PLOTTING: CELLS (ALL)

        chart_df = self.cells_df.copy()
        chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
        avg_length = chart_df["cell_length"].mean()
        title = "Cell Lengths (All Content)"
        title += f"<br><sup>Cells: {len(chart_df):,.0f} | Avg Length: {avg_length:,.0f} chars</sup>"
        fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500, title=title,
                hover_data=["page_content"], facet_row="cell_type",
                color="cell_type", color_discrete_map=CELL_COLORS_MAP
        )
        if fig_show:
            fig.show()

        # PLOTTING: CELLS (UNIQUE)

        chart_df = self.cells_df.copy()
        chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
        chart_df = chart_df[chart_df["dup_content"] == False]
        chart_df = chart_df[chart_df["starter_content"] == False]
        chart_df = chart_df[chart_df["is_empty"] == False]
        avg_length = chart_df["cell_length"].mean()
        title = "Cell Lengths (Unique Content Only)"
        title += f"<br><sup>Cells: {len(chart_df):,.0f} | Avg Length: {avg_length:,.0f} chars</sup>"
        fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500, title=title,
                hover_data=["page_content"], facet_row="cell_type",
                color="cell_type", color_discrete_map=CELL_COLORS_MAP
        )
        if fig_show:
            fig.show()


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


        # cells_df[cells_df["page_content"].str.contains("  with output: ") ]

        # NON-STARTER CELLS:

        #chart_df = cells_df.copy()
        #chart_df = chart_df[chart_df["cell_length"] <= 10_000] # filter out two outliers 25K, 30K
        #chart_df = chart_df[chart_df["starter_content"] == False]
        #fig = px.violin(chart_df, x="cell_length", box=True, points="all", height=500,
        #        title="Non-Starter Cell Lengths (All Submissions)",
        #        hover_data=["page_content"], facet_row="cell_type",
        #        color="cell_type", color_discrete_map=CELL_COLORS_MAP
        #)
        #fig.show()







if __name__ == "__main__":

    sp = SubmissionsProcessor()

    sp.perform()
    sp.plot_documents()
    sp.plot_cells()
