#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Felix Petersen"
__status__      = "Production"


import re

def get_first_occurence_of_in(before_str, after_str, text):
    """
    Get the string, which begins after the first occurence of before_str
    and ends before the first occurence of after_str after the first occurence of before_str.

    E.g. for getting the content of the tex document

    :param before_str: 
    :param after_str: 
    :param text: 
    :return: 
    """
    pos_begin = text.find(before_str)
    if pos_begin != -1:
        pos_begin += len(before_str)
        pos_begin_with_offset = pos_begin
        pos_end = text.find(after_str, pos_begin_with_offset)
        while (pos_end != -1) & (text[pos_end - 1] == '\\'):
            pos_begin_with_offset = pos_end + 1
            pos_end = text.find(after_str, pos_begin_with_offset)
        if pos_end != -1:
            return pos_begin, pos_end, text[pos_begin:pos_end]
    else:
        return ''


def get_author(text):
    """
    Returns the name of the author of the TeX document

    >>> get_author(r"...\\title{Title} ... \\author{Felix} ... Content")
    'Felix'
    >>> get_author(r"...\\title{Title} ... Author is Felix ... Content")
    'unknown author'

    :param text: LaTeX document
    :return: name of the author
    """
    author = get_first_occurence_of_in("\\author{", "}", text)
    if author == '':
        return 'unknown author'
    else:
        return author[2]


def split_content_of_first_occurence(before_str, after_str, text):
    """
    Splits a string according to `get_first_occurence_of_in` into three substrings.

    :param before_str: 
    :param after_str: 
    :param text: 
    :return: 
    """
    pos_begin, pos_end, content = get_first_occurence_of_in(before_str, after_str, text)
    return [text[:pos_begin], text[pos_begin:pos_end], text[pos_end:]]


# TODO: ensure to get the correct closing bracket (e.g. \chapter{{}} )
def split_at_every_splitter_latex(text, splitters):
    parts = []
    begin = 0
    first_occurence = len(text)
    end_of_first_occurence = 0
    for splitter in splitters:
        occurrence = text.find('\\' + splitter, begin)
        if (occurrence != -1) & (first_occurence > occurrence):
            first_occurence = text.find('\\' + splitter, begin)
            end_of_first_occurence = first_occurence + len(splitter)
    if first_occurence != len(text):
        while (end_of_first_occurence < len(text)) & (
            (text[end_of_first_occurence - 1] != '}') | (text[end_of_first_occurence - 2] == '\\')):
            end_of_first_occurence += 1
        parts.append(text[:first_occurence])
        parts.append(text[first_occurence:end_of_first_occurence])
        for part in split_at_every_splitter_latex(text[end_of_first_occurence:], splitters):
            parts.append(part)
    else:
        parts.append(text)
    return parts


def split_at_every_splitter(text, splitters):
    parts = []
    begin = 0
    first_occurence = len(text)
    end_of_first_occurence = 0
    for splitter in splitters:
        occurrence = text.find(splitter, begin)
        if (occurrence != -1) & (first_occurence > occurrence):
            first_occurence = text.find(splitter, begin)
            end_of_first_occurence = first_occurence + len(splitter)
    if first_occurence != len(text):
        parts.append(text[:first_occurence])
        parts.append(text[first_occurence:end_of_first_occurence])
        for part in split_at_every_splitter(text[end_of_first_occurence:], splitters):
            parts.append(part)
    else:
        parts.append(text)
    return parts


def apply_between_on_first_without_before_and_after(fun, before, after, text):
    """
    Applies 'fun' on the part between first 'before' and the next 'after', removes these 'before' and 'after', and
    concatenates this.

    :param fun: Function
    :param before: 
    :param after: 
    :param text: 
    :return: Concatenated with 'fun' applied to a part of 'text'
    """
    res = text.split(before)[0]
    res += fun(text.split(before)[1].split(after)[0])
    res += after.join(before.join(text.split(before)[1:]).split(after)[1:])
    return res


def get_number_of_element_occurences_list(list_of_elements, text):
    delimiters = r''
    for elem in list_of_elements:
        delimiters += r'(' + elem.replace('\\', '\\\\') + r')|'
    delimiters = delimiters[:-1]
    n_of_occurences = 0
    for elem in re.split(delimiters, text):
        if elem in list_of_elements:
            n_of_occurences += 1
    return n_of_occurences


def list_to_or_regex(list):
    """
    Transform a list into a RegEx, while connection each element with `OR`.
    
    :param list: 
    :return: regex
    """
    regex = r''
    for elem in list:
        regex += '(' + elem + ')|'
    return regex[:-1]


def get_as_long_as_correct_parentheses_from_left(input):
    """
    Takes a LaTeX math expression returns as much as possible while ensuring correct parentheses.
    Further it ensures that if there is currently no bracket it will be stopped by any maths comparator.
    
    >>> get_as_long_as_correct_parentheses_from_left(r" \sum_{i=1}^9 (i^2) = { 285 ")
    ' \\\sum_{i=1}^9 (i^2) '
    >>> get_as_long_as_correct_parentheses_from_left(r" \sum_{i=1}^9 (i^2) { 285 ")
    ' \\\sum_{i=1}^9 (i^2) { 285 '
    
    # Tests for `right`:
    
    >>> get_as_long_as_correct_parentheses_from_right(r" \sum_{i=1}^9 (i^2) = 285 ")
    ' 285 '
    >>> get_as_long_as_correct_parentheses_from_right(r" \sum_{i=1}^9 (i^2) { 285 ")
    ' 285 '
    >>> get_as_long_as_correct_parentheses_from_right(r" \sum_{i=1}^9 (i^2) = 285 ) ")
    ' \\\sum_{i=1}^9 (i^2) = 285 ) '
    
    :param input: LaTeX math expression
    :return: correct subexpression of input
    """

    parentheses_stack = []
    opening_to_closing = {'{': '}', '[': ']', '(': ')'}
    closing = '}])'

    delimiters_only_one_direction = ['=', '\\equiv', '\\neq', '\\geq', '\\leq']
    delimiters = []
    for delimiter in delimiters_only_one_direction:
        delimiters.append(delimiter)
        delimiters.append(delimiter[::-1])

    output = ''
    pos = 0
    for char in input:

        # Stop if there is no paranthese missing and there is a delimiter:
        if len(parentheses_stack) == 0:
            for delimiter in delimiters:
                if input[pos:].find(delimiter) == 0:
                    return output

        if char in opening_to_closing:
            parentheses_stack.append(opening_to_closing[char])
        elif char in closing:
            if len(parentheses_stack) != 0 and char == parentheses_stack.pop():
                pass
            elif len(parentheses_stack) == 0:
                return output
            else:
                return ''
        output += char
        pos += 1
    return output


def get_as_long_as_correct_parentheses_from_right(input):
    """
    The other direction of `get_as_long_as_correct_parentheses_from_left`.
    Uses `get_as_long_as_correct_parentheses_from_left`.
    """
    input = input.replace('{', '%temp%').replace('}', '{').replace('%temp%', '}')
    input = input.replace('[', '%temp%').replace(']', '[').replace('%temp%', ']')
    input = input.replace('(', '%temp%').replace(')', '(').replace('%temp%', ')')
    input = input[::-1]
    input = get_as_long_as_correct_parentheses_from_left(input)
    input = input.replace('{', '%temp%').replace('}', '{').replace('%temp%', '}')
    input = input.replace('[', '%temp%').replace(']', '[').replace('%temp%', ']')
    input = input.replace('(', '%temp%').replace(')', '(').replace('%temp%', ')')
    return input[::-1]




