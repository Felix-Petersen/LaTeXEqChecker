#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Felix Petersen"
__status__      = "Production"


import sys, os
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


def get_file_path(title1):
    filename = askopenfilename(filetypes=(("LaTeX files", "*.tex"),
                                          ("All files", "*.*")),
                               title=title1)
    return filename


def get_file_path_txt(title):
    filename = askopenfilename(filetypes=(("Text", "*.txt"),
                                          ("All files", "*.*")),
                               title=title)
    return filename


class GUI:
    """
    Class for the graphical interface.
    """
    
    def __init__(self, master, args):
        """
        Initializes the GUI.
        
        :param master: 
        :param args: `args` which are used as standard values of the GUI
        """
        self.master = master
        self.args = args
        master.title("LaTeXEqChecker")

        rowN = 0

        self.label = tk.Label(master, text="Checks equations in LaTeX files and annotates their correctness.")
        self.label.grid(row=rowN, columnspan=4)

        self.label_in_file = tk.Label(master, text="Input")
        self.label_out_file = tk.Label(master, text="Output")
        self.label_ans_file = tk.Label(master, text="WA API results store")

        self.in_file = tk.StringVar()
        self.out_file = tk.StringVar()
        self.ans_file = tk.StringVar()

        self.var_wa = tk.BooleanVar()
        self.var_sp = tk.BooleanVar()
        self.var_l  = tk.BooleanVar()
        self.var_num = tk.BooleanVar()
        self.var_stat = tk.BooleanVar()
        self.var_mirror = tk.BooleanVar()
        self.var_f = tk.BooleanVar()

        self.in_file.set("./" + args.input_file_dir)
        self.out_file.set(args.output)
        self.var_wa.set(args.wolfram_alpha)
        self.var_sp.set(args.sympy)
        self.var_l.set(args.lets)
        self.var_num.set(args.test_numerical)
        self.var_stat.set(args.statistics)
        self.var_mirror.set(args.mirror_interpretation)
        self.var_f.set(args.folder)
        if args.wolfram_alpha_results:
            self.ans_file.set(args.wolfram_alpha_results)

        self.text_in_file = tk.Entry(master, textvariable=self.in_file, width=50)
        self.text_out_file = tk.Entry(master, textvariable=self.out_file, width=50)
        
        self.check_l  = tk.Checkbutton(master, text="[WolframAlpha only] consider previous equations as definitions", variable=self.var_l)
        self.check_num = tk.Checkbutton(master, text="[SymPy only] test the equations numerical, too", variable=self.var_num)
        self.check_stat = tk.Checkbutton(master, text="print out some statistics about the results", variable=self.var_stat)
        self.check_mirror  = tk.Checkbutton(master, text="[SymPy only] show the interpretation of the formulae backconverted to LaTeX behind the formula, too", variable=self.var_mirror)
        self.check_f = tk.Checkbutton(master, text="check for every *.tex file in the directory (not recursively); save results in ./texEqCheck/*.tex", variable=self.var_f)
        self.text_ans_file = tk.Entry(master, textvariable=self.ans_file, width=50)

        self.cas_var = tk.IntVar()

        self.check_wa = tk.Radiobutton(master, text="use WolframAlpha for the correction", variable=self.cas_var, value=1)
        self.check_sp = tk.Radiobutton(master, text="use SymPy for the correction", variable=self.cas_var, value=2)

        def setInFile():
            self.in_file.set(get_file_path("Select input TeX file: \"IN\""))

        def setOutFile():
            self.out_file.set(asksaveasfilename(title="Where to save the output?", defaultextension=".tex"))

        def setAnsFile():
            self.ans_file.set(get_file_path_txt(title="[WolframAlpha only] define a file to store / reuse the results from the WolframAlpha API"))

        self.button_in_file = tk.Button(master, text="...",
                                        command=setInFile)
        self.button_out_file = tk.Button(master, text="...",
                                         command=setOutFile)
        self.button_ans_file = tk.Button(master, text="...",
                                         command=setAnsFile)

        rowN += 1
        self.label_in_file.grid(row=rowN, column=1, sticky=tk.W)
        self.text_in_file.grid(row=rowN, column=2)
        self.button_in_file.grid(row=rowN, column=3)

        rowN += 1
        self.label_out_file.grid(row=rowN, column=1, sticky=tk.W)
        self.text_out_file.grid(row=rowN, column=2)
        self.button_out_file.grid(row=rowN, column=3)

        rowN += 1
        self.check_f.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_wa.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_sp.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_l.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_num.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_mirror.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.check_stat.grid(row=rowN, column=2, sticky=tk.W)

        rowN += 1
        self.label_ans_file.grid(row=rowN, column=1, sticky=tk.W)
        self.text_ans_file.grid(row=rowN, column=2)
        self.button_ans_file.grid(row=rowN, column=3)

        rowN += 1

        self.close_button = tk.Button(master, text="Abort", command=self.close)
        self.close_button.grid(row=rowN, column=2)

        self.close_button = tk.Button(master, text="Check", command=self.compute)
        self.close_button.grid(row=rowN, column=3, sticky=tk.E)

    def compute(self):
        """
        Saves the in the GUI set values back to `args` and quits.
        
        :return: 
        """
        path_in = self.in_file.get()
        path_out = self.out_file.get()

        # check if the paths are correct:
        if os.path.isfile(path_in) & os.path.isdir(os.path.dirname(path_out)):
            self.args.input_file_dir = path_in
            self.args.output = path_out

            self.args.wolfram_alpha = (self.cas_var.get() == 1)
            self.args.sympy = (self.cas_var.get() == 2)
            self.args.lets = self.var_l.get()
            self.args.test_numerical = self.var_num.get()
            self.args.statistics = self.var_stat.get()
            self.args.mirror_interpretation = self.var_mirror.get()
            self.args.folder = self.var_f.get()

            self.args.wolfram_alpha_results = self.ans_file.get()

            self.master.quit()
        else:
            print("Please choose correct files!")


    def close(self):
        sys.exit(1)


if __name__ == "__main__":
    master = tk.Tk()

    gui = GUI(master, 0)

    tk.mainloop()