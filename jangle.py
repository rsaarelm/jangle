#!/usr/bin/env python3
import re
import sys
import subprocess

# Indented 7 or more columns, must contain non-whitespace.
CODE = re.compile(r'^\s{7}\S')

# Must have output marker at indentation 4
OUTPUT = re.compile(r'^\s{4}┆ ')

def gensym():
    n = 1
    while True:
        yield "'__PARAGRAPH_BREAK_GENSYM_%s__'" % n
        n += 1

def parse_gensym(line):
    # TODO: Should we do something with the number as well?
    return '__PARAGRAPH_BREAK_GENSYM_' in line

IN_TEXT = 0
IN_CODE = 1
IN_OUTPUT = 2

class Document:
    def __init__(self, lines):
        text = []
        code = []

        # A list of (text, code) pairs that catenate to the original document.
        self.data = []

        state = IN_TEXT
        previous_line_prevents_code_mode = False

        for line in lines:
            if state == IN_TEXT:
                if CODE.match(line) and not previous_line_prevents_code_mode:
                    state = IN_CODE
                    code = [line.rstrip()]
                else:
                    text.append(line.rstrip())
            elif state == IN_CODE:
                if OUTPUT.match(line):
                    # Start eating the output
                    state = IN_OUTPUT
                elif CODE.match(line):
                    code.append(line.rstrip())
                else:
                    state = IN_TEXT
                    self.data.append((text, code))
                    text, code = [line.rstrip()], []
            else:
                if OUTPUT.match(line):
                    continue
                elif CODE.match(line):
                    state = IN_CODE
                    self.data.append((text, code))
                    text, code = [], [line.rstrip()]
                else:
                    state = IN_TEXT
                    self.data.append((text, code))
                    text, code = [line.rstrip()], []

            # Can't switch to code mode immediately after a non-empty,
            # non-code, non-output line. This is to prevent accidental shifts
            # to code mode in middle of some other verbatim text that includes
            # a bit indented by 3 columns.
            previous_line_prevents_code_mode = \
                    state == IN_TEXT and \
                    not OUTPUT.match(line) and \
                    line.strip()

        if text or code:
            self.data.append((text, code))

    def tangle(self):
        """Produce executable J script."""
        lines = []
        g = gensym()
        for (text, code) in self.data:
            lines.extend(code)
            # A nasty hack to eat away the prompt lines
            if lines[-1].strip() != ')':
                # Last line isn't the end multiline declaration marker, so
                # assume it's an expression that prints something. Add the
                # empty echo before it to clean up prompt noise from any
                # definition lines before the last one.
                lines.insert(-1, "echo ''")
            lines.append(next(g))
        return '\n'.join(lines)

    def weave(self, script_output):
        """Create a new document from the original and the script output."""
        lines = []
        output_chunks = [[]]
        for line in script_output.splitlines():
            if not line.strip():
                continue
            if parse_gensym(line):
                output_chunks.append([])
            else:
                # The first output line will have the three input lines for
                # the interactive prompt printed to it, these need to be
                # removed.
                #
                # XXX: If the input chunk had multiple output-printing lines
                # in it, multiple prompt prefixes will be printed, and Jangle
                # isn't smart enough to remove the subsequent ones.
                if not len(output_chunks[-1]) and line.startswith('   '):
                    line = line[3:]
                line = '┆ ' + line.rstrip()
                output_chunks[-1].append('    '+line)

        for (i, (text, code)) in enumerate(self.data):
            lines.extend(text)
            lines.extend(code)
            if i < len(output_chunks):
                lines.extend(output_chunks[i])
        return '\n'.join(lines)

    def __str__(self):
        lines = []
        for (text, code) in self.data:
            lines.extend(text)
            lines.extend(code)
        return '\n'.join(lines)


def execute(source):
    p = subprocess.Popen(
            ('/usr/bin/env', 'jconsole'),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    return str(p.communicate(bytes(source, 'utf-8'))[0], 'utf-8')


if __name__=='__main__':
    doc = Document(sys.stdin)
    print(doc.weave(execute(doc.tangle())))
