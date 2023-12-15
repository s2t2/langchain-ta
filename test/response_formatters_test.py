

from app.response_formatters import Student, DocumentScoring, QuestionScoring, QuestionScorings


def test_student_formatter():


    student = Student(name="Sally Student", net_id="G123456")
    print(student)

    scoring = DocumentScoring(score=3.5, comments="Great work!", confidence=1.0)
    print(scoring)

    qs = QuestionScoring(question_id="5.1", score=0.75, comments="Great work!", confidence=1.0)
    scorings = QuestionScorings(scorings=[qs])
    print(scorings)

    breakpoint()
