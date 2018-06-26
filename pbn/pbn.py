# -*- coding: latin-1 -*-

# pbn
# (joshuah@alum.mit.edu)

# Solves (as much as it can) "paint by numbers" puzzles downloaded from
# http://webpbn.com/.

from collections import namedtuple


Segment = namedtuple('Segment', 'length, color')

# a CELL is a set of colors possible
# a SEGMENT is a pair (length, color)
# [color goes 0, 1, 2, ... where 0 is white]
# this function will return a new `cells`
# it should be idempotent tho!
def solve_row(cells, segments):
    new_cells = [set() for _ in xrange(len(cells))]
    solve_row_starting_with(new_cells, cells, segments, 0, [])
    return new_cells

def solve_row_starting_with(new_cells, cells, segments, cell_idx, segment_positions):
    if len(segment_positions) == len(segments):
        if not all(0 in cells[i]
                   for i in xrange(cell_idx, len(cells))):
            # Not a valid way to end the positions.
            return

        # We found a full set of segment positions! Record this in new_cells
        last_position = 0
        for segment, segment_position in zip(segments, segment_positions):
            for i in xrange(last_position, segment_position):
                new_cells[i].add(0)
            for i in xrange(segment_position, segment_position + segment.length):
                new_cells[i].add(segment.color)
            last_position = segment_position + segment.length
        for i in xrange(last_position, len(cells)):
            new_cells[i].add(0)
        return

    next_segment = segments[len(segment_positions)]

    if cell_idx > len(cells) - next_segment.length:
        # We ran out of cells! Give up
        return

    # Two options:

    # 1. Place the segment here
    if all(next_segment.color in cells[i]
           for i in xrange(cell_idx, cell_idx + next_segment.length)):
        solve_row_starting_with(new_cells, cells, segments,
                                cell_idx + next_segment.length, segment_positions + [cell_idx])

    # 2. Make this cell white and move to the next cell
    if 0 in cells[cell_idx]:
        solve_row_starting_with(new_cells, cells, segments, cell_idx + 1, segment_positions)

def solve_rows(cells, row_clues):
    width, height = len(cells[0]), len(cells)
    new_cells = [[None for _ in xrange(width)] for _ in xrange(height)]
    for i in range(height):
        solved = solve_row(cells[i], row_clues[i])
        for j in range(width):
            new_cells[i][j] = solved[j]
    return new_cells

def solve_columns(cells, column_clues):
    width, height = len(cells[0]), len(cells)
    new_cells = [[None for _ in xrange(width)] for _ in xrange(height)]
    for j in range(width):
        solved = solve_row([cells[i][j] for i in range(height)], column_clues[j])
        for i in range(height):
            new_cells[i][j] = solved[i]
    return new_cells


import requests
import requests_cache
import xml.etree.ElementTree as ET

requests_cache.install_cache("requests_cache")

doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=543').text)  # EASY
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=44').text)  # EASY
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=44').text)  # EASY
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=152').text)  # MEDIUM
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=29').text)  # HARD
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=189').text)  # HARD
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=130').text)  # HARD
# doc = ET.fromstring(requests.get('http://webpbn.com/XMLpuz.cgi?id=140').text)  # HARD

default_color = None
color_to_index = {}
for i, color_elem in enumerate(doc.find('puzzle').findall('color')):
    color = color_elem.attrib['name']
    if default_color == None and i != 0: default_color = color
    color_to_index[color] = i

clues = {}
for clue_elem in doc.find('puzzle').findall('clues'):
    lines = []
    for line_elem in clue_elem.findall('line'):
        segments = []
        for count_elem in line_elem.findall('count'):
            color = count_elem.attrib.get('color') or default_color
            segments.append(Segment(
                int(count_elem.text),
                color_to_index[color]))
        lines.append(segments)
    clues[clue_elem.attrib['type']] = lines

width = len(clues['columns'])
height = len(clues['rows'])

cells = [[set(range(len(color_to_index))) for _ in range(width)] for _ in range(height)]

import sys

def print_row(data, start, middle, middle_break, end):
    sys.stdout.write(start)
    for j, d in enumerate(data):
        if j % 5 == 0 and j > 0:
            sys.stdout.write(middle_break)
        if callable(middle):
            sys.stdout.write(middle(d))
        else:
            sys.stdout.write(middle)
    sys.stdout.write(end)
    sys.stdout.write('\n')

def print_cells():
    # Top border
    print_row(range(width), '┏','━','┯','┓')
    # Body
    for i, row in enumerate(cells):
        if i % 5 == 0 and i > 0:
            print_row(row, '┠','─','┼','┨')
        print_row(row, '┃',lambda cell: str(next(iter(cell))) if len(cell) == 1 else ' ','│','┃')
    print_row(range(width), '┗','━','┷','┛')

    sys.stdout.flush()

for _ in range(30):
    old_cells = cells

    print "Solving rows"
    cells = solve_rows(cells, clues['rows'])
    print_cells()

    print "Solving columns"
    cells = solve_columns(cells, clues['columns'])
    print_cells()

    if old_cells == cells:
        print "Solving has converged"
        break
