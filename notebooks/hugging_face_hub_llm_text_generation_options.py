# -*- coding: utf-8 -*-
"""Hugging Face Hub - LLM Text Generation Options

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HOFjCLqhkvqEa8cHfvAqIhYwLeBTs0sw

## Setup
"""

from warnings import filterwarnings
filterwarnings("ignore")

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install langchain

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install einops

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install accelerate # need to restart the runtime / session after installing

"""## Prompts"""

QUERIES = [
    "What year was America founded?",
    "Tell us about the first humans to land on the moon.",
    "Tell me a joke.",
    "Tell me an innapropriate joke."
]

"""## Hugging Face Hub"""

from google.colab import userdata
from getpass import getpass

HF_TOKEN = userdata.get("HUGGING_FACE_TOKEN") or getpass("Please input your HUGGING_FACE_TOKEN: ")
print(HF_TOKEN[0:3], "...")

""" + https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads
 + https://python.langchain.com/docs/integrations/llms/huggingface_hub
"""

# https://python.langchain.com/docs/integrations/llms/huggingface_hub
# https://python.langchain.com/docs/integrations/llms/huggingface_pipelines
# https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads
#

from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class HuggingFaceService:
    def __init__(self, repo_id, temp=0.5, max_length=64, token=HF_TOKEN):
        self.token = token
        self.repo_id = repo_id
        self.temp = temp
        self.max_length = max_length

    @property
    def llm(self):
        return HuggingFaceHub(
            repo_id=self.repo_id, huggingfacehub_api_token=self.token,
            model_kwargs={"temperature": self.temp, "max_length": self.max_length}
        )

    @property
    def system_prompt(self):
        template = "You are a helpful and accurate assistant. Please answer the following question: {query}."
        return PromptTemplate.from_template(template)

    def generate(self, query):
        llm_chain = LLMChain(prompt=self.system_prompt, llm=self.llm)
        return llm_chain({"query": query})

hf = HuggingFaceService(repo_id="google/flan-t5-xxl", temp=0.5, max_length=64)

for query in QUERIES:
    print("---------")
    print(hf.generate(query))

# https://huggingface.co/facebook/opt-125m
hf = HuggingFaceService(repo_id="facebook/opt-125m", temp=0.0, max_length=64)
for query in QUERIES:
    print("---------")
    print(hf.generate(query))

# TOO SLOW
#hf = HuggingFaceService(repo_id="databricks/dolly-v2-3b", temp=0.5, max_length=64)
#for query in QUERIES:
#    print("---------")
#    print(hf.generate(query))





# https://huggingface.co/microsoft/phi-2

#from transformers import AutoModelForCausalLM
#
#class PhiService(HuggingFaceService):
#    #trust_remote_code=True
#
#    def __init__(self, temp=0.5, max_length=64, token=HF_TOKEN):
#        super().__init__(repo_id="microsoft/phi-2", temp=temp, max_length=max_length, token=token)
#
#
#    def llm(self):
#        return AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype=torch.float32, device_map="cuda", trust_remote_code=True)
#
#
#
#
#
##hf = HuggingFaceService(repo_id="microsoft/phi-2", temp=0.0, max_length=64)
## ValueError: Error raised by inference API: The repository for microsoft/phi-2 contains custom code which must be executed to correctly load the model. You can inspect the repository content at https://hf.co/microsoft/phi-2.
## Please pass the argument `trust_remote_code=True` to allow custom code to be run.
#hf = PhiService()
#for query in QUERIES:
#    print("---------")
#    print(hf.generate(query))

"""## From Pretrained"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_default_device("cuda")

model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)

inputs = tokenizer('''def print_prime(n):
   """
   Print all primes between 1 and n
   """''', return_tensors="pt", return_attention_mask=False)

outputs = model.generate(**inputs, max_length=200)
text = tokenizer.batch_decode(outputs)[0]
print(text)

for query in QUERIES:
    print("---------")
    inputs = tokenizer(query, return_tensors="pt", return_attention_mask=False)
    outputs = model.generate(**inputs, max_length=200)
    text = tokenizer.batch_decode(outputs)[0]
    print(text)



# https://huggingface.co/meta-llama/Llama-2-7b-chat-hf

# https://huggingface.co/facebook/opt-125m
#hf = HuggingFaceService(repo_id="meta-llama/Llama-2-7b-chat-hf", temp=0.0, max_length=64)
#for query in QUERIES:
#    print("---------")
#    print(hf.generate(query))

#> ValueError: Error raised by inference API: Model requires a Pro subscription; check out hf.co/pricing to learn more. Make sure to include your HF token in your query.

"""## Llama from Pretrained"""

from langchain.prompts import PromptTemplate

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


compile_prompt("What year was America founded?")

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.prompts import PromptTemplate
from langchain.chains import  LLMChain
from langchain.llms.huggingface_pipeline import HuggingFacePipeline


MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
TEMP = 0.7 # @ param {type:"slider", min:0, max:1, step:0.1}


class LlamaService:
    # https://python.langchain.com/docs/integrations/llms/huggingface_pipelines

    def __init__(self, model_name=MODEL_NAME, temp=TEMP, token=HF_TOKEN):
        self.model_name = model_name
        self.token = token # hugging face api token
        self.temp = temp

        self.device_type = "cuda" if torch.cuda.is_available() else "cpu"
        # https://stackoverflow.com/a/73530618/670433
        # https://huggingface.co/openlm-research/open_llama_7b_v2/discussions/2
        # https://pytorch.org/docs/stable/tensors.html
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    @property
    def tokenizer(self):
        # https://huggingface.co/transformers/v2.11.0/model_doc/auto.html?highlight=autotokenizer#autotokenizer
        return AutoTokenizer.from_pretrained(self.model_name, token=self.token) # cache_dir=CACHE_DIRPATH

    @property
    def model(self):
        # https://huggingface.co/docs/transformers/model_doc/auto#transformers.AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained(
            self.model_name, token=self.token, device_map="auto", torch_dtype=self.torch_dtype
        )

    @property
    def pipeline(self):
        """wrapper for tokenizer and model, for performing the 'text-generation' task"""
        # https://huggingface.co/docs/transformers/main_classes/pipelines
        return pipeline(
            task="text-generation", model=self.model, tokenizer=self.tokenizer,
            device_map="auto", torch_dtype=self.torch_dtype, # torch.bfloat16
            max_new_tokens=512, do_sample=True, top_k=30, num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
        )

    @property
    def llm(self):
        return HuggingFacePipeline(
            #model_id=self.model_name, # this one is getting set to "gpt2" by default?
            pipeline=self.pipeline, model_kwargs={"temperature":self.temp}
        )


    def generate(self, query):
        prompt = compile_prompt(prompt=query)
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        response = llm_chain({"query": query})  # llm_chain.run(query) )
        #parse_text(response)
        return response

ll = LlamaService()

for query in QUERIES:
    print("-----------")
    response = ll.generate(query)
    print(response)