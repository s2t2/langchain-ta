

# https://docs.pydantic.dev/latest/

from typing import List
from pydantic import BaseModel, Field

COMMENTS = "Comment to accompany the score."
CONFIDENCE_SCORE = "Confidence level in the score. Values range from 0.0 (low) to 1.0 (high confidence)."

#ZERO_TO_ONE_SCORE = "The score. Values range from 0 (low) to 1 (high), in increments of 0.25 (where 0 is unattempted or blank, 0.5 is incorrect or incomplete, 0.75 is good, and 1.0 is great / thorough). Indicates the degree to which the response completely, thoroughly, and accurately addresses the question."
ZERO_TO_ONE_SCORE = "The score. Values generally range from 0.0 (low) to 1.0 (high), although it is possible for score to be greater than 1.0."
ONE_TO_FIVE_SCORE = "The score. Values generally range from 1.0 (low) to 5.0 (high)."

class Student(BaseModel):
    """A student."""
    name: str = Field(description="The student's full name.")
    net_id: str = Field(description="The student's identifier.")


class DocumentScoring(BaseModel):
    """A document scoring."""
    score: float = Field(description=ONE_TO_FIVE_SCORE)
    comments: str = Field(description=COMMENTS)
    confidence: float = Field(description=CONFIDENCE_SCORE)


class QuestionScoring(BaseModel):
    """A question scoring."""
    question_id: str = Field(description="The question identifier.")
    score: float = Field(description=ZERO_TO_ONE_SCORE)
    comments: str = Field(description=COMMENTS)
    confidence: float = Field(description=CONFIDENCE_SCORE)


class QuestionScorings(BaseModel):
    """A List of question scorings, for handling multiple questions in the same prompt."""
    scorings: List[QuestionScoring]



if __name__ == "__main__":

    student = Student(name="Sally Student", net_id="G123456")
    print(student)

    scoring = DocumentScoring(score=3.5, comments="Great work!", confidence=1.0)
    print(scoring)

    qs = QuestionScoring(question_id="5.1", score=0.75, comments="Great work!", confidence=1.0)
    scorings = QuestionScorings(scorings=[qs])
    print(scorings)
