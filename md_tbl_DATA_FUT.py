#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_tbl_DATA_FUT.py
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
#from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
#=======================================================================
_db_tod = dbs.Class_DB_SQLite()
_consts = dbs.Class_CNST()
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_ACNT():
    #head_data_acnt = ['name', 'val']
    head_data_acnt = ['dt', 'aBal', 'aPrf', 'aGo', 'aDep']
    aBal, aPrf, aGo, aDep = range(4)
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_DATA_FUT():
    #head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
    #            'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    #sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    def __init__(self):
        self.sP_code, self.arr = '', []
        self.dt_fut    = []     # list obj FUTs from table 'data_FUT'
        self.account   = Class_ACNT()# obj Class_ACNT()
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))

    def parse_data_FUT(self, data_FUT):
        #print('lench = ', len(data_FUT))
        # unpack cfg_SOFT --------------------------------------
        try:
            self.dt_fut = []
            acc = self.account

            for i, item in enumerate(data_FUT):
                lst = ''.join(item).replace(',','.').split('|')
                del lst[-1]
                if   i == 0:
                    acc.dt  = lst[0]
                elif i == 1:
                    acc.arr = [float(j) for j in lst]
                else:
                    self.dt_fut.append([lst[0], [float(k) for k in lst[1:]]])
            #print(self.account)
            #for i in self.dt_fut:   print(i)
        except Exception as ex:
            #self.err_status = 'read_data_FUT / try  ' + s_lmb(ex)
            #self.err_DB(err_log = True)
            return [4, ex]
        return [0, 'ok']

    def view_data_FUT(self):
        #for item in _tod.dt_fut:
        #    print(item.sP_code, item.arr)
        mtrx = [([item[0]] + item[1]) for item in self.dt_fut]
        layout = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = _consts.head_data_fut,
                    key      = '_DATA_FUT_FILE_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'lightsteelblue',
                    )],[sg.Button('Close')],                    ]
        wnd_3 = sg.Window('DATA_FUT_FILE_table', layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_3.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
        wnd_3.close()

    def view_ACOUNT(self):
        mtrx = [[self.account.dt] + self.account.arr]
        layout = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = Class_ACNT.head_data_acnt,
                    key      = '_ACOUNT_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'lightsteelblue',
                    )],[sg.Button('Close')],                    ]
        wnd_4 = sg.Window('ACOUNT_table', layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_4.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
        wnd_4.close()
#=======================================================================
def event_MENU(tbl_data_FUT, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'view_data_FUT':
        wndw.disappear()
        #os.system('cls')  # on windows
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'data_FUT':
                    tbl_data_FUT.parse_data_FUT(item[1])
                    tbl_data_FUT.view_data_FUT()
        else:
            err_lmb('view_data_FUT',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'view_ACOUNT':
        wndw.disappear()
        #os.system('cls')  # on windows
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'data_FUT':
                    tbl_data_FUT.parse_data_FUT(item[1])
                    tbl_data_FUT.view_ACOUNT()
        else:
            err_lmb('view_ACOUNT',res[1])
        wndw.reappear()
#=======================================================================
def main():
    tbl_data_FUT = Class_DATA_FUT()    # init new obj !!!
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'view_data_FUT',
                'view_ACOUNT',
                'About...',]
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['Exit', ['Exit']],
                    ['Func', func ],]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.StatusBar(text= '... just STATUS Bar ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title('py_data_FUT_class')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(tbl_data_FUT, window, event, values)
    return 0

if __name__ == '__main__':
    main()

