#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Felix Petersen"
__status__      = "Production"


import src.latex2sympy.process_latex as latex2sympy
import src.objects
import sympy
import random

class SP:
    """
    Sympy helper class
    """

    def __init__(self, args):
        """
        Initializer of the Sympy helper class.
        
        :param args: `args`
        """
        self.args = args

    def test_sympy_simplify(self, left, right, comparator):
        sub = comparator.is_valid_sub(sympy.simplify(left-right))
        if sympy.simplify(right) != 0:
            div = comparator.is_valid_div(sympy.simplify(left/right))
        else:
            div = sub
        return sub, div

    def test_sympy_numerical(self, left, right, comparator):
        left_symbols = left.free_symbols
        right_symbols = right.free_symbols
        symbols = left_symbols | right_symbols
        n_true = 0
        n_false = 0
        if self.args.verbose:
            print("Symbols in numerical test: " + symbols)
        for sign in [-1, 1]:
            for integer in range(20):
                substitutions = []
                for symbol in symbols:
                    value = (integer/2)**(random.uniform(0, 10)) * sign
                    substitutions.append((symbol, value))
                if self.test_sympy_simplify(left.subs(substitutions), right.subs(substitutions), comparator)[0]: # Use only the `sub'
                    n_true += 1
                else:
                    n_false += 1
        if self.args.verbose:
            print("True tests:  " + str(n_true))
            print("False tests: " + str(n_false))
        return n_true/(n_true + n_false)

    def sympy_query(self, query, lets):

        # Remove irrelevant commands (it is here because else it would be conflicting the matrix translation for WA)
        query.left_content = src.objects.query_replacer(query.left_content)
        query.right_content = src.objects.query_replacer(query.right_content)

        if '\\infty' in str(query):
            return 'None'

        if self.args.verbose:
            print((str(query)))
        try:
            left = latex2sympy.process_sympy(query.left_content)
            right = latex2sympy.process_sympy(query.right_content)

            query.interpretation_of_equation_to_latex = sympy.latex(left) + ' ' + str(query.comparator) + ' ' + sympy.latex(right)

            if ':' in str(query.comparator):
                return 'new'

            # Simplification tests:
            sub, div = self.test_sympy_simplify(left, right, query.comparator)
            if sub == div:
                if sub:
                    res = 'True'
                else:
                    res = 'False'
            else:
                res = 'sub and div different'

            # Numerical tests:
            if self.args.test_numerical:
                numerical = self.test_sympy_numerical(left, right, query.comparator)
                if numerical == 0:
                    res += ' False'
                elif numerical == 1:
                    res += ' True'
                else:
                    res += ' ' + str(numerical)

            return res
        except Exception as e:

            print('There was the following exception: ' + str(e))
            print('')
            return 'None'