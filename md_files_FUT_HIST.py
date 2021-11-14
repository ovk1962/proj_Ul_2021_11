#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_files_FUT_HIST.py
#  
#=======================================================================
import os, sqlite3, sys
from datetime import datetime, timezone
#from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
import md_tbl_CFG_SOFT as tbl_cfg_soft
import md_tbl_DATA_FUT as tbl_data_fut
#=======================================================================
_db_tod   = dbs.Class_DB_SQLite()
_consts   = dbs.Class_CNST()
_cfg_soft = tbl_cfg_soft.Class_CFG_SOFT()
_data_fut = tbl_data_fut.Class_DATA_FUT()
_data_acc = tbl_data_fut.Class_ACNT()
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_DATA_HIST():
    def __init__(self):
        #---------------------------  err_status  --------------------------
        self.err_try  = 128      #
        self.err_file = 1        # can not find file => path_file_DATA
        self.err_size = 2        # size DATA file is 0
        self.err_mdf_time  = 4   # FILE is not modificated
        self.err_file_size = 8   # FILE size is NULL
        #err_mrkt_time = 16  # size buf_str is NULL
        self.err_update_db = 32  #  can not update info in DB
        #-------------------------------------------------------------------
        self.path_file_DATA = ''
        self.path_file_HIST = ''
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.dt_fut      = []    # list of Class_FUT()
        self.account = _data_acc # obj Class_ACCOUNT()
        #
        self.time_1_min = 0
        #
        self.err_status  = 0
        self.cnt_errors  = 0
    #-------------------------------------------------------------------
    def check_MARKET_day(self):
        date = datetime.today()
        days=["Monday",   "Tuesday", "Wednesday", "Thursday", "Friday",
              "Saturday", "Sunday"]
        return days[date.weekday()]
    #-------------------------------------------------------------------
    def check_MARKET_time(self, term_dt):
        try:
            dtt = datetime.strptime(term_dt, "%d.%m.%Y %H:%M:%S")
            cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
            if (
                (cur_time > 25195  and # from 06:59:55 to 14:00:05
                #(cur_time > 35995  and # from 09:59:55 to 14:00:05
                cur_time < 50415) or   #
                (cur_time > 50685  and # from 14:04:55 to 18:45:05
                cur_time < 67505) or
                (cur_time > 68695  and # from 19:04:55 to 23:50:05
                cur_time < 85805)):
                    return True
        except Exception as ex:
            print('ERROR term_dt = ', term_dt)
        return False
    #-------------------------------------------------------------------
    def rd_term_FUT(self):
        # read data FUT from file 'path_file_DATA'----------------------
        print('=> _TERM rd_term_FUT => ' + self.path_file_DATA)
        self.err_status  = 0
        try:
            #--- check file self.file_path_DATA ------------------------
            if not os.path.isfile(self.path_file_DATA):
                self.err_status += self.err_file
                return
            buf_stat = os.stat(self.path_file_DATA)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size
                return
            #--- check time modificated of file ------------------------
            print('self.dt_file       ', self.dt_file)
            #print('self.dt_data       ', self.dt_data)
            print('buf_stat.st_mtime  ', int(buf_stat.st_mtime))
            if ((int(buf_stat.st_mtime) - self.dt_file) < 2):
            #if int(buf_stat.st_mtime) == self.dt_file:
                #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
                self.err_status += self.err_mdf_time
                return
            else:
                self.dt_file = int(buf_stat.st_mtime)
            #--- read TERM file ----------------------------------------
            buf_str = []
            with open(self.path_file_DATA,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size
                return
            self.data_in_file = buf_str[:]
            for i in self.data_in_file:   print(i)
            #
            self.dt_fut = []
            acc = self.account
            for i, item in enumerate(self.data_in_file):
                lst = ''.join(item).replace(',','.').split('|')
                del lst[-1]
                #print(lst)
                if   i == 0:
                    acc.dt  = lst[0]
                    dtt = datetime.strptime(acc.dt, "%d.%m.%Y %H:%M:%S")
                elif i == 1:
                    acc.arr = [float(j) for j in lst]
                #else:
                    #b_fut = .Class_DATA_FUT()
                    #b_fut.sP_code = lst[0]
                    #b_fut.arr     = [float(k) for k in lst[1:]]
                    #self.dt_fut.append(b_fut)
        except Exception as ex:
            self.err_status += self.err_try
        return
    #-------------------------------------------------------------------
    def rd_term_HST(self):
        # read HIST from file 'path_file_HIST'--------------------------
        print('=> _TERM rd_term_HST => ' + self.path_file_HIST)
        self.err_status  = 0
        try:
            path_hist = self.path_file_HIST
            #--- check file self.path_file_HIST ------------------------
            if not os.path.isfile(path_hist):
                self.err_status += self.err_file # can not find path_file_HIST
                return
            buf_stat = os.stat(path_hist)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size # size HIST file is NULL
                return
            #--- read HIST file ----------------------------------------
            buf_str = []
            with open(path_hist,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size # the size buf_str(HIST) is NULL
                return
            #--- check MARKET time from 10:00 to 23:45 -----------------
            self.hist_in_file = []
            error_MARKET_time = False
            for i, item in enumerate(buf_str):
                term_dt = item.split('|')[0]
                if self.check_MARKET_time(term_dt):
                    self.hist_in_file.append(item)
                else:
                    error_MARKET_time = True
                    print('error string is ',i)
            #--- repeir file 'path_file_HIST' --------------------------
            if error_MARKET_time:
                with open(path_hist, 'w') as file_HIST:
                    for item in self.hist_in_file:
                        file_HIST.write(item+'\n')
            #
        except Exception as ex:
            print('rd_term_HST\n' + str(ex))
            self.err_status += self.err_try
        return
    #-------------------------------------------------------------------
#=======================================================================
def event_MENU(files_DATA_HIST, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'read_file_DATA':
        wndw.disappear()
        #os.system('cls')  # on windows
        # 1. Get path_file_DATA from cfg_SOFT table
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'cfg_SOFT':
                    _cfg_soft.parse_cfg_SOFT(item[1])
        else:
            err_lmb('view_data_FUT',res[1])
        # 2. Read data FUT from file path_file_DATA
        files_DATA_HIST.path_file_DATA = _cfg_soft.user_cfg[_consts.path_file_DATA][1]
        files_DATA_HIST.rd_term_FUT()
        if files_DATA_HIST.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *data_file*!') +
                            s_lmb(files_DATA_HIST.err_status))
        else:
            sg.popup_ok('Read term *data_file* successfully !',
                    background_color='LightGreen', title='main')
            #os.system('cls')  # on windows
            #
            # 3. Write data FUT into table data_FUT
            buf_arr_1 = ((j,) for j in files_DATA_HIST.data_in_file)
            res = _db_tod.update_tbl('data_FUT', buf_arr_1, val = ' VALUES(?)')
            if res[0] == 0:
                sg.popup_ok(s_lmb('Updated table *data_FUT* successfully !'),
                        background_color='LightGreen', title='main')
            else:
                err_lmb('Write data FUT into table data_FUT',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev in ['view_tbl_DATA', 'view_tbl_ACOUNT']:
        wndw.disappear()
        #os.system('cls')  # on windows
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'data_FUT':
                    _data_fut.parse_data_FUT(item[1])
                    if ev == 'view_tbl_DATA':    _data_fut.view_data_FUT()
                    if ev == 'view_tbl_ACOUNT':  _data_fut.view_ACOUNT()
        else:
            err_lmb('view_data_FUT',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'read_file_HIST':
        wndw.disappear()
        #os.system('cls')  # on windows
        # 1. Get path_file_HIST from cfg_SOFT table
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'cfg_SOFT':
                    _cfg_soft.parse_cfg_SOFT(item[1])
        else:
            err_lmb('read_file_HIST',res[1])
        # 2. Read data FUT from file path_file_DATA
        files_DATA_HIST.path_file_HIST = _cfg_soft.user_cfg[_consts.path_file_HIST][1]
        files_DATA_HIST.rd_term_HST()
        if files_DATA_HIST.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *hist_file*!') +
                            s_lmb(files_DATA_HIST.err_status))
        else:
            sg.popup_ok('Read term *hist_file* successfully !',
                    background_color='LightGreen', title='main')
            if len(files_DATA_HIST.hist_in_file) > 0:
                buf_arr_2 = []
                frm = '%d.%m.%Y %H:%M:%S'
                for it in files_DATA_HIST.hist_in_file:
                    dtt = datetime.strptime(it.split('|')[0], frm)
                    ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                    buf_arr_2.append([ind_sec, it])
                res = _db_tod.update_tbl('hist_FUT', buf_arr_2, val = ' VALUES(?,?)')
                if res[0] == 0:
                    sg.popup_ok(s_lmb('Updated table *hist_FUT* successfully !'),
                            background_color='LightGreen', title='main')
                else:
                    err_lmb('Write hist FUT into table hist_FUT',res[1])
        wndw.reappear()
#=======================================================================
def main():
    files_DATA_HIST = Class_DATA_HIST()
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'read_file_DATA',
                'view_tbl_DATA',
                'view_tbl_ACOUNT',
                'read_file_HIST',
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
            event_MENU(files_DATA_HIST, window, event, values)
    return 0

if __name__ == '__main__':
    main()

