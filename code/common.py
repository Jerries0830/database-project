from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Treeview
from tkinter import *

import commands


def get_treeview(master, columns, widths, anchors):
    treeview = Treeview(master, columns=columns, show="headings")
    treeview.pack(side="left", fill="both", expand=True)

    for column, width, anchor in zip(columns, widths, anchors):
        treeview.column(column, width=width, anchor=anchor)
        treeview.heading(column, text=column)

    scroll = Scrollbar(master, orient=VERTICAL, command=treeview.yview)
    treeview.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    return treeview
