#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Felix Petersen"
__status__      = "Production"


import wolframalpha
appid = 'W536E7-TAGL5UQE8E'#mail@
# appid = '83RUHP-RQ2E2R3E65'#@uni-konstanz.de
# U2YPK6-9K5JY5YK6Y#mathematica
waclient = wolframalpha.Client(app_id=appid)

# Use unverified:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import src.helper


def is_latex_command(pos, text):
    """
    Check by going to the left if the word at the position is a \LaTeX command. (LaTeX commands begin with '\')
    
    :param pos: position to be checked
    :param text: text in which it should be checked
    :return: True or False
    """
    while pos >= 0:
        if text[pos].isalpha():
            pos -= 1
        elif text[pos] == '\\':
            return True
        else:
            return False
    return False


def alpha_len(text):
    """
    Alphabetic length of the text.
    Count only a-z & A-Z.
    
    :param text: 
    :return: 
    """
    len = 0
    for char in text:
        if char.isalpha():
            len += 1
    return len


def powerset(input, max):
    """
    Returns the powerset of `input` with the constraint, that each subset has max `max` elements.
    
    >>> powerset([1,2,3,4],2)
[[1, 2], [1, 3], [1, 4], [1], [2, 3], [2, 4], [2], [3, 4], [3], [4], []]
    
    :param input: 
    :param max: 
    :return: 
    """
    list = []
    if max > 0:
        if len(input) > 0:
            for subset in powerset(input[1:], max-1):
                list.append([input[0]] + subset)
            for subset in powerset(input[1:], max):
                list.append(subset)
        else:
            list.append([])
    else:
        list.append([])
    return list


class WA:
    """
    WolframAlpha API helper class
    """

    def __init__(self, args):
        """
        Initializer of the WolframAlpha API helper class.
        
        :param args: `args`
        """
        self.args = args

    def consider_as_let(self, query, lets):
        left = query.left_content
        right = query.right_content
        if (left.replace(' ', '') == '') or (right.replace(' ', '') == ''):
            return False
        if (alpha_len(left) == 0 and alpha_len(right) == 0):
            return False
        if (query.comparator == '=') or (query.comparator == '=:'):
            if alpha_len(right) != 0:
                lets.append(src.objects.Let(right.replace(' ', ''), left, query.comparator, query.is_used))
        if alpha_len(left) == 0:
            return False
        lets.append(src.objects.Let(left.replace(' ', ''), right, query.comparator, query.is_used))
        # TODO: consider the lets (\in \exists \forall := (= < >)?)

    def wa_query(self, query, lets):
        """
        Makes a WolframAlpha query call.
        Iff the result is negative it considers the lets.
        
        :param query: Equation object to be checked
        :param lets: List of (Let)s which can be extended and should be considered
        :return: 
        """

        # convert the matrices:
        query.left_content = self.wa_mod_matrix(query.left_content)
        query.right_content = self.wa_mod_matrix(query.right_content)

        # Remove irrelevant commands (it is here because else it would be conflicting the matrix translation for WA)
        query.left_content = src.objects.query_replacer(query.left_content)
        query.right_content = src.objects.query_replacer(query.right_content)

        # Get the result from the API / file
        result = self.wa_query_call(query)

        # Consider lets:
        if self.args.lets:
            if result != 'True':
                # The `max` at powerset defines how many lets should be maximal considered.
                for let_set in powerset(lets, max=2)[:-1]:

                    def lets_in_query():
                        # Checks whether all lets of the subset are in the query and none of them is a command.
                        for let in let_set:
                            if str(query).find(let.left) == -1 or is_latex_command(str(query).find(let.left), str(query)):
                                return False
                        return True

                    if lets_in_query():

                        temp_query = str(query)

                        for let in let_set:
                            temp_query = temp_query.replace(let.left, let.right)

                        result = self.wa_query_call(temp_query)

                        if self.args.verbose:
                            print('\n')
                            for let in let_set:
                                print('Let "'+str(let)+'" found in: '+str(query))
                            print('Lets:')
                            for current_let in lets:
                                print(current_let)
                            print(result)
                        if result == 'False':
                            for let in let_set:
                                let.is_used()
                                lets.remove(let)
                            if str(query.comparator) in ['=', ':=', '=:']:
                                self.consider_as_let(query, lets)
                            break
                        elif result == 'None':
                            # Test others if there was no result... later it will be interpreted...
                            pass
                        elif result == 'True':
                            for let in let_set:
                                let.is_used()
                            break
                        else:
                            break

            if result == 'None' and str(query.comparator) in ['=', ':=', '=:']:
                # TODO: Maybe additional delete a let that has the same left...
                self.consider_as_let(query, lets)

        return result

    def wa_query_call(self, query):
        """
        Checks whether the WolframAlpha query has already been requested and is in the 'args.wolfram_alpha_results' file.

        If not => call to WolframAlpha and write to the 'args.wolfram_alpha_results' file.

        :param query: 
        :return: 
        """
        result = ''
        if self.args.wolfram_alpha_results:
            with open(self.args.wolfram_alpha_results, "r") as file:
                for line in file.readlines():
                    if line.split('!!!')[0] == str(query):
                        result = line.split('!!!')[1].replace('\n', '')
        if result == '':
            result = self.wolframalpha_get_short_plain_result(str(query))
            if self.args.wolfram_alpha_results:
                with open(self.args.wolfram_alpha_results, "a") as file:
                    file.write('\n' + str(query) + '!!!' + result)
        return result

    def wolframalpha_get_short_plain_result(self, query):
        """
        Queries the query from WolframAlpha and interprets + returns the result.
    
        >>> self.wolframalpha_get_short_plain_result(r"{{a,b},{c,d}} ^{-1} =\\frac{1}{ad - bc}{{d,-b},{-c,a}}")
        'True'
        >>> self.wolframalpha_get_short_plain_result(r"{{1,2},{3,4}} = - \\frac{1}{2} {{4,-2},{-3,1}}")
        'False'
    
        :param query: 
        :return: Interpretation of the WolframAlphas APIs result
        """
        try:
            res = waclient.query(query)
        except Exception as e:
            print("Exception at 'waclient.query(query)':", e)
            print("Query =", query)

        result = "None"

        try:
            if res.success == 'true':
                for pod in res.pod:
                    if pod.title == 'Result':
                        for sub in pod.subpods:
                            result = sub.plaintext.replace('^', ' (carret) ').replace('{', '').replace('}', '').replace('\\',
                                                                                                                        'backslash').replace('&', '\\&').replace('_', '\\_')
            else:
                if 'tips' in res:
                    if 'tip' in res['tips']:
                        if '@text' in res['tips']['tip']:
                            result = res['tips']['tip']['@text'].replace('^', ' (carret) ').replace('{', '').replace('}', '').replace('\\',
                                                                                                                        'backslash').replace('&', '\\&').replace('_', '\\_')
        except Exception:
            pass
        try:
            if (self.args.verbose):
                print(query)
                print(result)
        except NameError:
            pass

        return result


    def latex_to_wa_matrix(self, input):
        """
        Converts a LaTeX matrix to a WolframAlpha matrix.
    
        Recursively interprets matrices in matrices.
    
        :param input: Content of a LaTeX matrix (without '\begin{...}')
        :return: Matrix in WolframAlpha style
        """
        # Recursion:
        input = self.wa_mod_matrix(input)

        input = input.replace('  ', ' ').replace('\n', '')
        res = '{'
        for row in input.split('\\\\'):
            temp_res = '{'
            for elem in row.split('&'):
                if len(elem) > 0:
                    if len(temp_res) > 1:
                        temp_res += ','
                    temp_res += elem
            temp_res += '}'
            # if len(temp_res) > 2:
            if temp_res != '{}' and temp_res != '{ }':
                if len(res) > 1:
                    res += ','
                res += temp_res
        res += '}'
        res = res.replace(', ', ',').replace(' ,', ',').replace('{ ', '{').replace(' }', '}')
        return " " + res + " "


    def wa_mod_matrix(self, latex):
        """
        Main function for converting LaTeX matrices to WolframAlpha matrices.
    
        :param latex: LaTeX code which possibly contains matrices
        :return: input, while matrices are converted into WolframAlpha matrices
        """
        for matrix_type in ['matrix', 'bmatrix', 'pmatrix']:
            while r'\begin{' + matrix_type + '}' in latex and r'\end{' + matrix_type + '}' in latex:
                latex = src.helper.apply_between_on_first_without_before_and_after(self.latex_to_wa_matrix, r'\begin{' + matrix_type + '}',
                                                                                   r'\end{' + matrix_type + '}', latex)

        return latex