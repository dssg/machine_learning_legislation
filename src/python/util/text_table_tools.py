import re

def paragraphs(fileobj, separator='\n'):
    if separator[-1:] != '\n': separator += '\n'
    paragraph = []
    for line in fileobj:
        if line == separator:
            if paragraph:
                yield ''.join(paragraph)
                paragraph = []
        else:
            paragraph.append(line)
    if paragraph: yield ''.join(paragraph)

def is_table(paragraph):
    dots_re = re.compile(r"\.\.\.")
    digit_re = re.compile(r"\d+")
    dash_re = re.compile(r"---")
    lines = paragraph.split("\n")
    matching_lines = [line for line in lines if (dots_re.search(line) and digit_re.search(line)) or dash_re.search(line)]

    if float(len(matching_lines))/len(lines) > 0.3:
        return True
    else:
        return False

def get_table_rows(table):
    rows = []
    table = table.replace("..", " ")
    for line in table.split("\n"):
        rows.append([col for col in re.split("[ ]{3,}", line) if col != "." and col != ""])

    return rows


