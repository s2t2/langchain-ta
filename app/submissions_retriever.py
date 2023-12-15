
import os
from functools import cached_property

from dotenv import load_dotenv
from pandas import DataFrame

from app import RESULTS_DIRPATH
from app.submissions_processor import SubmissionsProcessor
from app.document_processor import CHUNK_OVERLAP, CHUNK_SIZE, SIMILARITY_THRESHOLD
from app.rows_processor import RowsDocumentProcessor
from app.prompts import STUDENT_QUERY
from app.prompts.homework_4 import HOMEWORK_QUESTIONS


load_dotenv()

UNIQUE_ONLY = bool(os.getenv("UNIQUE_ONLY", default="true").lower() == "true")
DOCS_LIMIT = os.getenv("DOCS_LIMIT")


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


class SubmissionsRetriever:

    def __init__(self, unique_only=UNIQUE_ONLY, similarity_threshold=SIMILARITY_THRESHOLD, docs_limit=DOCS_LIMIT,
                 #retrieval_strategy="chunks",
                 chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
                 homework_questions=HOMEWORK_QUESTIONS,
                 ):

        self.unique_only = unique_only
        self.similarity_threshold = float(similarity_threshold)
        self.retrieval_strategy = "chunks"
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP

        self.homework_questions = homework_questions

        self.docs_limit = DOCS_LIMIT
        if self.docs_limit:
            self.docs_limit = int(self.docs_limit)

        self.queries_csv_filepath = os.path.join(RESULTS_DIRPATH, f"queries_similarity_{self.similarity_threshold}_chunks_{self.chunk_size}_{self.chunk_overlap}.csv")
        self.queries_df = None # DataFrame()


    def perform(self):
        sp = SubmissionsProcessor()
        sp.perform()

        cells_df = sp.cells_df.copy()
        print("ALL CELLS:", len(cells_df))
        if self.unique_only:
            cells_df = cells_df[ cells_df["dup_content"] == False ]
            print("UNIQUE CELLS:", len(cells_df))

        submission_filenames = cells_df["filename"].unique()
        print("SUBMISSIONS:", len(submission_filenames))

        records = []
        submission_filenames = submission_filenames[0:self.docs_limit] if self.docs_limit else submission_filenames
        for filename in submission_filenames:
            print("---------------------")
            print(filename)
            rows_df = cells_df[ cells_df["filename"] == filename ]
            dp = RowsDocumentProcessor(rows_df=rows_df, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap) # similarity_threshold=similarity_threshold
            #text_retriever = dp.text_compression_retriever
            base_retriever = dp.make_retriever(cell_type="TEXT", storage_strategy=self.retrieval_strategy)
            compression_retriever = dp.make_compression_retriever(base_retriever=base_retriever, similarity_threshold=self.similarity_threshold)

            records += get_relevant_records(retriever=compression_retriever, query=STUDENT_QUERY, query_id="STUDENT INFO", filename=filename, file_id=dp.file_id)
            # todo: designate which query gets which response model, so we can treat the student query the same as the homework queries
            for query_id, query in self.homework_questions:
                records += get_relevant_records(compression_retriever, query=query, query_id=query_id, filename=filename, file_id=dp.file_id)

        self.queries_df = DataFrame(records)
        #queries_df["cell_id"] = queries_df["cell_id"].astype(int)
        #queries_df["chunk_id"] = queries_df["chunk_id"].astype(int) # these were showing up as floats, because there are NaNs?
        self.queries_df.to_csv(self.queries_csv_filepath, index=False)




if __name__ == "__main__":



    sr = SubmissionsRetriever()
    sr.perform()
