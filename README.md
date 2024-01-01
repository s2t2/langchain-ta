# Langchain TA (Automated Homework Grading Agent)

An AI agent for grading homework assignments submitted as .IPYNB notebook documents.

For this particular use case we assume the homework submission documents are based on a common "starter" / instructions document. And we will grade the homeworks based only on the differences (i.e. unique submission content only).

Capabilities:

  1. **Cell-based Document Splitting**: We use intelligent cell-based splitting of the .IPYNB notebook documents that allows us to reference each cell separately, and reference the code cells and text cells separately, as needed. We generate artifacts from the document splitting process like a CSV file of all cell contents and metadata, to help speed up the grading process, without the use of AI agents.

  2. **Document Retrieval**: We use text embedding models to query the documents, to find the most relevant cell content for each question. We generate artifacts from the relevance search process which may further speed up the grading process without the use of AI agents.

  3. **Retreival Augmented Generation (RAG)**: Finally we leverage an AI agent to grade each homework document based on the relevant cell contents for each question. We feed the agent only the relevant contents for each question, rather than the entire submissions file, to cut down on costs, as currently we are using OpenAI based LLM models that incur costs based on the number of tokens / characters used in the prompts we pass to the model.



## Setup

### Environment Setup

Setup virtual environment:

```sh
conda create -n langchain-2024 python=3.10

conda activate langchain-2024
```

Install package dependencies:

```sh
pip install -r requirements.txt
```


### Submission Files Setup

Setup submission files:

1. Download submission files from the learning management system. It will be a zip file of .IPYNB files.
2. Unzip, and note the directory (i.e. `SUBMISSIONS_DIRPATH`).
3. Move a copy of the starter notebook (which contains instructions and some starer code) into the submissions directory, and note the filename (i.e. `STARTER_FILENAME`).


### LLM Setup

Choose an LLM provider (OpenAI or Meta Llama). OpenAI might be easier to get started, but costs money. Whereas Meta Llama is free, and for this reason is the recommended LLM provider. Based on your chosen LLM provider, see the corresponding setup instructions below.

#### OpenAI Setup

Obtain an OpenAI API Key (i.e. `OPENAI_API_KEY`).

#### Llama Setup

See: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf

First, visit the [Meta Llama website](https://ai.meta.com/resources/models-and-libraries/llama-downloads/), fill out the request form, and wait until your request is accepted.

Then, create a [Hugging Face account](https://huggingface.co) (using the same email address from step 1), and obtain a [user access token](https://huggingface.co/docs/hub/security-tokens) (i.e. `HUGGING_FACE_TOKEN`).


### Environment Variables Setup

Create ".env" file and set environment variables:

```sh
# this is the ".env" file...

# choose one based on your preferred llm provider:
OPENAI_API_KEY="sk-..."
HUGGINGFACE_TOKEN="hf_..."

# for grading a particular homework:
SUBMISSIONS_DIRPATH="/Users/USERNAME/Desktop/GRADING HW 4"
STARTER_FILENAME="Homework_X_STARTER.ipynb"
FILE_ID_SPLIT_INDEX="0" # 0 for files from Canvas, 1 for files from Blackboard
```


## Usage

### Submission Files Manager

Demonstrate ability to access submission files:

```sh
python -m app.submissions_manager
```

### LLM

Demonstrate ability to query your LLM of choice (OpenAI or Meta Llama).

Query the OpenAI LLM:

```sh
TEMP=0.6 python -m app.openai.llm
```

Query the Meta Llama LLM:

```sh
TEMP=0.6 python -m app.meta.llm
```
> NOTE: the first time the LLama model is run, it will take a while to download.

### Cell-based Document Splitting

Process the starter file:

```sh
python -m app.starter_doc_processor

# FIG_SHOW=false python -m app.starter_doc_processor

# FIG_SHOW=false CHUNK_SIZE=600 CHUNK_OVERLAP=0 python -m app.starter_doc_processor

# FIG_SHOW=false CHUNK_SIZE=600 CHUNK_OVERLAP=0 SIMILARITY_THRESHOLD=0.75 python -m app.starter_doc_processor
```

Process all submission files (provides metadata about the file contents, compares against starter):

```sh
python -m app.submissions_processor

#FIG_SHOW=false python -m app.submissions_processor
```

### Document Retrieval

Designate the homework questions (hard-coded in "app/prompts" dir for now).

Find the most relevant content from the submissions files for answering each of the homework questions (currently uses lower-cost text embeddings model "text-embedding-ada-002" from OpenAI to find relevant documents):

```sh
DOCS_LIMIT=5 python -m app.submissions_retriever

# DOCS_LIMIT=5 SIMILARITY_THRESHOLD=0.75 CHUNK_SIZE=1000 CHUNK_OVERLAP=0 python -m app.submissions_retriever
```


### Retreival Augmented Generation (RAG)

Use an LLM for grading:

```sh
DOCS_LIMIT=5 python -m app.openai.submissions_grader

# DOCS_LIMIT=5 SIMILARITY_THRESHOLD=0.75 CHUNK_SIZE=1000 CHUNK_OVERLAP=0 python -m app.submissions_grader
```


## Testing

Run tests:

```sh
pytest --disable-pytest-warnings
```
