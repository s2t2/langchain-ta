

# https://docs.pydantic.dev/latest/

from typing import List
from pydantic import BaseModel, Field

COMMENTS = "The comment to accompany the score. Provides justification for the score. Cites specific content present or absent from the response."
CONFIDENCE_SCORE = "Confidence level in the score. Values range between 0 (low confidence) and 1 (high confidence)"

ONE_TO_FIVE_SCORE = "The score. Values range from 1 (low) to 5 (high), in increments of 0.25 (where 1 is poor, 3 is decent, 4 is good, 4.5 is great, and 5 is perfect). Indicates the degree to which the response completely, thoroughly, and accurately addresses all the questions."
ZERO_TO_ONE_SCORE = "The score. Values range from 0 (low) to 1 (high), in increments of 0.05 (where 0 is unattempted or blank, 0.5 is incorrect or incomplete, 0.75 is good, 0.9 is great, and 1.0 is perfect). Indicates the degree to which the response completely, thoroughly, and accurately addresses the question."

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
