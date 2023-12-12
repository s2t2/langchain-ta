

from pprint import pprint


def split_text_by_substrings(input_text, substring_a, substring_b):
    """Source: https://chat.openai.com/share/3af75e94-a455-4fae-94e4-b0a3ce2d7578 """
    result = []
    current_string = ""

    for line in input_text.splitlines():
        if substring_a in line:
            if current_string:
                result.append(current_string.strip())
            current_string = line
        elif substring_b in line:
            if current_string:
                result.append(current_string.strip())
            current_string = line
        else:
            current_string += " " + line

    if current_string:
        result.append(current_string.strip())

    return result


if __name__ == "__main__":

    input_text = """
    Substring A: This is the first part.
    This is still part of the first part.
    Substring B: This is the second part.
    Substring A: This is the third part.
    """

    result_list = split_text_by_substrings(input_text, "Substring A:", "Substring B:")
    pprint(result_list)

    assert result_list == ['',
        'Substring A: This is the first part. This is still part of the first part.',
        'Substring B: This is the second part.',
        'Substring A: This is the third part.'
    ]
