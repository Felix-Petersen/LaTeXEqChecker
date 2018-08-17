#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Latex equation check

Checks math equations etc. in LaTeX documents and annotates correctness.

"""

__author__      = "Felix Petersen"
__copyright__   = "Copyright 2017, Felix Petersen"
# __license__     = ""
__version__     = "2017.12.28"
__email__       = "mail@felix-petersen.de"
__status__      = "Production"


import sys, os, re
import argparse


header_comment = "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n" \
                 "%% Annotated by texEqCheck.py     Version: 23.11.2017         %%\n" \
                 "%%                                                            %%\n" \
                 "%% texEqCheck by Felix Petersen                               %%\n" \
                 "%% Copyright (c) 2017 Felix Petersen. All rights reserved.    %%\n" \
                 "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"


def check_equation(query, lets):
    if args.wolfram_alpha:
        return wa.wa_query(query, lets)
    elif args.sympy:
        return sp.sympy_query(query, lets)
    return 'None'


if __name__ == '__main__':

    sys.setrecursionlimit(10000)

    # Parsing the arguments:
    parser = argparse.ArgumentParser(description='This program checks math equations etc. in LaTeX documents and annotates correctness.\n'
                                                 '\n'
                                                 'Two use case examples:\n'
                                                 '`../LaTeXEqChecker/texEqCheck.py -sp -stat -mirror -f mgi/`\n'
                                                 '`../LaTeXEqChecker/texEqCheck.py -wa -l -o corrected-file.tex file.tex`\n',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_file_dir', help='input file name (or any file of the directory if every TeX file of the folder should be checked)', type=str)
    parser.add_argument('-o', '--output', help='output file name (if every TeX file of a folder is checked, the results will be saved in ./texEqCheck/*.tex)', type=str)
    parser.add_argument('-f', '--folder', help='check for every *.tex file in the directory (not recursively); save results in ./texEqCheck/*.tex', action="store_true", default=False)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    parser.add_argument('-say', '--say', help='let the program tell if it has finished (using `say` command)', action="store_true", default=False)
    parser.add_argument('-wa', '--wolfram_alpha', help='use WolframAlpha for the correction', action="store_true", default=False)
    parser.add_argument('-sp', '--sympy', help='use SymPy for the correction', action="store_true", default=False)
    parser.add_argument('-l', '--lets', help='[WolframAlpha only] consider previous equations as definitions', action="store_true", default=False)
    parser.add_argument('-ans', '--wolfram_alpha_results', help='[WolframAlpha only] define a file to store / reuse the results from the WolframAlpha API', type=str)
    parser.add_argument('-num', '--test_numerical', help='[SymPy only] test the equations numerical, too', action="store_true", default=False)
    parser.add_argument('-mirror', '--mirror_interpretation', help='[SymPy only] show the interpretation of the formulae backconverted to LaTeX behind the formula, too', action="store_true", default=False)
    parser.add_argument('-wait', '--wait_for_output', help='wait for the user to press [Enter] before writing / outputting the result', action="store_true", default=False)
    parser.add_argument('-gui', '--gui', help='start the GUI (also possible using `./texEqCheck.py GUI`)', action="store_true", default=False)
    parser.add_argument('-stat', '--statistics', help='print out statistics about the results (how many equations could be checked, etc.)', action="store_true", default=False)
    args = parser.parse_args()

    import src

    # If user types "GUI" instead of the input file name, the GUI opens:
    if (args.input_file_dir.lower() == 'gui'):
        args.gui = True
        args.input_file_dir = ''

    # GUI:
    if args.gui:
        master = src.gui.tk.Tk()

        gui = src.gui.GUI(master, args)

        src.gui.tk.mainloop()

    files = {}

    if args.folder:
        dirname = os.path.dirname('./' + args.input_file_dir)
        print(dirname)
        if not os.path.exists(dirname + '/texEqCheck/'):
            os.makedirs(dirname + '/texEqCheck/')
        for file in os.listdir(dirname):
            if file[-4:] == '.tex' and file.find('_py') == -1:
                # exclude if '_py' in filename because it has been used before
                files[dirname + '/' + file] = dirname + '/texEqCheck/' + file
    else:
        files[args.input_file_dir] = args.output

    for file in files:
        args.input_file_dir = file
        args.output = files[file]

        # Checker initialization (because `args` is required)
        wa = src.wa.WA(args)
        sp = src.sympy.SP(args)

        # Check whether the input file is correct:
        file_dir = "./" + args.input_file_dir
        if os.path.isfile(file_dir):
            print("File \"" + file_dir + "\" exists.")
        else:
            print("File ", file_dir, " does not exist! Please enter a correct file.")
            sys.exit(1)

        # Read the input file:
        content = open(file_dir, 'r').read()
        original_content_length = len(content)

        # Ensure that the file has not been annotated yet.
        if header_comment in content:
            print("Document ", file_dir, " has already been corrected. Please use a not yet annotated document.")
            sys.exit(1)

        # Info output:
        print("The autor of this TeX file is " + src.helper.get_author(content) + ".")

        # Parses the document down to the math modes with top-down approach
        latex_document = src.objects.LaTeXDocument(content, args, check_equation)

        # Executes the correction
        latex_document.work_on_mathmodes()

        # Takes the modified document back
        content = header_comment + str(latex_document)

        # Info output:
        print("\nDuring processing the length of the TeX file changed from " + str(original_content_length) + " bytes to " + str(len(content)) + " bytes.")

        # wait for the user to press [Enter] before writing / outputting the result
        if args.wait_for_output:
            input("Press ENTER key to finish... (output, etc.)")

        # Output - either per standard output or writing to file:
        if args.output:
            output_file = open("./" + args.output, "w")
            output_file.write(content)
        else:
            print("\n\n    OUTPUT:\n\n\n")
            print(content)

    # Resume:
    print(str(len(files)) + " files have been corrected.\n")

    # Statistics about the results
    if args.statistics:
        print("Here are some statistics about the results:")
        print(src.objects.Equation.results_dict)
        sum = 0
        for key in src.objects.Equation.results_dict:
            sum += src.objects.Equation.results_dict[key]
        if 'True' in src.objects.Equation.results_dict and 'False' in src.objects.Equation.results_dict:
            print( str(src.objects.Equation.results_dict['True'] + src.objects.Equation.results_dict['False'])
                   + " of "
                   + str(sum)
                   + " equations could be checked." )
            print( str(src.objects.Equation.results_dict['True'])
                   + " of these "
                   + str(src.objects.Equation.results_dict['True'] + src.objects.Equation.results_dict['False'])
                   + " equations equations are true." )
        if 'Parentheses Error' in src.objects.Equation.results_dict:
            print(str(src.objects.Equation.results_dict['Parentheses Error'])
                  + " of "
                  + str(sum)
                  + " equations had a parentheses error.")

    if args.say:
        os.system('say "equation checker has finished"')
