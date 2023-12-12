




import os
from functools import cached_property

from dotenv import load_dotenv
from pandas import DataFrame
import plotly.express as px

from langchain.document_loaders import NotebookLoader
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter, PythonCodeTextSplitter, MarkdownTextSplitter #, MarkdownHeaderTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

from app.text_splitter import split_text_by_substrings

load_dotenv()

CHUNK_SIZE =  int(os.getenv("CHUNK_SIZE", default="1_000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", default="0")) # 40


TEXT_CELL_PREFIX = "'markdown' cell: "
CODE_CELL_PREFIX = "'code' cell: "

def parse_cell_type(page_content):

    # cell type (they are clearly marked at the beginning)
    if TEXT_CELL_PREFIX in page_content:
        cell_type = "TEXT"
    elif CODE_CELL_PREFIX in page_content:
        cell_type = "CODE"
    else:
        cell_type = None
    return cell_type



#class Cell(Document):
#
#    #def metadata(self):
#    #    meta = super().metadata
#    #    meta["cell_type"] = parse_cell_type(self.page_content)
#    #    return meta
#
#    def cell_type(self):
#        return parse_cell_type(self.page_content)


class DocumentProcessor:
    """Processes .IPYNB notebook documents."""

    def __init__(self, filepath, chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE, verbose=True):
        """Param : filepath to the notebook document"""

        self.filepath = filepath
        self.filename = self.filepath.split("/")[-1] # might not work on windows?

        self.chunk_overlap = chunk_overlap
        self.chunk_size = chunk_size

        self.embeddings_model_name = "text-embedding-ada-002"
        #self.faiss_index = self.filepath.upper().replace(".IPYNB", "") + "_FAISS_INDEX"

        self.verbose = bool(verbose)
        if self.verbose:
            print("---------------------")
            print("FILEPATH:", self.filepath)

    @cached_property
    def docs(self):
        loader = NotebookLoader(self.filepath, include_outputs=True, remove_newline=True)
        if self.verbose:
            print("LOADING...")

        docs = loader.load()
        if self.verbose:
            print("DOCS:", len(docs))
        assert len(docs) == 1 # right? let's see if this is never the case
        return docs


    @cached_property
    def doc(self):
        return self.docs[0]

    #@cached_property
    #def docs_df(self):
    #    # consider adding the page contents as well
    #    #return DataFrame([doc.metadata for doc in self.docs])
    #    records = []
    #    for doc in self.docs:
    #        metadata = doc.metadata
    #        metadata["page_content"] = doc.page_content
    #        records.append(metadata)
    #    return DataFrame(records)

    # SPLITTING:
    #@property
    #def splitter(self):
    #    return CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, separator="\n")
    #
    #@cached_property
    #def cell_chunks(self): # chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE
    #    return self.splitter.split_documents(documents=self.docs)

    # CELL SPLITTING (TEXT VS CODE):

    @cached_property
    def cells(self):
        cell_docs = []
        cell_texts = split_text_by_substrings(str(self.doc.page_content), TEXT_CELL_PREFIX, CODE_CELL_PREFIX)
        for i, cell_text in enumerate(cell_texts):
            cell_metadata = { #"filepath": self.filepath,
                "filename": self.filename,
                "cell_id": i+1,
                "cell_type": parse_cell_type(cell_text),
                "cell_length": len(cell_text)
            }
            #chunk.metadata = {**chunk.metadata, **cell_metadata} # dict merge
            doc = Document(page_content=cell_text, metadata=cell_metadata)
            cell_docs.append(doc)
        return cell_docs

    @cached_property
    def text_cells(self):
        return [cell for cell in self.cells if cell.metadata["cell_type"] == "TEXT"]

    @cached_property
    def code_cells(self):
        return [cell for cell in self.cells if cell.metadata["cell_type"] == "CODE"]

    @cached_property
    def cells_df(self):
        records = []
        for cell in self.cells:
            metadata = cell.metadata
            metadata["page_content"] = cell.page_content
            records.append(metadata)
        df = DataFrame(records)
        #df.index = df["cell_id"]
        return df





    # CHUNKS:

    @cached_property
    def chunks(self):
        """preserves metadata about absolute chunk order within notebook"""
        chunks = []

        #chunk_idx = 0
        for cell_i, cell in enumerate(self.cells):
            cell_type = cell.metadata["cell_type"]
            if cell_type == "TEXT":
                splitter = MarkdownTextSplitter(chunk_size=self.chunk_size)
                #splitter = MarkdownTextSplitter(chunk_size=self.text_chunk_size)
            elif cell_type == "CODE":
                splitter = PythonCodeTextSplitter(chunk_size=self.chunk_size)
                #splitter = PythonCodeTextSplitter(chunk_size=self.code_chunk_size)
            else:
                splitter = CharacterTextSplitter(chunk_size=self.chunk_size)

            cell_chunks = splitter.split_documents([cell])
            for cell_chunk_i, cell_chunk in enumerate(cell_chunks):
                cell_chunk.metadata["chunk_id"] = cell_chunk_i+1
                cell_chunk.metadata["chunk_length"] = len(cell_chunk.page_content)
                chunks.append(cell_chunk)
                #chunk_idx+=1

        return chunks

    @cached_property
    def text_chunks(self):
        return [chunk for chunk in self.chunks if chunk.metadata["cell_type"] == "TEXT"]

    @cached_property
    def code_chunks(self):
        return [chunk for chunk in self.chunks if chunk.metadata["cell_type"] == "CODE"]

    @cached_property
    def chunks_df(self):
        # consider adding the page contents as well
        #return DataFrame([chunk.metadata for chunk in self.chunks])
        records = []
        for chunk in self.chunks:
            metadata = chunk.metadata
            metadata["page_content"] = chunk.page_content
            records.append(metadata)
        return DataFrame(records)




    # EMBEDDINGS:

    @property
    def embeddings_model(self):
        model = OpenAIEmbeddings(model=self.embeddings_model_name)
        if self.verbose:
            print(model)
        return model

    @cached_property
    def retriever(self):
        db = FAISS.from_documents(self.chunks, self.embeddings_model)
        #faiss_index = self.filepath.upper().replace(".IPYNB", "") + "_FAISS_INDEX"
        #db.save_local(faiss_index)
        #db = FAISS.load_local(faiss_index, self.embeddings)
        retriever = db.as_retriever()
        if self.verbose:
            print("RETRIEVER:", type(retriever))
        return retriever

    def make_retriever(self, cell_type="TEXT", storage_strategy="chunks"):
        docs_map = {
            "TEXT": {
                "cells": self.text_cells,
                "chunks": self.text_chunks,
            },
            "CODE": {
                "cells": self.code_cells,
                "chunks": self.code_chunks,
            }
        }
        docs = docs_map[cell_type][storage_strategy]

        embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
        print(embeddings_model.model_name)

        db = FAISS.from_documents(docs, embeddings_model)
        retriever = db.as_retriever()
        print(cell_type, storage_strategy.upper(), "RETRIEVER:", type(retriever))
        return retriever

    @cached_property
    def code_retriever(self):
        return self.make_retriever(cell_type="CODE", storage_strategy=self.retrieval_strategy)

    @cached_property
    def text_retriever(self):
        return self.make_retriever(cell_type="TEXT", storage_strategy=self.retrieval_strategy)





def print_docs(docs, meta=False):
    for doc in docs:
        print("----")
        print(doc.page_content[0:50], "...", doc.page_content[-10:])
        if meta:
            print(doc.metadata)



if __name__ == "__main__":

    from app.submissions_manager import SubmissionsManager

    print("---------------")
    print("SUBMISSIONS...")
    sm = SubmissionsManager()
    print(sm.dirpath)
    print(len(sm.filenames))

    print("---------------")
    print("STARTER DOC...")
    starter_filepath = sm.find_filepath(substr="STARTER")
    dp =  DocumentProcessor(starter_filepath)
    #starter_doc = dp.doc
    print("DOC(S):", len(dp.docs))

    print("CELLS:", len(dp.cells))
    #print(dp.cells)
    print(dp.cells_df.shape)
    print(dp.cells_df.head())

    print(f"TEXT CELLS ({len(dp.text_cells)}):")
    print_docs(dp.text_cells)

    print(f"CODE CELLS ({len(dp.code_cells)}):")
    print_docs(dp.code_cells)


    breakpoint()

    print("----------")
    print("CHUNKS:", len(dp.chunks))
    print_docs(dp.chunks)



    #starter_dp.retriever

    # cp.plot_cell_lengths(title_extra="- Homework 4 Starter Notebook")
    # cp.docs_df.groupby("cell_type")["cell_length"].describe()
    # cp.plot_chunk_lengths(title_extra="- Homework 4 Starter Notebook")
    #starter_dp.chunks_df.drop(columns="source").to_csv("hw_4_cell_chunks.csv")
    #starter_dp.chunks_df.drop(columns="source").head()
