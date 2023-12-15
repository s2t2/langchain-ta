
import os
from functools import cached_property

from langchain.document_loaders import DataFrameLoader
from dotenv import load_dotenv

from app import RESULTS_DIRPATH
from app.cell import Cell
from app.submissions_processor import SubmissionsProcessor
from app.document_processor import DocumentProcessor, CHUNK_OVERLAP, CHUNK_SIZE, SIMILARITY_THRESHOLD


load_dotenv()


class RowsDocumentProcessor(DocumentProcessor):
    """Processes a collection of row documents."""

    #def __init__(self, rows_df, filepath, chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE, verbose=True, similarity_threshold=SIMILARITY_THRESHOLD, file_id=None):
    #    super().__init__(filepath=filepath, chunk_overlap=chunk_overlap, chunk_size=chunk_size, verbose=verbose, similarity_threshold=similarity_threshold, file_id=file_id)
    #    self.rows_df = rows_df.copy()
    #    print("ROWS:", len(self.rows_df))

    def __init__(self, rows_df, chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE, verbose=True, similarity_threshold=SIMILARITY_THRESHOLD):

        self.rows_df = rows_df.copy()
        self.filename = rows_df["filename"].unique()[0] # take the first, they should all be the same
        self.file_id = rows_df["file_id"].unique()[0] # take the first, they should all be the same

        self.chunk_overlap = int(chunk_overlap)
        self.chunk_size = int(chunk_size)

        self.embeddings_model_name = "text-embedding-ada-002"
        #self.faiss_index = self.filepath.upper().replace(".IPYNB", "") + "_FAISS_INDEX"
        self.similarity_threshold = float(similarity_threshold)

        self.verbose = bool(verbose)
        if self.verbose:
            print("---------------------")
            print("FILENAME:", self.filename)
            print("ROWS:", len(self.rows_df))


    # OVERWRITE PARENT METHODS WE DON'T NEED

    @cached_property
    def docs(self):
        return []

    @cached_property
    def doc(self):
        return None

    # OVERWRITE PARENT METHOD TO GET CELLS STRAIGHT FROM THE ROWS DATAFRAME:

    @cached_property
    def cells(self):
        loader = DataFrameLoader(self.rows_df, page_content_column="page_content")
        docs = loader.load()
        # wrap docs in cell class, to stay consistent with parent method
        docs = [Cell(page_content=doc.page_content, metadata=doc.metadata) for doc in docs]
        return docs # cell_docs


def get_relevant_records(retriever, query, query_id, filename=None, file_id=None, verbose=True):
    records = []
    relevant_docs_with_state = retriever.get_relevant_documents(query)
    #relevant_docs_with_state[0] #> _DocumentWithState has page_content and state["embedded_doc"]
    #relevant_docs = [dws.to_document() for dws in relevant_docs_with_state]
    if verbose:
        print(query)
        print(len(relevant_docs_with_state))

    if any(relevant_docs_with_state):
        for dws in relevant_docs_with_state:
            doc = dws.to_document()
            #print(doc)
            record = {
                "filename": doc.metadata["filename"],
                "file_id": doc.metadata["file_id"],
                "query_id": query_id,
                #"query": query,
                "similarity": dws.state["query_similarity_score"],
                "cell_id": doc.metadata["cell_id"],
                "chunk_id": doc.metadata.get("chunk_id"),
                "page_content": doc.page_content
            }
            #record = {**doc.metadata, **record} # dict merge
            records.append(record)
    else:
        record = {
            "filename": filename,
            "file_id": file_id,
            "query_id": query_id,
            #"query": query,
            "similarity": None,
            "cell_id": None,
            "chunk_id": None,
            "page_content": None
        }
        records.append(record)

    return records


if __name__ == "__main__":
    #import pandas as pd
    #pd.set_option('display.max_colwidth', 0)

    from pandas import DataFrame

    from app.prompts import STUDENT_QUERY
    from app.prompts.homework_4 import HOMEWORK_QUESTIONS

    UNIQUE_ONLY = bool(os.getenv("UNIQUE_ONLY", default="true").lower() == "true")
    DOCS_LIMIT = os.getenv("DOCS_LIMIT")

    # TODO: convert into a class

    unique_only = UNIQUE_ONLY
    similarity_threshold = SIMILARITY_THRESHOLD
    retrieval_strategy = "chunks"
    chunk_size = CHUNK_SIZE
    chunk_overlap = CHUNK_OVERLAP
    docs_limit = DOCS_LIMIT
    if docs_limit:
        docs_limit = int(docs_limit)
    queries_csv_filepath = os.path.join(RESULTS_DIRPATH, f"queries_similarity_{similarity_threshold}_chunks_{chunk_size}_{chunk_overlap}.csv")

    sp = SubmissionsProcessor()
    sp.perform()

    cells_df = sp.cells_df.copy()
    print("ALL CELLS:", len(cells_df))
    if unique_only:
        cells_df = cells_df[ cells_df["dup_content"] == False ]
        print("UNIQUE CELLS:", len(cells_df))

    submission_filenames = cells_df["filename"].unique()
    print("SUBMISSIONS:", len(submission_filenames))

    records = []
    submission_filenames = submission_filenames[0:docs_limit] if docs_limit else submission_filenames
    for filename in submission_filenames:
        print("---------------------")
        print(filename)

        rows_df = cells_df[ cells_df["filename"] == filename ]
        dp = RowsDocumentProcessor(rows_df=rows_df, chunk_size=chunk_size, chunk_overlap=chunk_overlap) # similarity_threshold=similarity_threshold
        #text_retriever = dp.text_compression_retriever
        base_retriever = dp.make_retriever(cell_type="TEXT", storage_strategy=retrieval_strategy)
        compression_retriever = dp.make_compression_retriever(base_retriever=base_retriever, similarity_threshold=similarity_threshold)

        records += get_relevant_records(retriever=compression_retriever, query=STUDENT_QUERY, query_id="STUDENT INFO", filename=filename, file_id=dp.file_id)

        for query_id, query in HOMEWORK_QUESTIONS:
            records += get_relevant_records(compression_retriever, query=query, query_id=query_id, filename=filename, file_id=dp.file_id)

    queries_df = DataFrame(records)
    #queries_df["cell_id"] = queries_df["cell_id"].astype(int)
    #queries_df["chunk_id"] = queries_df["chunk_id"].astype(int) # these were showing up as floats, because there are NaNs?
    queries_df.to_csv(queries_csv_filepath, index=False)
