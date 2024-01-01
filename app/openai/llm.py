
import os

import openai
from langchain.llms import OpenAI
from dotenv import load_dotenv

#from app import seek_confirmation


load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", default="text-davinci-003")
TEMP = float(os.getenv("TEMP", default="0.0")) # @param {type:"slider", min:0, max:1, step:0.1}


def create_llm(model_name=MODEL_NAME, temp=TEMP):
    # default model is text-davinci-003
    # default temp is 0.7
    return OpenAI(model_name=MODEL_NAME, temperature=TEMP)


if __name__ == "__main__":

    from random import choice

    llm = create_llm()
    print(llm)
    #print(llm.model_name)
    #print(llm.temperature)

    #seek_confirmation("Continue to prompt? (Y/N): ")

    general_knowlege_queries = [
        "What year was America founded?",
        "Tell us about the first humans who landed on the moon"
    ]

    query = input("Please provide a Query (enter for default, 'Q' to quit): ")
    if query.upper() == "Q":
        exit()

    query = query or choice(general_knowlege_queries)
    print(query)
    response = llm.predict(query).strip()
    print(response)
