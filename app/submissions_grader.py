
import os
from functools import cached_property
from pprint import pprint

from pandas import DataFrame
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain

from app import RESULTS_DIRPATH
from app.submissions_processor import SubmissionsProcessor
from app.document_processor import CHUNK_OVERLAP, CHUNK_SIZE, SIMILARITY_THRESHOLD
from app.rows_processor import RowsDocumentProcessor
from app.prompts import STUDENT_QUERY
from app.prompts.homework_4 import HOMEWORK_QUESTIONS
from app.submissions_retriever import SubmissionsRetriever, UNIQUE_ONLY, DOCS_LIMIT
from app.openai_llm import create_llm, MODEL_NAME, TEMP
from app.response_formatters import Student, QuestionScoring


def get_relevant_docs(retriever, query, verbose=True):
    relevant_docs_with_state = retriever.get_relevant_documents(query)
    #relevant_docs_with_state[0] #> _DocumentWithState has page_content and state["embedded_doc"]
    if verbose:
        print(query)
        print(len(relevant_docs_with_state))

    relevant_docs = [dws.to_document() for dws in relevant_docs_with_state]
    return relevant_docs



SYSTEM_INSTRUCTIONS = """You are an experienced machine learning practitioner and instructor. Your goal is to grade a student's machine learning homework assignment. Provide a score (and corresponding comments) to indicate how completely and accurately the student addressed the following question:"""

QA_CONTEXT_TEMPLATE = """Answer the **query**, based on the provided **context**, and format your response according to the **formatting instructions** (avoid using special characters).

**Context**: {context}

**Query**: {query}

**Formatting Instructions**: {formatting_instructions}
"""

#QA_CONTEXT_TEMPLATE = """Answer the **query**, based on the provided **context**.
#
#**Context**: {context}
#
#**Query**: {query}
#"""


def qa_chain(llm, query, compression_retriever, parser_class, verbose=False):
    # https://www.youtube.com/watch?v=yriZBFKE9JU

    prompt = ChatPromptTemplate.from_template(QA_CONTEXT_TEMPLATE)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

    relevant_docs = get_relevant_docs(retriever=compression_retriever, query=query)

    parser = PydanticOutputParser(pydantic_object=parser_class)
    formatting_instructions = parser.get_format_instructions()

    response = chain.invoke({"query": query, "context": relevant_docs, "formatting_instructions": formatting_instructions})
    parsed_response = parser.invoke(response["text"])
    return parsed_response


class SubmissionsGrader(SubmissionsRetriever):

    def __init__(self, unique_only=UNIQUE_ONLY, similarity_threshold=SIMILARITY_THRESHOLD, docs_limit=DOCS_LIMIT,
                 #retrieval_strategy="chunks",
                 chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
                 homework_questions=HOMEWORK_QUESTIONS,
                 results_dirpath=RESULTS_DIRPATH,

                 model_name=MODEL_NAME, temp=TEMP
                 ):

        super().__init__(unique_only=unique_only, similarity_threshold=similarity_threshold, docs_limit=docs_limit,
                 #retrieval_strategy="chunks",
                 chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                 homework_questions=homework_questions, results_dirpath=results_dirpath
                )

        # ADDITIONS:
        self.temp = temp
        self.model_name = model_name
        self.llm = create_llm(model_name=self.model_name, temp=self.temp)

        self.scorings_csv_filepath = os.path.join(self.results_dirpath, f"scoring_errors_similarity_{self.similarity_threshold}_chunks_{self.chunk_size}_{self.chunk_overlap}_temp_{self.temp}.csv")
        self.scorings_df = DataFrame()
        #self.errors_csv_filepath = os.path.join(self.results_dirpath, f"scoring_errors_similarity_{self.similarity_threshold}_chunks_{self.chunk_size}_{self.chunk_overlap}_temp_{self.temp}.csv")
        #self.errors_df = DataFrame()


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
        errors = []
        submission_filenames = submission_filenames[0:self.docs_limit] if self.docs_limit else submission_filenames
        for filename in submission_filenames:
            print("---------------------")
            print(filename)
            rows_df = cells_df[ cells_df["filename"] == filename ]
            dp = RowsDocumentProcessor(rows_df=rows_df, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap) # similarity_threshold=similarity_threshold
            #text_retriever = dp.text_compression_retriever
            base_retriever = dp.make_retriever(cell_type="TEXT", storage_strategy=self.retrieval_strategy)
            compression_retriever = dp.make_compression_retriever(base_retriever=base_retriever, similarity_threshold=self.similarity_threshold)

            record = {"filename": filename, "file_id": dp.file_id} # flattened structure, one row per submission document
            try:
                student = qa_chain(llm=self.llm, query=STUDENT_QUERY, compression_retriever=compression_retriever, parser_class=Student)
                record = {**record, **{"student_id": student.net_id, "student_name": student.name}}

                i = 1
                for query_id, query in self.homework_questions:
                    scoring = qa_chain(llm=self.llm, query=query, compression_retriever=compression_retriever, parser_class=QuestionScoring)
                    record[f"scoring_{i}_question_id"] = scoring.question_id
                    record[f"scoring_{i}_score"] = scoring.score
                    record[f"scoring_{i}_comments"] = scoring.comments
                    record[f"scoring_{i}_confidence"] = scoring.confidence
                    i+=1

                record["error"] = None
                records.append(record)
            except Exception as err:
                print("ERROR...")
                errors.append({"filename": filename, "error": err})
                records.append({"filename": filename, "error": err})

            print("-----------------")
            print("RECORDS:")
            print(len(records))
            print("-----------------")
            print("ERRORS:")
            pprint(errors)

        self.scorings_df = DataFrame(records)
        self.scorings_df.to_csv(self.scorings_csv_filepath, index=False)

        #self.errors_df = DataFrame(errors)
        #self.errors_df.to_csv(self.errors_csv_filepath, index=False)





if __name__ == "__main__":



    grader = SubmissionsGrader()
    grader.perform()

    print(grader.scorings_df.head())
