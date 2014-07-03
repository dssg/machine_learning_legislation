import re
import os, sys
import codecs
import operator
from pprint import pprint
import argparse
import path_tools
from collections import Counter
import csv
from itertools import chain
import math



class Table:
    def __init__(self):
        self.content = [] 
        self.title = []
        self.offset = 0
        self.length = 0
        self.body = []
        self.header = []
        self.rows = []
        self.row_offsets = []
        self.candidate_entities = []
        
    def __str__(self):
        pass #print self.title, self.content
        
class TableRow:
    def __init__(self):
        self.raw_text =""
        self.cells = []
        self.offset = 0
        self.length = 0
        self.number = 0
    def __str__(self):
        return  ' | '.join(map(str, self.cells))
        
class TableCell:
    def __init__(self):
        self.raw_text = ""
        self.clean_text = ""
        self.offset = 0
        self.length = 0
        
    def __str__(self):
        return self.clean_text
            
        
class Paragraph:
    def __init__(self):
        self.content = []
        self.offset = 0
        self.length = 0

class ParsingPrimitives:
    def __init__(self):
        self.dots_re = re.compile(r'\.{2,}')
        self.spaces_re = re.compile(r'^[ ]+')
        self.money_re = re.compile(r'\$*[\d,]+')
        
        
    def has_dots(self, cell):
        """
        returns boolean indicating whether the cell has multiple consecutive dots
        """
        return self.dots_re.search(cell) != None
        
    def indentation_count(self, cell):
        """
        finds the number of empty spaces at the beginning of the cell
        """
        match = self.spaces_re.search(cell)
        if match:
            begin, end = match.span()
            length = end - begin
            return length
        else:
            return 0
                
    def ends_with_colon(self, cell):
        return cell.strip().endswith(':')
        
    def is_money_cell(self, cell):
        """
        returns boolean whether a cell matches money regex
        """
        return money_re.search(cell) != None

class Entropy:
    def __init__(self):
        pass
    def compute_entropy(self,iterable):
        """
        computes the entropy of an iterable
        each element in the iterable should implement the hash function
        if it's not a standard type like str or int
        """
        counts = {}
        n = len(iterable) * 1.0
        for i in iterable:
            counts[i] = counts.get(i,0) +1
        entropy = 0
        for k,v in counts.iteritems():
            entropy += math.log((v/ n)) * (v/n) 
        return -1 * entropy

def get_paragraphs(fileobj, separator='\n'):
    paragraphs = []
    if separator[-1:] != '\n': separator += '\n'
    paragraph = Paragraph()
    paragraph.offset = 0
    offset = 0
    for line in fileobj:
        if line == separator:
            if len(paragraph.content) > 0:
                paragraph.length = sum (map (lambda a: len(a), paragraph.content))
                paragraphs.append(paragraph)
                paragraph = Paragraph()
                paragraph.offset = offset + len(line)
        else:
            paragraph.content.append(line)
        offset += len(line)
    if len(paragraph.content): paragraphs.append(paragraph)
    return paragraphs
    
def identify_tables(list_paragraphs):
    """
    returns a list of tables from the list of paragraphs
    """
    tables= []
    i = -1
    while i+1 < len(list_paragraphs) :
        i += 1
        p = list_paragraphs[i]
        if is_table(p.content):
            first_par_index = i
            table = Table()
            table.content = p.content
            table.offset = p.offset
            table.length = p.length
            dashes_length , num_lines = get_max_dash_lines_count(p.content)
            if num_lines == 2:
                # we only found two dashes, make sure the distance between them is no longer than 3
                MAX_DISTANCE = 4
                line_numbers = get_line_numbers_matching_re(p.content, r"^---*", match_length=dashes_length)
                if abs(line_numbers[1]-line_numbers[0]) <= MAX_DISTANCE:
                    # apply the three dash lines heurstic
                    for j in range(i+1, len(list_paragraphs)):
                        p_next = list_paragraphs[j]
                        p_next_dashes_length , p_next_num_lines = get_max_dash_lines_count(p_next.content)
                        i = j
                        if p_next_dashes_length == dashes_length:
                            table.content = table.content + p_next.content
                            table.length += p_next.length
                            break
                        else:
                            p_next_next = list_paragraphs[j+1]
                            if not is_table(p_next.content) and not is_table(p_next_next.content):
                                break # two consecutive not table paragraphs
                        table.content = table.content + p_next.content
                        table.length += p_next.length
            
            table.title = get_table_title(list_paragraphs[:first_par_index])
            tables.append(table)
            
    for table in tables:
        find_table_header(table)
        table_type = detect_table_type(table)        
        print table_type
        if table_type == 'dashes':
            parse_dashed_table(table)
        elif table_type == 'dots':
            parse_dots_table(table)
            #find_table_rows(table)
        #get_candidate_entities(table)
        
    return tables


def find_table_header(table):
    """
    given a table object, returns the headers
    """
    dashes_length , num_lines = get_max_dash_lines_count(table.content)
    if num_lines >= 2:
        line_numbers = get_line_numbers_matching_re(table.content, r"^---*", match_length=dashes_length)
        MAX_DISTANCE = 4
        if abs(line_numbers[1]-line_numbers[0]) <= MAX_DISTANCE:
            header_content = table.content[line_numbers[0] +1:  line_numbers[1]]
            table.body = table.content[line_numbers[1]+1:]
            table.header = parse_header(header_content)
        else:
            table.body = table.content
    else:
        table.body = table.content


        
def parse_header(header_content):
    """
    given a list of lines that make a header, parse these lines and return list of headers
    header_content: list of lines
    """
    words = []
    re_dashes = re.compile('^-{2,}')
    for i in range(len(header_content)):
        line = header_content[i]
        parts = re.split("[ ]{2,}", line)
        if len(parts) > 0:
            prev_token_offset = 0
            for j in range (len(parts)):
                part = parts[j]
                clean_part = part.strip()
                if re_dashes.search(part):
                    continue
                if len(clean_part) > 0:
                    offset = line.find(part,prev_token_offset)
                    prev_token_offset = offset + len(part)
                    words.append( (clean_part, i, offset, offset+len(clean_part)))
                
    s_words= sorted(words, key=operator.itemgetter(2))
    clusters = []
    clusters.append([s_words[0],])
    for i in range(1,len(s_words)):
        w = s_words[i]
        prev_w = s_words[i-1]
        if w[2] < prev_w[3]:
            clusters[-1].append(w)
        else:
            clusters.append([w,])
            
    headers = []
    for cluster in clusters:
        headers.append(' '.join(map(lambda a: a[0], sorted(cluster, key=operator.itemgetter(1)))))
    return headers
     

def get_candidate_entities(table):
    counts = Counter(list(chain.from_iterable(table.rows)))
    entities = [key for key in counts.keys() if (counts[key]<3 and not re.match(r'\$*[\d,]{3,}', key))]
    #pprint(entities)
    return entities       

def detect_table_type(table):
    """
    detects the type of the table. it can be either dots or dashes
    """
    pp = ParsingPrimitives()
    table_type = 'dashed'
    has_dots = reduce(lambda a, b: a or b , map( pp.has_dots , table.content))
    if has_dots:
        return 'dots'
    else:
        return 'dashes'

def merge_rows(rows):
    """
    given  rows, they are merged into a NEW row
    assuming the first row appears before others
    """
    row = TableRow()
    row.number = rows[0].number
    row.offset = rows[0].offset
    row.length = sum(map ( lambda row: row.length , rows)) + len(rows) -1
    row.raw_text = ' '.join( map(lambda row: row.raw_text, rows))
    for i in range(len(rows[0].cells)):
        cell = TableCell()
        cell.offset = rows[0].cells[i].offset
        cell.raw_text = ' '.join(map(lambda row: row.cells[i].raw_text, rows))
        cell.length = len(cell.raw_text)
        cell.clean_text = ' '.join(map(lambda row: row.cells[i].clean_text, rows)).strip()
        row.cells.append(cell)
    return row        

def parse_dashed_table(table):
    """
    parses a table of the dashed type
    """
    parse_table_structure(table)
    rows_to_merge = []
    candidates = [table.rows[0],]
     
    for i in range(1,len(table.rows)):
        row = table.rows[i]
        if row.number - candidates[-1].number  ==1:
            candidates.append(row)
        else:
            if len(candidates) > 1:
                rows_to_merge.append(candidates)
            candidates = [row,]
    dirty_row_numbers = set()
    for candidates in rows_to_merge:
        for row in candidates:
            dirty_row_numbers.add(row.number)
    new_rows = []
    for candidates in rows_to_merge:
        new_row = merge_rows(candidates)
        new_rows.append(new_row)
    rows = [ row for row in table.rows if row.number not in dirty_row_numbers ]
    rows += new_rows
    rows = sorted(rows, key = lambda a: a.number)
    table.rows = rows
            
                
            
    for row in table.rows:
        print row.number
    return
    block = []
    row_number = 0
    offset = 0
    re_dashes = re.compile(r'^-{2,}')
    #import pdb; pdb.set_trace()
    for i in range(len(table.body)):
        line = table.body[i]
        if re_dashes.search(line) and len(block) > 0:
            cell_contents = parse_header(block)
            row = TableRow()
            row_number +=1
            row.number = row_number
            row.offset = offset
            row.raw_text = ''.join(block)
            row.length = len(row.raw_text)
            offset += row.length
            cell_offset = 0
            for part in cell_contents:
                cell = TableCell()
                cell.raw_text = part
                cell.clean_text = part
                cell.offset = row.raw_text.find(part.split()[0],cell_offset)
                cell.length = len(cell.raw_text)
                cell_offset += cell.length
                row.cells.append(cell)
            table.rows.append(row)
            block = []                
        else:
            block.append(line)

def parse_dots_table(table):
    parse_table_structure(table)
    columns = [ [table.rows[i].cells[j].clean_text for i in range(len(table.rows)) ] 
    for j in range(len(table.rows[0].cells)) ]
    
    
        
def parse_table_structure(table):
    """
    parses the structure of a table into equal number of columns
    """
    find_table_rows(table)
    #for r in table.rows:
    #    find_row_cells(row)
    #applying multi line table heuristic
    heat_map = []
    max_line_length = max(map(lambda a: len(a.raw_text) ,table.rows))
    for row in table.rows:
        padded_str = row.raw_text[:-1] + ' '*(max_line_length-len(row.raw_text)) + '\n'
        empty_chars = set( [i for i in range(len(padded_str)) if padded_str[i] ==' '])
        heat_map.append(empty_chars)
    intersections = reduce (lambda a, b : a.intersection(b), heat_map)
    indices = sorted(list(intersections) )
    boundaries = [('a',0),] # just for sanity check, we know it's char
    i = 1
    begin_index = indices[0]
    prev_index = indices[0]
    while i < len(indices):
        if indices[i] - prev_index == 1:
            prev_index = indices[i]
        else:
            boundaries.append( (begin_index, prev_index))
            begin_index = indices[i]
            prev_index = indices[i]
        i+=1
    boundaries.append((begin_index, prev_index))
    boundaries.append((-1,'a'))
    for row in table.rows:
        for i  in range(len(boundaries)-1):
            cell = TableCell()
            cell.raw_text = row.raw_text[boundaries[i][1]:boundaries[i+1][0]]
            cell.clean_text = cell.raw_text.strip().rstrip('.')
            cell.offset = row.raw_text.find(cell.raw_text, boundaries[i][1])
            cell.length = len(cell.raw_text)
            row.cells.append(cell)

def compute_table_entropy(table):
    e = Entropy()
    if len(table.rows) ==0 :
        return 0
    columns = [ [table.rows[i].cells[j].clean_text for i in range(len(table.rows)) ] 
    for j in range(len(table.rows[0].cells)) ]
    entropies = []
    for i in range(len(columns)):
        entropies.append(e.compute_entropy(columns[i]))
        #print "Entropy of Column %d equals %f" %(i+1, e.compute_entropy(columns[i])) 
    return entropies  

def find_row_cells(row):
    """
    given TableRow object, segments it into cells
    """
    parts = re.split("[ ]{2,}", row.raw_text)
    
    if len(parts) > 0:
        for part in parts:
            cell = TableCell()
            cell.raw_text = part
            clean_part = part.strip().rstrip('.')
            cell.clean_text = clean_part
            if re_dashes.search(clean_part) or len(clean_part) == 0:
                continue 
            row.cells.append(cell)        

def find_table_rows(table):
    """
    given a table object, finds the rows that contain data
    assuming that the header was parsed already
    """
    re_dashes = re.compile(r'^-{2,}')
    re_ignore = re.compile(r'^[\.=-]+')
    re_spaces = re.compile(r'[ ]{2,}')
    offset = 0
    row_number = -1
    max_dashes = get_max_dash_lines_count(table.body)
    
    for i in range(len(table.body)):
        row_number += 1
        row = TableRow()
        row.number = row_number
        line = table.body[i]
        row.raw_text = line
        row.offset = offset
        line_length = len(line)
        row.length = line_length
        offset += line_length
        if len(line.strip()) == 0:
            continue
        if re_ignore.search(line.strip()):
            continue
        if not re_spaces.search(line):
            continue
        table.rows.append(row)
        

                

def get_table_title(list_paragraphs):
    title = []
    lines = []
    for p in list_paragraphs:
        lines.extend(p.content)
    k = len(lines) -1
    while k > 0:
        if len(lines[k].strip()) == 0:
            k -=1
            continue
        else:
            if not lines[k].startswith(' ') :
                break
            else:
                title.append(lines[k])
                k -=1
                
    title.reverse()
    return title        

def get_line_numbers_matching_re(lines, re_pattern, match_length=None):
    """
    returns list of line numbers that match re_pattern, such that each match consumes at least match_length characters
    """
    matches = []
    regex = re.compile(re_pattern)
    for i in range(len(lines)):
        match = regex.match(lines[i])
        if match:
            start , end = match.span()
            if match_length:
                if (end-start) == match_length:
                    matches.append(i)
            else:
                matches.append(i)
                
    return matches
                        

def get_max_dash_lines_count(text_list):
    """
    given a list of lines, 
    returns the number of times the longest line that match the ---* regex appears, and the length of that
    line in  tuple , such that (length, count)
    """
    dash_re = re.compile(r"^---*")
    dash_length ={0:0}
    for line in text_list:
        match = dash_re.search(line)
        if match:
            begin, end = match.span()
            length = end - begin
            dash_length[ length ] = dash_length.get(length,0) + 1
    
    return sorted( dash_length.items() , key=operator.itemgetter(0), reverse=True)[0]
            

def is_table(paragraph):
    dots_re = re.compile(r"\.\.\.")
    digit_re = re.compile(r"\d+")
    dash_re = re.compile(r"---")
    spaces_re = re.compile(r'[\S]+[ ]{2,}')
    lines = paragraph
    matching_lines = [line for line in lines if (dots_re.search(line) and digit_re.search(line)) 
    or (spaces_re.search(line) and digit_re.search(line)) or dash_re.search(line)]

    if float(len(matching_lines))/len(lines) > 0.3:
        return True
    else:
        return False





if __name__=="__main__":
    parser = argparse.ArgumentParser(description='identify tables and paragrapghs in bills')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tables', action='store_true' , help ="print tables")
    group.add_argument('--paragraphs', action='store_true', help="print paragrapghs")
    parser.add_argument('--path', required=True, help='path to congress bill or report')
    args = parser.parse_args()
    path = args.path
    paragrapghs_list = get_paragraphs(codecs.open(path,'r','utf8'))
    if args.tables:
        tables = identify_tables(paragrapghs_list)
        for t in tables:
            print "title:" 
            pprint(t.title)
            print '='*50
            
            print "content" 
            pprint(t.content) 
            print "Table offset %d, length %d" %(t.offset, t.length)
            print "Headers:"
            pprint(t.header)
            print "Rows:"
            for row in t.rows: print row
            print 'Entropy:'
            print compute_table_entropy(t)
            print '=' *50
            print'\n'*8
            #pprint (t.candidate_entities)
    if args.paragraphs:
        for p in paragrapghs_list:
            pprint(p.content)
            print "Paragrapgh offset %d, length %d" %(p.offset, p.length)
            print "is table? " , is_table(p.content)
            print'\n'*8
    
            

            
            
    
    
        

