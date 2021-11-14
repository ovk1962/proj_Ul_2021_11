#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_TEST_strategy_0_0.py
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
import md_tbl_DATA_FUT as tbl_data_fut
import md_tbl_CFG_SOFT as tbl_cfg_soft
import md_tbl_CFG_PACK as tbl_cfg_pack
import md_files_FUT_HIST as fls_data_hist
import md_tbl_HIST_FUT as tbl_hist_fut_pack
import md_com_SMTP as send_smtp
import md_GRAPH_0_2 as graphic
#=======================================================================
locationXY = (200, 150)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_STRATEG():
    def __init__(self):
        self.db_tod   = dbs.Class_DB_SQLite()
        self.db_arc   = dbs.Class_DB_SQLite(prd = 'ARCH')
        self.consts   = dbs.Class_CNST()
        self.data_fut = tbl_data_fut.Class_DATA_FUT()
        self.cfg_sft  = tbl_cfg_soft.Class_CFG_SOFT()
        self.cfg_pck  = tbl_cfg_pack.Class_CFG_PACK([])
        self.fls_data = fls_data_hist.Class_DATA_HIST()
        self.tbl_fut_pack = tbl_hist_fut_pack.Class_HIST_FUT()
        self.send_smtp    = send_smtp.Class_SMTP('','')
        self.graph_PACK   = graphic.Class_GRAPH_bar()
        self.arr_tod  = []  # list of db_tod
        self.arr_arc  = []  # list of db_arc
        #---------------------------------------------------------------
        self.tmr_RUN  = 60000
        #self.cfg_pck.parse_cfg_PACK([('p0_2_SBER','0:2:SR,9:-20:MX',0,'1111:100',1,1,1)])
            
    def read_all_tbl_ARCHIV(self):
        res = self.db_arc.read_all_tbl()
        if res[0] == 0:
            self.arr_arc = res[1]
        else:
            err_lmb('read_all_tbl_ARCHIV',res[1])

    def init_all_tbl_ARCHIV(self):
        self.read_all_tbl_ARCHIV()
        for item in self.arr_arc:
            if item[0] == 'hist_FUT':
                if len(item[1]) == 0:
                    err_lmb('arr_fut_a','Lench = 0 !')
                    return [1, 'Lench = 0 !']
                print('arr_fut_a = ', len(item[1]))
                res = self.tbl_fut_pack.parse_hist_FUT(item[1])
                if res[0] > 0:
                    err_lmb('error INIT hist_FUT_arc', res[1])
                    return [1, 'error INIT hist_FUT_arc !']
                self.tbl_fut_pack.arr_fut_a = res[1]
                self.tbl_fut_pack.view_arr_FUT(res[1], 'arr_fut_a')
            if item[0] == 'hist_PACK':
                if len(item[1]) == 0:
                    err_lmb('arr_pck_a','Lench = 0 !')
                    return [1, 'Lench = 0 !']
                print('arr_pck_a = ', len(item[1]))
                req = self.tbl_fut_pack.unpack_str_pck(item[1])
                if req[0] > 0:
                    err_lmb('error INIT hist_PACK_arc', res[1])
                    return [1, 'error INIT hist_FUT_arc !']
                self.tbl_fut_pack.arr_pck_a = req[1]
                self.tbl_fut_pack.view_arr_PACK(req[1], 'arr_pck_a')
        return [0, 'OK']
            
    def read_all_tbl_TODAY(self):
        res = self.db_tod.read_all_tbl()
        if res[0] == 0:
            self.arr_tod = res[1]
        else:
            err_lmb('read_all_tbl_TODAY',res[1])

    def init_all_tbl_TODAY(self):
        self.read_all_tbl_TODAY()
        for item in self.arr_tod:
            if item[0] == 'data_FUT':
                self.data_fut.parse_data_FUT(item[1])
                self.data_fut.view_data_FUT()
                self.data_fut.view_ACOUNT()
            if item[0] == 'cfg_SOFT':
                self.cfg_sft.parse_cfg_SOFT(item[1])
                self.cfg_sft.view_cfg_SOFT()
            if item[0] == 'cfg_PACK':
                self.cfg_pck.parse_cfg_PACK(item[1])
                self.cfg_pck.calc_cfg_PACK(self.data_fut)
                self.tbl_fut_pack.cfg_pck = self.cfg_pck
                self.cfg_pck.view_cfg_PACK()
            if item[0] == 'hist_FUT':
                if len(item[1]) > 0:
                    print('arr_fut_t = ', len(item[1]))
                    res = self.tbl_fut_pack.parse_hist_FUT(item[1])
                    if res[0] == 0:
                        self.tbl_fut_pack.arr_fut_t = res[1]
                        self.tbl_fut_pack.view_arr_FUT(res[1], 'arr_fut_t')
                    else:
                        err_lmb('error INIT hist_FUT_tod',res[1])
                else:
                    print('arr_fut_t is EMPTY !!!')
            if item[0] == 'hist_PACK':
                if len(item[1]) > 0:
                    print('arr_pck_t = ', len(item[1]))
                    req = self.tbl_fut_pack.unpack_str_pck(item[1])
                    if req[0] == 0:
                        self.tbl_fut_pack.arr_pck_t = req[1]
                        self.tbl_fut_pack.view_arr_PACK(req[1], 'arr_pck_t')
                    else:
                        err_lmb('error INIT hist_PACK_tod',req[1])
                else:
                    print('arr_pck_t is EMPTY !!!')
        return [0, 'OK']

    def calc_arr_pck_archiv(self):
        #--- prepair kNul to calc hist_PACK archiv -----------------
        for i in range(len(self.cfg_pck.cfg_PACK)):
            self.cfg_pck.cfg_PACK[i][self.consts.kNul] = 0
        #  Calc ASK/BID arr_pck_a  for  arr_fut_a
        #   LEN(arr_fut_a) should be not ZERO !!!
        res = self.tbl_fut_pack.clc_ASK_BID(self.tbl_fut_pack.arr_fut_a)
        if res[0] > 0:
            err_msg = 'Could not clc_ASK_BID in calc_arr_pck_archiv !'
            return [res[0], err_msg]
        sg.popup_ok(s_lmb('calc_ASK_BID_tod successfully !'),
                background_color='LightGreen', title='main')
        self.tbl_fut_pack.arr_pck_a = res[1]
        sg.popup('view_hist_PACK 1 last day',
                    str(self.tbl_fut_pack.arr_pck_a[-1]))
        #--- calc EMA hist_PACK archiv  ----------------------------
        sg.popup('self.tbl_fut_pack.cfg_pck',
            str(self.tbl_fut_pack.cfg_pck.cfg_PACK[-1]))
        rep = self.tbl_fut_pack.clc_EMA(self.tbl_fut_pack.arr_pck_a,
                                    tbl_hist_fut_pack.Class_str_FUT_PCK())
        if rep[0] > 0:
            #err_lmb('clc_EMA ARCHIV => ',rep[1])
            err_msg = 'Could not clc_EMA in calc_arr_pck_archiv !'
            return [rep[0], err_msg]
        self.tbl_fut_pack.arr_pck_a = rep[1]
        sg.popup_ok(s_lmb('clc_EMA successfully !'),
                background_color='LightGreen', title='main')
        rep = self.tbl_fut_pack.pack_arr_pck(self.tbl_fut_pack.arr_pck_a, self.db_arc, 'hist_PACK')
        if rep[0] > 0:
            #err_lmb('clc_EMA ARCHIV => ',rep[1])
            err_msg = 'Could not pack_arr_pck in calc_arr_pck_archiv !'
            return [rep[0], err_msg]
        #--- update kNul in cfg_pack  ------------------------------
        self.cfg_pck.update_tbl_cfg_pack()
        return [0, 'Ok']
#=======================================================================
def event_TIMEOUT(c_main, wndw, ev, val):
    #-------------------------------------------------------------------
    pass
#=======================================================================
def event_MENU(c_main, wndw, ev, val):
    #-------------------------------------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 '"Matplotlib Ver  ' + str(mpl.__version__),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #-------------------------------------------------------------------
    if ev == 'STEP':
        c_main.tmr_RUN = 600000
        wndw['-STATUS_BAR-'].Update(ev, background_color = 'Yellow')
    #-------------------------------------------------------------------
    if ev == 'STRT':
        c_main.tmr_RUN = 100
        wndw['-STATUS_BAR-'].Update(ev, background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'STOP':
        c_main.tmr_RUN = 60000
        wndw['-STATUS_BAR-'].Update(ev, background_color = 'Coral')
    #-------------------------------------------------------------------
    if ev == 'init_all_tbl_ARCHIV':
        c_main.tmr_RUN = 600000
        wndw.disappear()
        c_main.init_all_tbl_ARCHIV()
        wndw.reappear()
    #-------------------------------------------------------------------
    if ev == 'calc_ASK_BID_EMA_arc':
        c_main.tmr_RUN = 600000
        wndw.disappear()
        c_main.calc_arr_pck_archiv()
        wndw.reappear()
    #-------------------------------------------------------------------
#=======================================================================
def main():
    c_main = Class_STRATEG()    # init new obj !!!
    r = c_main.init_all_tbl_ARCHIV()
    #if r[0] > 0: return
    r = c_main.init_all_tbl_TODAY()
    if r[0] > 0: return
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'STEP',
                'STRT',
                'STOP',]
        serv = [
                'init_all_tbl_ARCHIV',
                'calc_ASK_BID_EMA_arc',
                'About...',]
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['Exit', ['Exit']],
                    ['Func', func ],
                    ['Serv', serv ],]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.Canvas(size=(240, 180), key='-CANVAS-')],
                  [sg.StatusBar(text= '... just STATUS Bar ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title('TEST_strat')
        #--------------------------------------------------------------#
        fig_agg = FigureCanvasTkAgg(c_main.graph_PACK.fig, window['-CANVAS-'].TKCanvas)
        fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        #--------------------------------------------------------------#
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read(timeout = c_main.tmr_RUN)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in ['__TIMEOUT__']:
            event_TIMEOUT(c_main, window, event, values)
        #
        if event in func + serv:
            event_MENU(c_main, window, event, values)
        #
        fig_agg.draw()
    return 0
if __name__ == '__main__':
    main()

