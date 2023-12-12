
from app.submissions_manager import SubmissionsManager
from app.document_processor import DocumentProcessor, print_docs


if __name__ == "__main__":

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
    print(dp.cells_df.groupby("cell_type")["cell_length"].describe())

    print("---------------")
    print(f"TEXT CELLS ({len(dp.text_cells)}):")
    print_docs(dp.text_cells)

    print("---------------")
    print(f"CODE CELLS ({len(dp.code_cells)}):")
    print_docs(dp.code_cells)

    dp.plot_cell_lengths()

    print("----------")
    print("CHUNKS:", len(dp.chunks))
    print(dp.chunks_df.head())

    dp.plot_chunk_lengths()
    #starter_dp.chunks_df.drop(columns="source").to_csv("hw_4_cell_chunks.csv")
    #starter_dp.chunks_df.drop(columns="source").head()

    #starter_dp.retriever
