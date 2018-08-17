#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Felix Petersen"
__status__      = "Production"


import re
from src.helper import get_as_long_as_correct_parentheses_from_right, get_as_long_as_correct_parentheses_from_left


def query_replacer(input):
    """
    Removes not semantically wanted commands of LaTeX math code.
    
    :param input: LaTeX math code
    :return: 
    """
    return input.replace('\\\\', '').replace('\\quad', ' ').replace('\\qquad', ' ').replace('&', '').replace('\n', '')\
        .replace('~', ' ').replace(r'\ ', ' ').replace('   ', ' ').replace('  ', ' ').replace('\\equiv', '=')


class Equation:
    """
    Equation class.
    
    Stores one equation with:
    - presentation
    - content
    - interpretation
    
    Further it stores a reference to the lets.
    
    The Equation can be checked by calling `compute_result`.
    After that the comparator can be printed including the result.
    """

    # For statistics purposes:
    results_dict = {}

    def __init__(self, left_presentation, right_presentation, left_content, right_content, comparator, lets, check_equation):
        """
        Initializer of the Equation.
        
        :param left_presentation: 
        :param right_presentation: 
        :param left_content: 
        :param right_content: 
        :param comparator: 
        :param lets: 
        :param check_equation: 
        """

        self.left_presentation = left_presentation
        self.right_presentation = right_presentation
        self.comparator = Comparator(comparator)
        self.lets = lets
        self.res = ''
        self.interpretation_of_equation_to_latex = ''

        self.check_equation = check_equation

        self.left_content = get_as_long_as_correct_parentheses_from_right(left_content)
        self.right_content = get_as_long_as_correct_parentheses_from_left(right_content)


    def __str__(self):
        """
        The string is the "content" string. (There can be parts missing which would be in the presentation)
        
        The string can be used e.g. for a WA API call.
        
        :return: 
        """
        return self.left_content + str(self.comparator) + self.right_content

    def compute_result(self):
        """
        Computes and saves the result of the check using `check_equation`.
        """
        if self.left_content.replace(' ', '') != '' and self.right_content.replace(' ', '') != '':
            self.res = self.check_equation(query=self, lets=self.lets)
        else:
            self.res = 'Parentheses Error'
        # For statistics purposes:
        if self.res in Equation.results_dict:
            Equation.results_dict[self.res] += 1
        else:
            Equation.results_dict[self.res] = 1

    def get_result_comparator(self):
        """
        Prints the comparator including the result as a string.
        
        This is done by unsing 'overset' to place the annotation above the equation.
        
        :return: comparator including the result
        """
        result_comparator = r'\overset{'
        if self.res.find("True") != -1:
            result_comparator += r'\text{\color{green}\cmark}'
        if self.res.find("False") != -1:
            result_comparator += r'\text{\color{red}\xmark}'
        if self.res.find("None") != -1:
            result_comparator += r'\text{\color{orange}?~}'
        if self.res.find("new") != -1:
            result_comparator += r'\text{\color{blue} def}'
        if self.res.replace("True", '').replace('False', '').replace('new', '').replace('None', '').replace(' ', '') != '':
            result_comparator += r'\text{' + self.res.replace("True", '').replace('False', '').replace('new', '').replace('None', '') + r'}'


        # # If None is inside res but "None" != res
        # elif self.res.find("None") != -1:
        #     if len(self.res) > 32:
        #         # res = r'\footnote{' + res + r'}'
        #         res = self.res[:32]
        #     result_comparator += r'\text{\color{orange}?~' + self.res + r'}'

        result_comparator += '}{' + str(self.comparator) + r'}'

        return result_comparator

    def is_used(self):
        """
        If the by the Equation generated Let has been used, it adds the "new" tag to the annotation.

        :return: 
        """
        self.res += ' new'


class Let:
    """
    Let class.
    
    Stores lets by storing the left and right side, as well as the operator between them.
    
    The left side should prefered to be shorter and should be the variable.
    E.g. rather `i := 10' than '10 := 1'
    """

    def __init__(self, left, right, between, is_used):
        """
        Initializer of the Let.
        
        :param left: left side of the Let (the variable that should be defined)
        :param right: definition of the variable
        :param between: operator for the definition (usually ':=' resp. '=')
        """
        self.left = left
        self.right = right
        self.between = between
        self.is_used = is_used

    def __str__(self):
        """
        The Let printed as string.
        
        :return: 
        """
        return self.left + ' ' + str(self.between) + ' ' + self.right


class Comparator:
    """
    Comparator class.
    
    Stores a comparator and allows the check if the application of two values to the comparator is valid.
    """
    def __init__(self, comparator):
        if comparator in ['=', '\\equiv', '\\neq', '\\leq', '\\geq', '<', '>', ':=', '=:']: # not:
            self.comparator = comparator
        else:
            raise ValueError('non-valid comparator"' + comparator + '"')

    def __str__(self):

        return self.comparator

    def is_valid(self, left_op_right, op_neutral):
        if self.comparator == '=':
            return left_op_right == op_neutral
        elif self.comparator == '\\equiv':
            return left_op_right == op_neutral
        elif self.comparator == '\\neq':
            return left_op_right != op_neutral
        elif self.comparator == '\\geq':
            return left_op_right >= op_neutral
        elif self.comparator == '\\leq':
            return left_op_right <= op_neutral
        elif self.comparator == '<':
            return left_op_right < op_neutral
        elif self.comparator == '>':
            return left_op_right > op_neutral
        raise ValueError('non-valid comparator"' + self.comparator + '"')

    def is_valid_sub(self, left_minus_right):
        return self.is_valid(left_minus_right, 0)

    def is_valid_div(self, left_divided_by_right):
        return self.is_valid(left_divided_by_right, 1)


class LaTeXTreeNode:
    """
    LaTeXTreeNode class.
    
    Node for the tree representing the LaTeX file.
    """
    def __init__(self, name, type, list, **kwargs):
        self.name = name
        self.type = type
        self.list = []
        for elem in list:
            self.list.append( elem )
        if 'lets' in kwargs:
            self.lets = kwargs['lets']

    def get_list_elem(self, n):
        return self.list[n]

    def set_list_elem(self, elem, n):
        self.list[n] = elem

    def append_list_elem(self, elem):
        self.list.append( elem )
        return len(self.list)

    def __str__(self):
        string = ''
        for elem in self.list:
            string += str(elem)
        return string

    def do_for_every(self, fun):
        temp_list = []
        for elem in self.list:
            temp_list.append(fun(elem))
        self.list = temp_list


class LaTeXTreeLeaf:
    """
    LaTeXTreeLeaf class.
    
    Leaf for the tree representing the LaTeX file.
    """
    def __init__(self, name, type, content):
        self.name = name
        self.type = type
        self.content = content

    def __str__(self):
        return str(self.content)


class LaTeXMathmode:
    """
    LaTeXMathmode class.
    
    Represents and saves a LaTeX mathmode incl.:
    - begin-splitter
    - end-splitter
    - content
    - list of the equations as Equations
    
    All equations can be checked using `checkEquations`.
    """
    def __init__(self, args, begin, end, content, lets, check_equation):
        self.args = args
        self.begin = begin
        self.content = content
        self.equations = []
        self.end = end

        last_part = ''
        last_parts = ''
        delimiters = r'(=)|(\\equiv)|(\\neq)|(\\geq)|(\\leq)|(:=)|(=:)|(<)|(>)'  # needs to be double-escaped because of use in re.split()
        search_begin = 0
        match = None
        while re.search(delimiters, self.content[search_begin:]) != None:
            match = re.search(delimiters, self.content[search_begin:])
            next_match = re.search(delimiters, self.content[search_begin + match.end():])
            next_start = 0
            if next_match:
                next_start = search_begin + next_match.start()
            else:
                next_start = len(self.content)

            eq = Equation(self.content[search_begin:search_begin + match.start()], self.content[search_begin + match.end():next_start], # presentation
                          self.content[            :search_begin + match.start()], self.content[search_begin + match.end():          ], # content
                          self.content[search_begin + match.start():search_begin + match.end()], # comparator
                          lets, check_equation)

            self.equations.append(eq)

            search_begin += match.end()

    def __str__(self):
        equations = ''
        if len(self.equations):
            for equation in self.equations:
                equations += equation.left_presentation + equation.get_result_comparator()
            equations += self.equations[-1].right_presentation
        else:
            equations += self.content
        if not self.args.mirror_interpretation:
            return self.begin + equations + self.end
        else:
            # show the interpretation of the formulae backconverted to LaTeX behind the formula, too
            interpretations = ''
            for equation in self.equations:
                if equation.interpretation_of_equation_to_latex:
                    interpretations += r' $$' + equation.interpretation_of_equation_to_latex + r'$$ '
            return self.begin + equations + self.end + interpretations

    def checkEquations(self):
        for eq in self.equations:
            eq.compute_result()


class LaTeXDocument:
    """
    LaTeXDocument class.
    
    Class for storing and operating on a whole LaTeX document.
    
    Represents and saves a LaTeX document incl.:
    - header
    - tail
    - content as a tree of "LaTeXTreeNode"
    """
    def __init__(self, content, args, check_equation):
        """
        Constructor of LaTeXDocument.
        Includes the splitting of the content into a tree.
        
        :param content: Content of the original LaTeX document
        :param args: argsparsers args
        """
        import src.helper
        self.args = args

        def removeComments(string):
            res = ""
            regex = r"(?<!\\)%"
            for line in string.split("\n"):
                if len(re.split(regex, line)) > 1:
                    if re.split(regex, line)[0].strip() != '':
                        res += re.split(regex, line)[0] + '\n'
                else:
                    res += line + '\n'
            return res

        def replaceDollar(string):
            # Special case of '\$' should be ignored for getting mathmodes
            string = re.sub(re.compile(r"([^\\])\\\$"), r"\1\\textdollar{}", string)
            return string

        content = replaceDollar( removeComments( content ) )

        split_document = src.helper.split_content_of_first_occurence("\\begin{document}", "\\end{document}", content)
        self.head = split_document[0].split("\\begin{document}")[0] + '\n' \
                    + r'\usepackage{pifont}% http://ctan.org/pkg/pifont' + '\n' \
                    + r'\newcommand{\cmark}{\ding{51}}%' + '\n' \
                    + r'\newcommand{\xmark}{\ding{55}}%' + '\n' \
                    + r'\usepackage{color}' + '\n' \
                    + r'\usepackage{xcolor}' + '\n\n' \
                    + "\\begin{document}"
        self.main = split_document[1]
        self.tail = split_document[2]

        # Split into different namespaces using following splitters:
        namespace_splitters = ['chapter', 'section', 'subsection']
        # '$$' is here before '$' in order to preserve the order:
        mathmode_splitters = {'$$' : '$$', '$' : '$', r'\(' : r'\)', r'\[' : r'\]',
                              r'\begin{equation}' : r'\end{equation}', r'\begin{equation*}' : r'\end{equation*}',
                              r'\begin{align}' : r'\end{align}', r'\begin{align*}' : r'\end{align*}',
                              r'\begin{multline}' : r'\end{multline}', r'\begin{multline*}' : r'\end{multline*}'}

        mathmode_splitters_list = []
        for mathmode_splitter in mathmode_splitters:
            mathmode_splitters_list.append(mathmode_splitter)
            mathmode_splitters_list.append(mathmode_splitters[mathmode_splitter])


        self.tree = LaTeXTreeNode('', 'main', [])

        index_namespace = 0
        for namespace in src.helper.split_at_every_splitter_latex(self.main, namespace_splitters):
            if index_namespace % 2 == 0:
                type = 'namespace'
            else:
                type = 'splitter'
            self.tree.append_list_elem(LaTeXTreeLeaf('', type, namespace))
            index_namespace += 1

        def namespace_to_text_and_math(leaf):
            # Helper function
            if leaf.type == 'namespace':
                lets = []
                node = LaTeXTreeNode('', 'namespace', [], lets=lets)
                is_mathmode_that_began_with = ''
                current_math = ''
                for mathmode_or_text in src.helper.split_at_every_splitter(str(leaf), mathmode_splitters_list):
                    # Get the mathmodes with both correct begin and correct end and the content as LaTeXMathmodes and the texts between them as strings:
                    if is_mathmode_that_began_with:
                        if mathmode_splitters[is_mathmode_that_began_with] == mathmode_or_text:
                            mathmode = LaTeXMathmode(self.args, is_mathmode_that_began_with, mathmode_splitters[is_mathmode_that_began_with], current_math, lets, check_equation)
                            node.append_list_elem(LaTeXTreeLeaf('', 'mathmode', mathmode))
                            is_mathmode_that_began_with = ''
                            current_math = ''
                        else:
                            if not current_math:
                                current_math = mathmode_or_text
                            else:
                                current_math += mathmode_or_text
                                # raise Exception('there is a foreign splitter within a mathmode')
                    else:
                        if mathmode_or_text in mathmode_splitters:
                            is_mathmode_that_began_with = mathmode_or_text
                        else:
                            node.append_list_elem(LaTeXTreeLeaf('', 'text', mathmode_or_text))

                return node
            else:
                return leaf

        self.tree.do_for_every(namespace_to_text_and_math)

    def __str__(self):
        """
        Converts the LaTeXDocument to a string by concatenating
        
        :return: concatenated string
        """
        return self.head + str(self.tree) + self.tail

    def work_on_mathmodes(self):
        def fun2(node):
            # lets = []
            def work_on_mathmode_incl_lets(mathmode):
                if mathmode.type == 'mathmode':
                    mathmode.content.checkEquations()
                return mathmode
            if node.type == 'namespace':
                node.do_for_every(work_on_mathmode_incl_lets)
            return node

        self.tree.do_for_every(fun2)

    def do_for_every_leaf_with_type(self, fun, type):
        def fun2(node):
            # Applies @fun on every child if the node has type @type
            if node.type == type:
                node.do_for_every(fun)
            return node

        self.tree.do_for_every(fun2)
