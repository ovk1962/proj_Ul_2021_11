#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_GRAPH_0_2.py
#  
#=======================================================================
import os, sqlite3, sys
from datetime import datetime, timezone
#from prettytable import PrettyTable
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
import md_tbl_HIST_FUT as tbl_hist_fut_pack
import md_tbl_CFG_PACK as cfg_pack
#=======================================================================
_consts   = dbs.Class_CNST()
_db_tod   = dbs.Class_DB_SQLite()
_db_arc   = dbs.Class_DB_SQLite(prd = 'ARCH')
_tbl_fut_pack = tbl_hist_fut_pack.Class_HIST_FUT()
_cfg_pack = cfg_pack.Class_CFG_PACK([])
#=======================================================================
locationXY = (100, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_GRAPH():
    def __init__(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.fig.subplots_adjust(left=0.07, right=0.94, bottom=0.1, top=0.9)
        self.ax  = self.fig.add_subplot(111)
        self.ax2 = self.ax.twinx()
        self.arr_graph = []

    def draw_graph(self, num_packet, discret, num_points, legend):
        #num_packet = 0
        #discret = 1 # time period 5 minutes ... from 1 to 60

        x, y_ASK, y_BID, y_EMA, y_EMAr, y_CNT = [], [], [], [], [], []
        arr_pk_gr = list(item.arr[num_packet] for item in self.arr_graph)[num_points::discret]
        x = list(item.dt[1] + '\n' + item.dt[0] for item in self.arr_graph)[num_points::discret]
        y_ASK = list(item[0] for item in arr_pk_gr)
        y_BID = list(item[1] for item in arr_pk_gr)
        y_EMA = list(item[2] for item in arr_pk_gr)
        y_EMAr = list(item[3] for item in arr_pk_gr)
        y_CNT  = list(item[4] for item in arr_pk_gr)

        self.ax.cla()
        self.ax2.cla()

        self.ax.set_title(legend + '.png   ') # + v['-NUM_PACK-'])
        self.ax.tick_params(axis='x', which='major', labelsize=6)
        self.ax.tick_params(axis='y', which='major', labelsize=10)

        self.ax.grid(axis = 'both')
        self.ax2.grid(False)
        self.ax2.set_xticks([])
            
        self.ax.scatter(x, y_ASK, c='red',   label='ASK', s=3) # alpha=0.3, edgecolors='none')
        self.ax.scatter(x, y_BID, c='blue',  label='BID', s=3) # alpha=0.3, edgecolors='none')
        self.ax.scatter(x, y_EMA, c='green', label='y_EMA', alpha=0.5,  s=3) # alpha=0.5, edgecolors='none')
        self.ax.plot(x, y_EMAr, c='black', label='y_EMAr', alpha=0.75,  linewidth=3) # alpha=0.5, edgecolors='none')

        self.ax2.plot(x, y_CNT, color = (0.1, 0.2, 0.9, 0.5), linewidth = 5, label='CNT')
        #ax2.scatter(x, y_CNT, c='green', label='CNT', alpha=0.75,  s=3) # alpha=0.3, edgecolors='none')

        self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))

        self.ax.legend(loc='upper left')
        self.ax2.legend(loc='upper right')
#=======================================================================
class Class_GRAPH_s():
    def __init__(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.fig.subplots_adjust(left=0.07, right=0.94, bottom=0.1, top=0.9)
        self.ax  = self.fig.add_subplot(111)
        self.arr_graph = []

    def draw_graph(self, num_packet, discret, num_points, legend):
        #num_packet = 0
        #discret = 1 # time period 5 minutes ... from 1 to 60

        x, y_ASK_BID, y_EMA = [], [], []
        arr_pk_gr = list(item.arr[num_packet] for item in self.arr_graph)[num_points::discret]
        x = list(item.dt[1] + '\n' + item.dt[0] for item in self.arr_graph)[num_points::discret]
        y_ASK_BID = list(int(item[0] + item[1])/2 for item in arr_pk_gr)
        y_EMA = list(item[2] for item in arr_pk_gr)

        self.ax.cla()

        self.ax.set_title(legend + '.png   ') # + v['-NUM_PACK-'])
        self.ax.tick_params(axis='x', which='major', labelsize=6)
        self.ax.tick_params(axis='y', which='major', labelsize=10)

        self.ax.grid(axis = 'both')
            
        #self.ax.scatter(x, y_ASK, c='red',   label='ASK', s=3) # alpha=0.3, edgecolors='none')
        #self.ax.scatter(x, y_BID, c='blue',  label='BID', s=3) # alpha=0.3, edgecolors='none')
        self.ax.scatter(x, y_ASK_BID, c='blue',  label='ASK_BID', s=3) # alpha=0.3, edgecolors='none')
        #self.ax.scatter(x, y_EMA, c='green', label='y_EMA', alpha=0.5,  s=3) # alpha=0.5, edgecolors='none')
        self.ax.plot(x, y_EMA, c='green', label='y_EMA', alpha=0.25,  linewidth=7) # alpha=0.5, edgecolors='none')
        #self.ax.plot(x, y_EMAr, c='black', label='y_EMAr', alpha=0.75,  linewidth=3) # alpha=0.5, edgecolors='none')

        self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))

        self.ax.legend(loc='upper left')
        #self.ax2.legend(loc='upper right')
#=======================================================================
class Class_GRAPH_bar():
    def __init__(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.fig.subplots_adjust(left=0.02, right=0.93, bottom=0.1, top=0.9)
        self.ax  = self.fig.add_subplot(111)
        self.ax2 = self.ax.twinx()
        self.arr_graph = []
        
    def draw_graph(self, num_packet, discret, num_points, legend):
        #num_packet = 0
        #discret = 1 # time period 5 minutes ... from 1 to 60

        x, y_ASK_BID, y_EMA = [], [], []
        arr_pk_gr = list(item.arr[num_packet] for item in self.arr_graph)[num_points::discret]
        x = list(item.dt[1] + '\n' + item.dt[0] for item in self.arr_graph)[num_points::discret]
        y_ASK_BID = list(int(item[0] + item[1])/2 for item in arr_pk_gr)
        y_EMA = list(item[2] for item in arr_pk_gr)
        ASK_last  = str(arr_pk_gr[-1][0])
        BID_last  = str(arr_pk_gr[-1][1])
        TIME_last = self.arr_graph[-1].dt[1]
        
        x_bar, y_top_bar, y_bot_bar, y_ema_bar = [], [], [], []
        per = 10
        #sg.popup_ok('len(x)', s_lmb(str(len(x))),
            #background_color='Coral', title='test_001')
        for i, item in enumerate (x[per-1::per]):
            #sg.popup_ok('i, item',
                #s_lmb(str(i)), s_lmb(item), s_lmb(str(i*per)), y_ASK_BID[i*per:per+i*per],
                #s_lmb(str(max(y_ASK_BID[i*per:per+i*per]))),
                #s_lmb(str(min(y_ASK_BID[i*per:per+i*per]))),
                #background_color='Coral', title='test_001')
            x_bar.append(item)
            y_ema_bar.append(y_EMA[i*per])
            y_top_bar.append((max(y_ASK_BID[i*per:per+i*per]))-(min(y_ASK_BID[i*per:per+i*per])))
            y_bot_bar.append((min(y_ASK_BID[i*per:per+i*per])))

        self.ax.cla()
        self.ax2.cla()

        self.ax.grid(axis = 'both')
        self.ax2.grid(axis = 'both')
        #self.ax2.grid(False)
        #self.ax2.set_xticks([])
        
        self.ax.set_title(legend + '.png   TIME=' + TIME_last + '  ASK=' + ASK_last + '  BID=' + BID_last)
        self.ax.tick_params(axis='x', which='major', labelsize=6)
        self.ax.tick_params(axis='y', which='major', labelsize=6)
        self.ax.yaxis.set_major_locator(mpl.ticker.LinearLocator(1))
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(11))
        
        #self.ax2.tick_params(axis='x', which='major', labelsize=4)
        self.ax2.tick_params(axis='y', which='major', labelsize=8)
        self.ax2.xaxis.set_major_locator(plt.MaxNLocator(11))
        
        self.ax2.bar(x_bar, y_top_bar, bottom = y_bot_bar)
        #self.ax.bar(x_bar, y_bot_bar)
        #self.ax.scatter(x, y_ASK, c='red',   label='ASK', s=3) # alpha=0.3, edgecolors='none')
        #self.ax.scatter(x, y_BID, c='blue',  label='BID', s=3) # alpha=0.3, edgecolors='none')
        #self.ax.scatter(x, y_ASK_BID, c='blue',  label='ASK_BID', s=3) # alpha=0.3, edgecolors='none')
        #self.ax.scatter(x, y_EMA, c='green', label='y_EMA', alpha=0.5,  s=3) # alpha=0.5, edgecolors='none')
        self.ax2.plot(x_bar, y_ema_bar, c='green', label='y_EMA', alpha=0.25,  linewidth=7) # alpha=0.5, edgecolors='none')
        #self.ax.plot(x, y_EMAr, c='black', label='y_EMAr', alpha=0.75,  linewidth=3) # alpha=0.5, edgecolors='none')



        #self.ax.legend(loc='upper left')
        self.ax2.legend(loc='upper left')
#=======================================================================

def event_MENU(graph_PACK, wndw, ev, val):
    #----------------------------------------
    if ev == 'About':
        wndw.disappear()
        sg.popup('About this program  Ver 0.0',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 '"Matplotlib Ver  ' + str(mpl.__version__),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'view_p0_graph_1_day':
        res = _tbl_fut_pack.get_period_hist_pack(_db_arc, _db_tod, 1)
        if res[0] == 0:
            _tbl_fut_pack.view_arr_PACK(res[1], 'view_hist_PACK 1 last day')
            graph_PACK.arr_graph = res[1]
            i = 9
            titul = '1_' + _cfg_pack.cfg_PACK[i][_consts.kNm]
            graph_PACK.draw_graph(i, 1, 0, titul)
            graph_PACK.fig.savefig('c:\\1_pack_' + str(i) + '.png')
            print(titul)
    #----------------------------------------
    if ev == 'view_graph_1_day':
        res = _tbl_fut_pack.get_period_hist_pack(_db_arc, _db_tod, 1)
        if res[0] == 0:
            _tbl_fut_pack.view_arr_PACK(res[1], 'view_hist_PACK 1 last day')
            graph_PACK.arr_graph = res[1]
            for i in range(len(res[1][0].arr)):
                titul = '1_' + _cfg_pack.cfg_PACK[i][_consts.kNm]
                graph_PACK.draw_graph(i, 1, 0, titul)
                graph_PACK.fig.savefig('c:\\1_pack_' + str(i) + '.png')
                print(titul)
    #----------------------------------------
    if ev == 'view_graph_99_day':
        res = _tbl_fut_pack.get_period_hist_pack(_db_arc, _db_tod, 99)
        if res[0] == 0:
            _tbl_fut_pack.view_arr_PACK(res[1], 'view_hist_PACK 99 last days')
            graph_PACK.arr_graph = res[1]
            for i in range(len(res[1][0].arr)):
                titul = '10_' + _cfg_pack.cfg_PACK[i][_consts.kNm]
                graph_PACK.draw_graph(i, 5, 0, titul)
                graph_PACK.fig.savefig('c:\\10_pack_' + str(i) + '.png')
                print(titul)
    #----------------------------------------
#=======================================================================
def event_TIMEOUT(graph_PACK, wndw, ev, val):
    wndw.disappear()
    os.system('cls')  # on windows
    #
    res = _tbl_fut_pack.get_period_hist_pack(_db_arc, _db_tod, 1)
    if res[0] == 0:
        #_tbl_fut_pack.view_arr_PACK(res[1], 'view_hist_PACK 1 last day')
        graph_PACK.arr_graph = res[1]
        for i in range(len(res[1][0].arr)):
            titul = '1_' + _cfg_pack.cfg_PACK[i][_consts.kNm]
            graph_PACK.draw_graph(i, 1, 0, titul)
            graph_PACK.fig.savefig('c:\\1_pack_' + str(i) + '.png')
            print(titul)
    wndw.reappear()
#=======================================================================
def main():
    res = _db_tod.read_all_tbl()
    if res[0] == 0:
        for item in res[1]:
            if item[0] == 'cfg_PACK':
                if len(item[1]) > 0:
                    #print('_cfg_pack = ', item[1][0])
                    _cfg_pack.parse_cfg_PACK(item[1])
                    _cfg_pack.view_cfg_PACK()
                    print('_cfg_pack = ', _cfg_pack.cfg_PACK[0][_consts.kNm])
    graph_PACK = Class_GRAPH_bar()
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'view_p0_graph_1_day',
                'view_graph_1_day',
                'view_graph_99_day',
                '---',
                'About',]
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['Exit', ['Exit']],
                    ['Func', func ],]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.Canvas(size=(240, 180), key='-CANVAS-')],
                  #[sg.Button(' REFRESH ', key='-REFRESH_GRAPH_One_PACK-')],
                  [sg.StatusBar(text= '... just STATUS Bar ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('window title', layout, finalize=True,
                            no_titlebar=False, location=locationXY)
        window.set_title('md_GRAPH_0_0')
        #--------------------------------------------------------------#
        fig_agg = FigureCanvasTkAgg(graph_PACK.fig, window['-CANVAS-'].TKCanvas)
        fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        #--------------------------------------------------------------#
        break
    while True: #--- Main Cycle ---------------------------------------#
        window['-STATUS_BAR-'].update('Ready', background_color = 'LightGreen')
        #event, values = window.read() # .read(timeout = 1000)
        event, values = window.read(timeout = 580000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in ['__TIMEOUT__']:
            event_TIMEOUT(graph_PACK, window, event, values)
            fig_agg.draw()
        #
        if event in func:
            window['-STATUS_BAR-'].update('Hold on ...', background_color = 'Pink')
            event_MENU(graph_PACK, window, event, values)
            fig_agg.draw()


    return 0

if __name__ == '__main__':
    main()

