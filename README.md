# homework-grader-py


Setup environment:

```sh
conda create -n langchain-2024 python=3.10

conda activate langchain-2024

pip install -r requirements.txt
```


Create ".env" file:

```
OPENAI_API_KEY="sk-..."
SUBMISSIONS_DIRPATH="/Users/USERNAME/Desktop/GRADING HW 4"
```


## Usage

```sh
python -m app.submissions_manager
```


```sh
python -m app.document_processor
```
