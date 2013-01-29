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

def main():
    functions = file('functions').read()
    programma = file('program').read()
    programma = replace_functions(programma, functions)
    if programma.find('(') != -1:
        print 'Er zijn mogelijk onbekende functies gebruikt: %s' % programma
    programma = optimize(programma)
    print programma

if __name__ == '__main__':
    main()