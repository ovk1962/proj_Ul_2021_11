#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_db_SQLite.py
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_CNST():
    # cfg_soft
    titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    head_cfg_soft  = ['name', 'val']
    default_cfg = [['titul',          'term'],                      # name of term
                   ['path_file_DATA', 'C:/get_ASK_BID.txt'],        # data file
                   ['path_file_HIST', 'C:/2021-00-00_hist_log.txt'],# hist file TODAY from term
                   ['dt_start',       '2017-01-01 00:00:00'],       # don't change
                   ['path_file_TXT',  'C:/***_hist_log.txt']]       # hist file TODAY from SQLite DB
    # account
    head_data_acnt = ['name', 'val']
    #
    head_hist_fut = ['dt', 'tm', 'SBER_ask', 'SBER_bid', 'GAZP_ask', 'GAZP_bid']
    head_hist_pck = ['dt', 'tm', 'ask', 'bid', 'ema', 'ema_r', 'cnt']
    #
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    # hist_fut
    head_data_hst  = ['name', 'val']
    fAsk, fBid = range(2)
    # account
    aBal, aPrf, aGo, aDep = range(4)
    # cfg_pck
    kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
    head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go', 'pos', 'neg', 'ratio']
    # arr_fut_a  arr_fut_t
    fAsk, fBid = range(2)
    # data_pck
    head_data_pack = ['nm', 'Ask', 'Bid', 'ema', 'ema_r', 'cnt']
    # arr_pck_a  arr_pck_t
    pAsk, pBid, pEMAf, pEMAf_r, pCnt_EMAf_r = range(5)
    # setup the parameters of the message
    pa   = '200'
    ss   = '66'
    word = '002'
    msg_from = 'mobile.ovk@gmail.com'
    # setup the parameters of the FTP
    pas   = '30'
    ssw   = 'M%5'
    sword = 'ba8'
    hst   = 't91619ws'
    usr   = hst + '_ftp'

#=======================================================================
class Class_DB_SQLite():
    def __init__(self, prd = 'TODAY'):
        #self.path_db  = path_db
        c_dir           = os.path.abspath(os.curdir)
        if prd == 'TODAY':
            self.path_db    = c_dir + '\\DB\\db_TODAY.sqlite'
        else:
            self.path_db    = c_dir + '\\DB\\db_ARCH.sqlite'
            
    def read_all_tbl(self):
        print('=> _SQLite read_all_tbl => ', self.path_db)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cur.fetchall()
                all_tbls = []
                for table_name in tables:
                    cur.execute('SELECT * from ' + table_name[0])
                    arr = cur.fetchall()
                    all_tbls.append([table_name[0], list(arr)])
                    #ok_lmb('read_all_tbl', table_name[0])
                print(3*'=', ' Read ALL tables from DB TODAY ', 43*'=') 
                x = PrettyTable()
                x.field_names = ["Table name", "Len"]
                for item in all_tbls:
                    x.add_row( [item[0],  len(item[1])])
                print(x, '\n')
    
        except Exception as ex:
            return [1, ex]
        return [0, all_tbls]
        
    def read_tbl(self, nm_tbl):
        print('=> _SQLite read_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
                lst_arr = []
                for item in arr: lst_arr.append(list(item))
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, lst_arr]

    def read_tbl_between(self, nm_tbl, sec_FROM, sec_TO):
        print('=> _SQLite read_tbl_between ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl + ' WHERE ind_sec > ' + str(sec_FROM) + ' AND ind_sec < ' + str(sec_TO))
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
                lst_arr = []
                for item in arr: lst_arr.append(list(item))
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, lst_arr]

    def update_tbl(self, nm_tbl, buf_arr, val = ' VALUES(?,?)', p_append = False):
        print('=> _SQLite update_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                if p_append == False:
                    cur.execute('DELETE FROM ' + nm_tbl)
                    print('=> _SQLite DELETE FROM ', nm_tbl)
                cur.executemany('INSERT INTO ' + nm_tbl + val, buf_arr)
                conn.commit()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                print('=> _SQLite SELECT * from ', nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, arr]

    def update_2_tbl(self,
                    nm_tbl_1, buf_arr_1,
                    nm_tbl_2, buf_arr_2,
                    val1 = ' VALUES(?)', val2 = ' VALUES(?,?)'):
        print('=> _SQLite update_2_tbl ', nm_tbl_1, '   ', nm_tbl_2)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                cur.execute('DELETE FROM ' + nm_tbl_1)
                cur.execute('DELETE FROM ' + nm_tbl_2)
                cur.executemany('INSERT INTO ' + nm_tbl_1 + val1, buf_arr_1)
                cur.executemany('INSERT INTO ' + nm_tbl_2 + val2, buf_arr_2)
                conn.commit()
                #--- read  table   ---------------------------------
                #cur.execute('SELECT * from ' + nm_tbl_1)
                #arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']
#=======================================================================
def event_MENU(_tod, wndw, ev, val):
    res = _tod.read_all_tbl()
    #if res[0] == 0:
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
#=======================================================================
def main():
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = ['DATA_FUT',
                'CFG_SOFT',
                'CFG_PACK',
                'DATA_TICKS',
                'HIST_FUT',
                'HIST_PACK',]
        _tod = Class_DB_SQLite()
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['Exit', ['Exit']],
                    ['Func', func ],
                    ['Help', ['About...']],]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.StatusBar(text= '... just STATUS Bar ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title('py_SQLite_class')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(_tod, window, event, values)
        #
        if event == 'About...':
            event_MENU(_tod, window, event, values)

    return 0

if __name__ == '__main__':
    main()

