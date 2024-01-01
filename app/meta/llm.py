
# adapted from youtube video about llama and langchain: ________________

import os
from dotenv import load_dotenv

import torch
#import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.prompts import PromptTemplate
from langchain.chains import  LLMChain
from langchain.llms.huggingface_pipeline import HuggingFacePipeline

from app.meta.prompts import get_prompt, parse_text, cut_off_text, remove_substring

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf" # os.getenv("MODEL_NAME", default="meta-llama/Llama-2-7b-chat-hf")

#MAX_NEW_TOKENS = 512
TEMP = float(os.getenv("TEMP", default="0.0")) # @param {type:"slider", min:0, max:1, step:0.1}

# THIS IS THE OFFICIAL SYSTEM PROMPT?
INST, INST_END = "[INST]", "[/INST]"
SYS, SYS_END = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
"""

def compile_prompt(prompt, system_prompt=DEFAULT_SYSTEM_PROMPT, input_variables=[]) -> PromptTemplate:
    """Wraps your query in syntax the model understands. Uses default system instructions, or ones you provide.

        Params:
            prompt (str) : your prompt string, optionally with placeholder {} for input vars

            input variables: a list of string input variable names in your prompt, default is None

        Returns: langchain.PromptTemplate
    """
    formatted_prompt = f"{INST} {SYS} {system_prompt} {SYS_END} {prompt} {INST_END}"
    return PromptTemplate(template=formatted_prompt, input_variables=input_variables)


class HuggingFaceService:
    def __init__(self, model_name=MODEL_NAME, temp=TEMP, token=HUGGINGFACE_TOKEN): # device_type="cpu",
        self.model_name = model_name
        self.token = token # hugging face api token
        self.temp = temp

        #self.device_type = device_type # "cpu" for local dev, or "cuda" for colab gpu

    @property
    def tokenizer(self):
        # https://huggingface.co/transformers/v2.11.0/model_doc/auto.html?highlight=autotokenizer#autotokenizer
        return AutoTokenizer.from_pretrained(self.model_name, token=self.token) # cache_dir=CACHE_DIRPATH

    @property
    def model(self):
        # https://huggingface.co/docs/transformers/model_doc/auto#transformers.AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained(self.model_name, token=self.token,
                                                    device_map="auto",
                                                    #torch_dtype=torch.float16, # GPU ONLY?  https://stackoverflow.com/a/73530618/670433
                                                    torch_dtype=torch.float32 # CPU
        )

    @property
    def pipeline(self):
        """wrapper for tokenizer and model, for performing the 'text-generation' task"""
        # https://huggingface.co/docs/transformers/main_classes/pipelines
        return pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer,
                        device_map="auto",
                        max_new_tokens=512, do_sample=True, top_k=30, num_return_sequences=1,
                        eos_token_id=self.tokenizer.eos_token_id,
                        #torch_dtype=torch.bfloat16, # GPU ONLY? https://stackoverflow.com/a/73530618/670433
                        torch_dtype=torch.float32, # CPU
        )

    @property
    def llm(self):
        return HuggingFacePipeline(pipeline=self.pipeline, model_kwargs={"temperature":self.temp})


    #def predict(self, query):


    #def formatted_response(self, prompt, system_prompt=DEFAULT_SYSTEM_PROMPT, input_variables=None):
    #    prompt = self.compile_prompt(prompt)
    #
    #    llm_chain = LLMChain(prompt=prompt, llm=llm)
    #    response = llm_chain.run(query)
    #    parse_text(response)

    #def generate(self, text):
    #    prompt = get_prompt(text)
    #
    #    with torch.autocast(self.device_type, dtype=torch.bfloat16):
    #        #inputs = self.tokenizer(prompt, return_tensors="pt").to('cuda') # on CPU as well?
    #        inputs = self.tokenizer(prompt, return_tensors="pt") #
    #        breakpoint()
    #        #if self.device_type == "cuda":
    #        #    inputs = inputs.to("cuda")
    #
    #        outputs = self.model.generate(**inputs,
    #                                max_new_tokens=512,
    #                                eos_token_id=self.tokenizer.eos_token_id,
    #                                pad_token_id=self.tokenizer.eos_token_id,
    #        )
    #        final_outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    #        final_outputs = cut_off_text(final_outputs, '</s>')
    #        final_outputs = remove_substring(final_outputs, prompt)
    #
    #    return final_outputs#, outputs





if __name__ == "__main__":

    hf = HuggingFaceService()

    llm = hf.llm
    print(llm)

    general_knowlege_queries = [
        "What year was America founded?",
        "Tell us about the first humans who landed on the moon."
    ]

    for query in general_knowlege_queries:
        # response = llm.predict(query).strip()
        prompt = compile_prompt(prompt=query)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        #response = llm_chain.run(query) # chain({'foo': 1, 'bar': 2})
        #> ValueError: A single string input was passed in, but this chain expects multiple inputs (set()). When a chain expects multiple inputs, please call it by passing in a dictionary, eg `chain({'foo': 1, 'bar': 2})`
        response = llm_chain({"query": query}) # ooh it's slow?
        parse_text(response)


    breakpoint()
    exit()

    # PROMPT

    system_prompt = "You are an advanced assistant that excels at translation. "
    instruction = "Convert the following text from English to French:\n\n {text}"
    prompt = compile_prompt(prompt=instruction, system_prompt=system_prompt, input_variables=["text"])
    print(template)

    # CHAIN

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    query = "how are you today?"
    while query != "":
        print(query)
        response = llm_chain.run(query)
        parse_text(response)
        print("------")
        query = input("Query (or press enter to stop): ")
