import text_table_tools as ttt
import codecs
import os

def find_labeled(filename):
    flist = open(filename).readlines()

    parsing = False
    lines = []
    tables = []
    for line in flist:

        if line.startswith("</dashTable>") or line.startswith("</dotTable>"):
            parsing = False
            tables.append("".join(lines))
            lines = []
        if parsing:
            lines.append(line)
        if line.startswith("<dashTable>") or line.startswith("<dotTable>"):
            parsing = True
    return tables

labeled_folder = "/mnt/data/sunlight/tables/labeled"
out_folder = "/mnt/data/sunlight/tables/evaluate"

for doc in os.listdir(labeled_folder):
    # get table parser tables
    doc_file = os.path.join(labeled_folder, doc)
    paragraph_list = ttt.get_paragraphs(codecs.open(doc_file, 'r', 'utf8'))
    table_parser_tables = ttt.identify_tables(paragraph_list)

    # get labeled tables
    labeled_tables = find_labeled(doc_file)

    print "For document %s:" % doc_file
    print "Number of hand labeled tables: %s" % len(labeled_tables)
    print "Number of table parser tables: %s" % len(table_parser_tables)
    print "\n\n\n\n\n"

    # output results for manual inspection
    labeled_file = open(os.path.join(out_folder, doc + "-labeled"), "w")
    parsed_file = open(os.path.join(out_folder, doc + "-parsed"), "w")
    labeled_file.write("TABLE:\n".join(labeled_tables))
    parsed_file.write("TABLE:\n".join("".join(table.content) for table in table_parser_tables))
