




import os
from functools import cached_property

from dotenv import load_dotenv
from pandas import DataFrame
import plotly.express as px

from langchain.document_loaders import NotebookLoader
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter #, PythonCodeTextSplitter, MarkdownTextSplitter #, MarkdownHeaderTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS


load_dotenv()

CHUNK_SIZE =  int(os.getenv("CHUNK_SIZE", default="1_000"))

CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", default="0")) # 40




class DocumentProcessor:
    """Processes .IPYNB notebook documents."""

    def __init__(self, filepath, chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE, verbose=True):
        """Param : filepath to the notebook document"""

        self.filepath = filepath
        self.filename = self.filepath.split("/")[-1] # might not work on windows?

        self.chunk_overlap = chunk_overlap
        self.chunk_size = chunk_size

        #self.faiss_index = self.filepath.upper().replace(".IPYNB", "") + "_FAISS_INDEX"

        self.verbose = bool(verbose)
        if self.verbose:
            print("---------------------")
            print("FILEPATH:", self.filepath)

    @cached_property
    def docs(self):
        loader = NotebookLoader(self.filepath, include_outputs=True, remove_newline=True)

        print("LOADING...")

        docs = loader.load()
        print("DOCS:", len(docs))

        return docs # loader.load()

    @cached_property
    def chunks(self): # chunk_overlap=CHUNK_OVERLAP, chunk_size=CHUNK_SIZE
        splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, separator="\n")
        chunks = splitter.split_documents(documents=self.docs)
        print("CHUNKS:", len(chunks))
        #print(type(chunks))
        #print(type(chunks[0]))
        return chunks

    @cached_property
    def retriever(self):
        faiss_index = self.filepath.upper().replace(".IPYNB", "") + "_FAISS_INDEX"

        print("EMBEDDINGS...")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        print(type(self.embeddings))

        vectorstore = FAISS.from_documents(self.chunks, self.embeddings)
        vectorstore.save_local(faiss_index)

        persisted_vectorstore = FAISS.load_local(faiss_index, self.embeddings)
        retriever = persisted_vectorstore.as_retriever()
        print("RETRIEVER:", type(retriever))
        return retriever





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
    starter_dp =  DocumentProcessor(starter_filepath)
    #starter_doc = starter_dp.doc
    print("DOC(S):", len(starter_dp.docs))

    print("CHUNKS:", len(starter_dp.chunks))
    for chunk in starter_dp.chunks:
        print("----")
        #print(chunk.metadata) #> {'source': "/path/to/file"}
        print(chunk.page_content[0:50])



    # cp.plot_cell_lengths(title_extra="- Homework 4 Starter Notebook")
    # cp.docs_df.groupby("cell_type")["cell_length"].describe()
    # cp.plot_chunk_lengths(title_extra="- Homework 4 Starter Notebook")
    #starter_dp.chunks_df.drop(columns="source").to_csv("hw_4_cell_chunks.csv")
    #starter_dp.chunks_df.drop(columns="source").head()
