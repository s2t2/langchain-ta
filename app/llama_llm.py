
# adapted from youtube video about llama and langchain: ________________

import os
from dotenv import load_dotenv

import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from app.llama_prompts import get_prompt, cut_off_text, remove_substring

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"


class LlamaService:
    def __init__(self, model_name=MODEL_NAME, hf_token=HUGGINGFACE_TOKEN):
        self.model_name = model_name
        self.hf_token = hf_token

    @property
    def tokenizer(self):
        # https://huggingface.co/transformers/v2.11.0/model_doc/auto.html?highlight=autotokenizer#autotokenizer
        return AutoTokenizer.from_pretrained(self.model_name, token=self.hf_token)

    @property
    def model(self):
        # https://huggingface.co/docs/transformers/model_doc/auto#transformers.AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained(self.model_name, token=self.hf_token,
                                                    device_map='auto', torch_dtype=torch.float16,
        )

    @property
    def pipeline(self):
        # https://huggingface.co/docs/transformers/main_classes/pipelines
        return pipeline(task="text-generation", model=self.model, tokenizer= self.tokenizer,
                        device_map="auto", torch_dtype=torch.bfloat16,
                        max_new_tokens=512, do_sample=True, top_k=30, num_return_sequences=1,
                        eos_token_id=self.tokenizer.eos_token_id
        )


    def generate(self, text):
        prompt = get_prompt(text)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            inputs = self.tokenizer(prompt, return_tensors="pt").to('cuda')
            outputs = self.model.generate(**inputs,
                                    max_new_tokens=512,
                                    eos_token_id=self.tokenizer.eos_token_id,
                                    pad_token_id=self.tokenizer.eos_token_id,
            )
            final_outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            final_outputs = cut_off_text(final_outputs, '</s>')
            final_outputs = remove_substring(final_outputs, prompt)

        return final_outputs#, outputs
