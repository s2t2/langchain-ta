




def print_docs(docs, meta=False):
    for doc in docs:
        #print("----")
        print(doc.page_content[0:50], "...", doc.page_content[-25:])
        if meta:
            print(doc.metadata)



def print_rows(rows):
    for _, row in rows.iterrows():
        #print("----")
        print(row["page_content"][0:50], "...", row["page_content"][-25:])




from pandas import DataFrame

def documents_to_df(docs):
    """Converts list of Docs to a DataFrame. Includes columns for doc metadata and page content."""
    records = []
    for doc in docs:
        metadata = doc.metadata
        metadata["page_content"] = doc.page_content
        records.append(metadata)
    df = DataFrame(records)
    return df
