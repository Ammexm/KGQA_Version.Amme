# coding: utf-8
# File: AmmeRevision
# Update: 2021/1/31
# Blog:
# Origin Source:
# 1、https://github.com/liuhuanyong/QASystemOnMedicalKG
# 2、https://github.com/vivianLL/QASystemOnHepatopathyKG


def set_win_center(root, curWidth='', curHight=''):

    if not curWidth:
        curWidth = root.winfo_width()
    if not curHight:
        curHight = root.winfo_height()
    print(curWidth, curHight)

    scn_w, scn_h = root.maxsize()
    print(scn_w, scn_h)

    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    print(cen_x, cen_y)

    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    root.geometry(size_xy)

def insert_point():
    var = entry.get()
    t.insert('insert', var)

def insert_end():
    var = entry.get()
    t.insert('end', var)
    # t.insert(2.2, var)

import Tkinter as tk
from Tkinter import *

window = tk.Tk()
var=tk.IntVar()
window.title('Test')
window.configure(background='white')
window.resizable(width=False, height=False)
window.geometry('600x400')

window.update()
set_win_center(window, 600, 600)

# entry = tk.Entry(window, show="*")
entry = tk.Entry(window, show=None)
entry.grid()
var = entry.get()

t = tk.Text(window, height=10)

b1 = tk.Button(window, text='insert the target', command=insert_point)
b1.grid()
b2 = tk.Button(window, text='insert the end', command=insert_end)
b2.grid()

t.grid()

window.mainloop()
