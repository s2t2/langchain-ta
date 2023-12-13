# homework-grader-py

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
3. Move a copy of the starter notebook (which contains instructions and some starer code) into the submissions directory, and rename it so it contains "STARTER" somewhere in the file name.


### Environment Variables Setup

Create ".env" file and set environment variables:

```sh
# this is the ".env" file...

OPENAI_API_KEY="sk-..."

SUBMISSIONS_DIRPATH="/Users/USERNAME/Desktop/GRADING HW 4"
```


## Usage

Demonstrate ability to identify submission files:

```sh
python -m app.submissions_manager
```

Process the starter file:

```sh
python -m app.jobs.starter

# SIMILARITY_THRESHOLD=0.75 ...
CHUNK_SIZE=600 CHUNK_OVERLAP=0 FIG_SHOW=false python -m app.jobs.starter
```

Process all submission files:

```sh
python -m app.jobs.submissions
```

## Testing

Run tests:

```sh
pytest --disable-pytest-warnings
```
