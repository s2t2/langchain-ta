from warnings import filterwarnings
filterwarnings("ignore")

from app import DATA_DIRPATH
from app.submissions_manager import SubmissionsManager
from app.document_processor import DocumentProcessor #, print_docs

from pandas import pivot_table

def print_docs(docs, meta=False):
    for doc in docs:
        #print("----")
        print(doc.page_content[0:50], "...", doc.page_content[-25:])
        if meta:
            print(doc.metadata)

def print_relevant_cells(cells):
    total_length = 0
    for doc in cells:
        print("\n")
        print("CELL:", doc.metadata["cell_id"], "CHUNK:", doc.metadata["chunk_id"])
        print("LENGTH:", len(doc.page_content))
        print("CONTENT:", doc.page_content)

        total_length += len(doc.page_content)

    print("\n")
    print("TOTAL LENGTH:", total_length)
    #return total_length


if __name__ == "__main__":

    print("---------------")
    print("SUBMISSIONS...")
    sm = SubmissionsManager()
    print(sm.dirpath)
    print(len(sm.filenames))
    starter_filepath = sm.find_filepath(substr="STARTER")

    print("---------------")
    print("STARTER DOC...")
    dp =  DocumentProcessor(starter_filepath)

    print("CELLS:", len(dp.cells))
    print("AVG LENGTHS:", dp.cells_df.groupby("cell_type")["cell_length"].mean())
    #print(dp.cells_df.groupby("cell_type")["cell_length"].describe())
    #pivot_table(dp.cells_df, index="cell_type", columns=["..."])

    print("---------------")
    print(f"TEXT CELLS ({len(dp.text_cells)}):")
    print_docs(dp.text_cells)
    print("---------------")
    print(f"CODE CELLS ({len(dp.code_cells)}):")
    print_docs(dp.code_cells)
    dp.plot_cell_lengths()

    print("----------")
    print("CHUNKS:", len(dp.chunks))
    print("AVG LENGTHS:", dp.chunks_df.groupby("cell_type")["chunk_length"].mean())
    #print_docs(dp.chunks)
    dp.plot_chunk_lengths()

    keep_going = input("CONTINUE TO QUERYING AND RETRIEVAL? ('Y'/'N'): ").upper() or "N"
    if keep_going != "Y":
        exit()

    STUDENT_QUERY = "What is the student's name? What is their GW ID?"
    print("QUERY:", STUDENT_QUERY)

    relevant_docs = dp.text_retriever.get_relevant_documents(STUDENT_QUERY)
    print("-----------")
    print(f"RELEVANT DOCS ({len(relevant_docs)}):")
    print_relevant_cells(relevant_docs)

    compressed_docs = dp.text_compression_retriever.get_relevant_documents(STUDENT_QUERY)
    print("-----------")
    print(f"COMPRESSED DOCS: ({len(compressed_docs)}):")
    print_relevant_cells(compressed_docs)

    #breakpoint()
