Notebook evaluator for J programming language

Write J expressions with exactly seven columns of indentation (4 to get you to
the Markdown code literal block, and 3 more to match the J repl convention):

       'Hello, world!'
    ┆ Hello, world!
        o. 1
    ┆ 3.14159

When you pipe your file through Jangle, the output shows up right below the
input:

       *table~ i.6
    ┆ ┌─┬───────────────┐
    ┆ │*│0 1  2  3  4  5│
    ┆ ├─┼───────────────┤
    ┆ │0│0 0  0  0  0  0│
    ┆ │1│0 1  2  3  4  5│
    ┆ │2│0 2  4  6  8 10│
    ┆ │3│0 3  6  9 12 15│
    ┆ │4│0 4  8 12 16 20│
    ┆ │5│0 5 10 15 20 25│
    ┆ └─┴───────────────┘

To be parsed as a J expression, the line should be separated by empty lines.
Regular blocks of verbatim text that happen to have a line indented 7 columns
in the middle do not get converted:

    # A non-notebook source code example
    def func(a, b):
       return a * b

All consecutive non-whitespace lines indented at 4 columns and starting with
the special marker character will be considered generated output and will be
deleted at the next Jangle run.

Vim shortcut for formatting a file (assuming you have jangle.py in your path):

    :%!jangle.py

Command-line use:

    jangle.py < input.txt > output.txt

You can do in-place replacement with

    jangle.py < document.txt | sponge document.txt

# Bugs

If a script block has more than one output-producing expression, the
subsequent expressions will be misaligned due to the J interpreter printing
input prompt indentations to stdout when it's run. There is a workaround for
this, but it only handles output emitted by the last line of a script block.
Until this is fixed, script blocks need to be written so that only the last
line emits output.
