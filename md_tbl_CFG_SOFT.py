#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_tbl_CFG_SOFT.py
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
from prettytable import PrettyTable
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
class Class_CFG_SOFT():
    #head_cfg_pack  = ['name', 'val']
    #titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    #default_cfg = [['titul',          'term'],                      # name of term
                   #['path_file_DATA', 'C:/get_ASK_BID.txt'],        # data file
                   #['path_file_HIST', 'C:/2021-00-00_hist_log.txt'],# hist file TODAY from term
                   #['dt_start',       '2017-01-01 00:00:00'],       # don't change
                   #['path_file_TXT',  'C:/***_hist_log.txt']]       # hist file TODAY from SQLite DB

    def __init__(self):
        self.user_cfg = []

    def prn_PrettyTable(self):
        print(3*'=', ' Class_CFG_SOFT user_cfg ', 50*'=') 
        x = PrettyTable()
        x.field_names = ["val", "user"]
        for i, item in enumerate(self.user_cfg):
            x.add_row([item[0], item[1]])
        print(x, '\n')
        print(3*'=', ' Class_CFG_SOFT default_cfg ', 47*'=') 
        y = PrettyTable()
        y.field_names = ["val", "default"]
        for i, item in enumerate(_consts.default_cfg):
            y.add_row([item[0], item[1] ])
        print(y, '\n')

    def parse_cfg_SOFT(self, lst_cfg):
        print('lench = ', len(lst_cfg))
        self.user_cfg = []
        for i, j in enumerate(lst_cfg):
            self.user_cfg.append(j)
        self.prn_PrettyTable()

    def view_cfg_SOFT(self):
        #c = Class_CFG_SOFT()
        c = _consts
        m = self.user_cfg
        layout = [
          [sg.Text('titul         ', size=(12, 1)), sg.In(m[c.titul][1],          key='-TT-')],
          [sg.Text('path_file_DATA', size=(12, 1)), sg.In(m[c.path_file_DATA][1], key='-DT-'), sg.FileBrowse()],
          [sg.Text('path_file_HIST', size=(12, 1)), sg.In(m[c.path_file_HIST][1], key='-HS-'), sg.FileBrowse()],
          [sg.Text('path_file_TXT ', size=(12, 1)), sg.In(m[c.path_file_TXT][1],  key='-TX-'), sg.FileBrowse()],
          [sg.Button('_SAVE_', key='-SAVE_CFG_SOFT-'), sg.Button('_Close_')]]

        wnd_4 = sg.Window('DB_TABL / CONF_PACK_TABL', layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_4.read()
            if e in [sg.WIN_CLOSED, '_Close_']:  break
            if e in ['-SAVE_CFG_SOFT-']:
                m[c.titul] = (m[c.titul][0], v['-TT-'])
                m[c.path_file_DATA] = (m[c.path_file_DATA][0], v['-DT-'])
                m[c.path_file_HIST] = (m[c.path_file_HIST][0], v['-HS-'])
                m[c.path_file_TXT] = (m[c.path_file_TXT][0], v['-TX-'])
                os.system('cls')  # on windows
                self.prn_PrettyTable()
                #update self.user_cfg into DB TODAY
                rq = _db_tod.update_tbl('cfg_SOFT',
                            self.user_cfg, val = ' VALUES(?,?)')
                if rq[0] > 0:
                    #err_lmb('event_menu_CFG_SOFT',
                    #    s_lmb('Did not update cfg_SOFT!') + s_lmb(rep[1]))
                    sg.popup_ok('Did not update cfg_SOFT!', s_lmb(rq[1]),
                        background_color='Coral', title=e)
                else:
                    sg.popup_ok('Updated *cfg_SOFT* successfully !',
                        background_color='LightGreen', title=e)
                break
        wnd_4.close()

#=======================================================================
def event_MENU(tbl_cfg_SOFT, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'view_cfg_SOFT':
        wndw.disappear()
        #os.system('cls')  # on windows
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'cfg_SOFT':
                    tbl_cfg_SOFT.parse_cfg_SOFT(item[1])
                    tbl_cfg_SOFT.view_cfg_SOFT()
        else:
            err_lmb('view_cfg_SOFT',res[1])
        wndw.reappear()
#=======================================================================
def main():
    tbl_cfg_SOFT = Class_CFG_SOFT()    # init new obj !!!
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'view_cfg_SOFT',
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
        window.set_title('py_cfg_SOFT_class')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(tbl_cfg_SOFT, window, event, values)
    return 0

if __name__ == '__main__':
    main()

