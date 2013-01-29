#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT
from shlex import split

pre_code = '''#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int tape_len = 1;
int tape_pos = 0;
int *tape = NULL;

void main(int argc, char **argv)
{
    tape = malloc(sizeof(int));
    '''

post_code = '''
    if(argc > 1 && ((strcmp(argv[1], "-t") == 0) || (strcmp(argv[1], "--tape") == 0)))
    {
        printf("\\nTape: [");
        int i;
        for(i = 0; i < tape_len; i++)
        {   
            printf("%d, ", tape[i]);
        }   
        printf("]\\n");
    }
}'''

def replace_function(programma, name, args, code):
    eerste = programma.find(name + "(")
    if eerste == -1:
        return programma
    laatste = eerste + len(name) + 1
    depth = 1
    argvals = []
    argval = ""
    while depth != 0:
        if programma[laatste] == ')':
            depth -= 1
        elif programma[laatste] == '(':
            depth += 1
        if programma[laatste] == ',' and depth == 1:
            argvals.append(argval)
            argval = ""
        elif depth != 0:
            argval += programma[laatste]
        laatste += 1
    argvals.append(argval)
    if len(args) == 0 and len(argvals) == 1:
        argvals = []
    assert len(args) == len(argvals)
    zoek = programma[eerste:(laatste)]
    i = 0
    while i < len(args):
        code = code.replace(args[i], argvals[i])
        i += 1
    return programma.replace(zoek, code)

def replace_functions(programma, functions):
    functions = functions.replace("\n", "")
    functions = functions.split("----")
    replaced = True
    while replaced:
        prog_old = programma
        for function in functions:
            function = function.split('====')
            name = ""
            args = []
            code = ""
            if len(function) == 2:
                name = function[0]
                code = function[1]
            elif len(function) == 3:
                name = function[0]
                code = function[2]
            elif len(function) == 4:
                name = function[0]
                args = function[1].split(",")
                code = function[3]
            name = name.replace(" ", "")
            if name != "":
                programma = replace_function(programma, name, args, code)
        replaced = prog_old != programma
    return programma

def optimize(programma):
    replaced = True
    while replaced:
        prog_old = programma
        programma = programma.replace("><", "")
        programma = programma.replace("<>", "")
        programma = programma.replace("+-", "")
        programma = programma.replace("-+", "")
        for char in programma:
            if not char in ['+', '-', '<', '>', '.', ',', '[', ']']:
                programma = programma.replace(char, "")
        replaced = prog_old != programma
    return programma

def compileer(programma):
    nieuw = pre_code
    for char in programma:
        if char == '-':
            nieuw += 'tape[tape_pos]--;'
        elif char == '+':
            nieuw += 'tape[tape_pos]++;'
        elif char == '<':
            nieuw += 'tape_pos--; assert(tape_pos >= 0);'
        elif char == '>':
            nieuw += 'tape_pos++; if(tape_pos >= tape_len){tape = realloc(tape, sizeof(int) * tape_pos); tape_len++;};'
        elif char == '[':
            nieuw += 'while(tape[tape_pos]){'
        elif char == ']':
            nieuw += '};'
        elif char == ',':
            nieuw += 'tape[tape_pos] = fgetc(stdin)-48;'
        elif char == '.':
            nieuw += 'printf("%d", tape[tape_pos]);'
    nieuw += post_code
    return nieuw

def compileer_c(programma, cc='gcc'):
    return Popen(split('gcc -xc -o /dev/stdout -'), stdout=PIPE, stdin=PIPE).communicate(input=programma)[0]

def run(input, output, no_optimize, no_compile, no_assemble):
    if output == None:
        output = 'a.out'
    inputf = file(input)
    inputr = inputf.read().split("////")
    if output == '-':
        outputf = sys.stdout
    else:
        outputf = file(output, 'w')
    functions = ""
    programma = ""
    if len(input) == 1:
        programma = inputr[0]
    else:
        functions = inputr[0]
        programma = inputr[1]
    inputf.close()
    programma = replace_functions(programma, functions)
    if programma.find('(') != -1:
        print 'There may have been used undefined functions: %s' % programma
    if not no_optimize:
        programma = optimize(programma)
    if not no_compile:
        programma = compileer(programma)
        if not no_assemble:
            programma = compileer_c(programma)
    outputf.write(programma)
    outputf.close()

def parse_args():
    parser = ArgumentParser(description='Compile Enhanced BrainF*ck')
    parser.add_argument('input', help='The input file')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('-no', '--no-optimize', help='Disable BF optimization', action='store_true')
    parser.add_argument('-nc', '--no-compile', help='Do not compile to C', action='store_true')
    parser.add_argument('-na', '--no-assemble', help='Do not compile to machine code', action='store_true')
    result = parser.parse_args()
    return result

if __name__ == '__main__':
    args = parse_args()
    run(args.input, args.output, args.no_optimize, args.no_compile, args.no_assemble)
