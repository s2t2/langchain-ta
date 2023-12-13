

from app.text_splitter import split_text_by_substrings


input_text = """
Substring A: This is the first part.
This is still part of the first part.
Substring B: This is the second part.
Substring A: This is the third part.
"""


def test_substring_splitting():

    results = split_text_by_substrings(input_text, "Substring A:", "Substring B:")
    assert results == ['',
        'Substring A: This is the first part. This is still part of the first part.',
        'Substring B: This is the second part.',
        'Substring A: This is the third part.'
    ]
