# adapted from youtube video about llama and langchain: ________________


import os
from dotenv import load_dotenv

from langchain import HuggingFacePipeline
from langchain import PromptTemplate,  LLMChain

from app.llama_prompts import get_prompt, parse_text
from app.llama_llm import LlamaService


if __name__ == "__main__":

    service = LlamaService()
    #pipeline = service.pipeline
    #llm = HuggingFacePipeline(pipeline=pipeline, model_kwargs={"temperature":TEMP})
    #print(llm)

    # SIMPLE LLM CHAIN

    #system_prompt = "You are an advanced assistant that excels at translation. "
    #instruction = "Convert the following text from English to French:\n\n {text}"
    #template = get_prompt(instruction, system_prompt)
    #print(template)
    #prompt = PromptTemplate(template=template, input_variables=["text"])
#
    #llm_chain = LLMChain(prompt=prompt, llm=llm)
#
    #query = "how are you today?"
    #response = llm_chain.run(query)
    #parse_text(response)


    # CHAT CHAIN

    if input("Continue to chat (Y/N): ").upper() != "Y":
        exit()


    from langchain.memory import ConversationBufferMemory
    from langchain import LLMChain, PromptTemplate

    prompt = PromptTemplate(template=template, input_variables=["chat_history", "user_input"])
    memory = ConversationBufferMemory(memory_key="chat_history")



    # for chat, with memory
    instruction = "Chat History:\n\n{chat_history} \n\nUser: {user_input}"
    system_prompt = "You are a helpful assistant, you always only answer for the assistant then you stop. read the chat history to get context"

    template = get_prompt(instruction, system_prompt)
    print(template)

    llm_chain = LLMChain(prompt=prompt, llm=llm,
        verbose=True, memory=memory,
    )

    query = ""
    while query != "":
        query = input("Please ask a question: ")
        print(query)

        response = llm_chain.predict(user_input=query)
        print(response)
