#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_tbl_HIST_FUT.py
#  
#=======================================================================
import os, sqlite3, sys
from datetime import datetime, timezone
import math
#from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
import md_tbl_CFG_PACK as cfg_pack
#=======================================================================
_db_tod   = dbs.Class_DB_SQLite()
_db_arc   = dbs.Class_DB_SQLite(prd = 'ARCH')
_consts   = dbs.Class_CNST()
_cfg_pack = cfg_pack.Class_CFG_PACK([])
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_str_FUT_PCK(): # Class_str_FUT  Class_str_PCK  Class_cfg_PCK
    def __init__(self):
        self.ind_s, self.dt = 0, ''
        self.arr = []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_HIST_FUT():
    # FOR -   ----------------------------------------------------------
    # 0. read (unpack) FUT ARCHIV & TODAY
    # 1. append FUT ARCHIV
    # 2. read (unpack) & write (pack) data PACK (ASK/BID/EMA)
    # 3. calc ASK/BID/EMA  for array PACK ARCHIV & TODAY
    #-------------------------------------------------------------------
    def __init__(self):
        self.len_arr_fut_t = 0
        self.arr_fut_t = []
        self.arr_pck_t = []
        self.arr_fut_a = []
        self.arr_pck_a = []

        self.cfg_pck  = cfg_pack.Class_CFG_PACK([])

    def view_arr_PACK(self, hist_pck, titul):
        #for item in _tod.dt_fut:
        #    print(item.sP_code, item.arr)
        mtrx = [hist_pck[0].dt + hist_pck[0].arr[0],
                hist_pck[1].dt + hist_pck[1].arr[0],
                ['-------------'],
                hist_pck[-2].dt + hist_pck[-2].arr[0],
                hist_pck[-1].dt + hist_pck[-1].arr[0],
                ]
        layout = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = _consts.head_hist_pck,
                    key      = '_hist_PACK_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'lightsteelblue',
                    )],[sg.Button('Close')],                    ]
        wnd_3 = sg.Window(titul, layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_3.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
        wnd_3.close()

    def view_arr_FUT(self, hist_fut, titul):
        #for item in _tod.dt_fut:
        #    print(item.sP_code, item.arr)
        mtrx = [hist_fut[0].dt + hist_fut[0].arr[0] + hist_fut[0].arr[1],
                hist_fut[1].dt + hist_fut[1].arr[0] + hist_fut[1].arr[1],
                ['---------------------'],
                hist_fut[-2].dt + hist_fut[-2].arr[0] + hist_fut[-2].arr[1],
                hist_fut[-1].dt + hist_fut[-1].arr[0] + hist_fut[-1].arr[1],
                ]
        layout = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = _consts.head_hist_fut,
                    key      = '_hist_FUT_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'lightsteelblue',
                    )],[sg.Button('Close')],                    ]
        wnd_3 = sg.Window(titul, layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_3.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
        wnd_3.close()
        
    def parse_hist_FUT(self, hist_fut):
        c = _consts
        #print('lench = ', len(hist_fut))
        # unpack cfg_SOFT --------------------------------------
        try:
            arr_fut = []
            for cnt, i_str in enumerate(hist_fut):
                mn_pr, mn_cr = '', ''
                if cnt == 0 :
                    mn_pr, mn_cr = '', '00'
                else:
                    mn_pr = hist_fut[cnt-1][1][14:16]
                    mn_cr = hist_fut[cnt-0][1][14:16]
                if mn_pr != mn_cr:
                    s = Class_str_FUT_PCK()
                    s.ind_s = i_str[0]
                    s.dt    = i_str[1].split('|')[0].split(' ')
                    arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                    for item in (zip(arr_buf[::2], arr_buf[1::2])):
                        s.arr.append([float(item[c.fAsk]),
                                      float(item[c.fBid])])
                    arr_fut.append(s)
                if len(arr_fut) % 1000 == 0:  print(len(arr_fut), end='\r')
            # self.prn_arr('arr_fut_t', arr_fut)
            # ok_lmb('unpack hist_FUT', s_lmb('unpack hist_FUT TODAY successfully !'))
        except Exception as ex:
            self.err_status = 'unpack_hist_FUT / try  ' + s_lmb(ex)
            print(self.err_status)
            #self.err_DB(err_log = True)
            return [1, ex]
        return [0, arr_fut]
        
    def clc_ASK_BID(self, arr_FUT):
        c = _consts
        print('=> _GL clc_ASK_BID ', len(arr_FUT))
        try:
        #_cfg_pack => self.cfg_pck
            print('kNul = ', str(self.cfg_pck.cfg_PACK[0][c.kNul]))
            b_null = True if (self.cfg_pck.cfg_PACK[0][c.kNul] == 0) else False
            print('b_null = ', b_null)
            ''' init  table ARCHIV_PACK  --------------------'''
            arr_pk  = []  # list of Class_str_FUT_PCK()
            nm_pcks = len(self.cfg_pck.cfg_PACK)
            for idx, item in enumerate(arr_FUT): # change STRINGs
                if idx % 100 == 0:  print(idx, end='\r')
                arr_bb = Class_str_FUT_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for p in range(nm_pcks):        # change PACKETs
                    ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                    for jdx, jtem in enumerate(self.cfg_pck.cfg_PACK[p][c.kKoef]): # calc PACK
                        i_koef, k_koef = jtem[0], jtem[1]
                        if k_koef > 0 :
                            ask_p +=  k_koef * item.arr[i_koef][c.fAsk]
                            bid_p +=  k_koef * item.arr[i_koef][c.fBid]
                        if k_koef < 0 :
                            ask_p +=  k_koef * item.arr[i_koef][c.fBid]
                            bid_p +=  k_koef * item.arr[i_koef][c.fAsk]

                    if idx == 0 and b_null:
                        arr_pp = [0, 0, 0, 0, 0]
                        self.cfg_pck.cfg_PACK[p][c.kNul]= int((ask_p + bid_p)/2)
                        arr_bb.arr.append(arr_pp)
                        continue
                    arr_pp = [int(ask_p - self.cfg_pck.cfg_PACK[p][c.kNul]), int(bid_p - self.cfg_pck.cfg_PACK[p][c.kNul]), 0, 0, 0]
                    arr_bb.arr.append(arr_pp)
                arr_pk.append(arr_bb)

        except Exception as ex:
            self.err_status = 'clc_ASK_BID / try  ' + s_lmb(ex)
            #self.err_DB(err_log = True)
            return [1, self.err_status]

        return [0, arr_pk]

    def clc_EMA(self, arr_pk, last_pk):
        c = _consts
        print('=> _GL clc_EMA ', len(arr_pk))
        b_null = True if (last_pk.ind_s == 0) else False
        try:
            #sg.popup('self.cfg_pck.cfg_PACK',
            #    str(self.cfg_pck.cfg_PACK[-1]))
            nm_pcks = len(self.cfg_pck.cfg_PACK)
            koef_EMA, k_EMA_rnd = [], []
            for kdx in range(nm_pcks):
                k_ema = self.cfg_pck.cfg_PACK[kdx][c.kEma]
                koef_EMA.append(round(2/(1+int(k_ema[0])),5))
                k_EMA_rnd.append(int(k_ema[1]))
            for idx, item in enumerate(arr_pk):
                if idx % 1000 == 0:  print(idx, end='\r')
                if idx == 0:
                    if not b_null:
                        arr_pk[0] = last_pk
                else:
                    for pdx, ptem in enumerate(item.arr):
                        cr = arr_pk[idx].arr[pdx]
                        pr = arr_pk[idx-1].arr[pdx]
                        cr[c.pEMAf]  = round(pr[c.pEMAf] + (int((ptem[c.pAsk] + ptem[c.pBid])/2) - pr[c.pEMAf]) * koef_EMA[pdx], 1)
                        cr[c.pEMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[c.pEMAf] / k_EMA_rnd[pdx] )
                        if pr[c.pEMAf_r] > cr[c.pEMAf_r]:
                            cr[c.pCnt_EMAf_r] = 0 if pr[c.pCnt_EMAf_r] > 0 else pr[c.pCnt_EMAf_r]-1
                        elif pr[c.pEMAf_r] < cr[c.pEMAf_r]:
                            cr[c.pCnt_EMAf_r] = 0 if pr[c.pCnt_EMAf_r] < 0 else pr[c.pCnt_EMAf_r]+1
                        else:
                            cr[c.pCnt_EMAf_r] = pr[c.pCnt_EMAf_r]
        except Exception as ex:
            self.err_status = 'clc_EMA / try  ' + s_lmb(ex)
            #self.err_DB(err_log = True)
            return [1, ex]

        return [0, arr_pk]

    def pack_arr_pck(self, arr_pk, db_pk, nm_tbl_pk):
        c = _consts
        print('=> _PACK pack_arr_pck ', nm_tbl_pk, len(arr_pk))
        try:
            pck_list = []
            #pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
            if len(arr_pk) > 0:
                for i_hist, item_hist in enumerate(arr_pk):
                    if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                    #bp()
                    buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                    buf_s = ''
                    for i_pack, item_pack in enumerate(item_hist.arr):
                        buf_s += str(item_pack[c.pAsk]) + ' ' + str(item_pack[c.pBid])   + ' '
                        buf_s += str(item_pack[c.pEMAf]) + ' ' + str(item_pack[c.pEMAf_r]) + ' '
                        buf_s += str(item_pack[c.pCnt_EMAf_r]) + '|'
                    pck_list.append((item_hist.ind_s, buf_dt + buf_s.replace('.', ',')))
            ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
            r_update = db_pk.update_tbl(nm_tbl_pk, pck_list, val = ' VALUES(?,?)')
            if r_update[0] > 0:
                self.err_status = 'pack_arr_pck / Did not update *hist_PACK*!  ' + s_lmb(r_update[1])
                #self.err_DB(err_pop = True, err_log = True)
                return [2, self.err_status]
        except Exception as ex:
            self.err_status = 'pack_arr_pck / Try error !  ' + str(ex)
            #self.err_DB(err_pop = True, err_log = True)
            return [1, self.err_status]

        return [0, pck_list]

    def unpack_str_pck(self, hist_pck):
        print('=> _GL unpack_str_pck ', len(hist_pck))
        try:
            arr_pck = []
            for cnt, i_str in enumerate(hist_pck):
                buf = i_str[1].replace(',','.').split('|')
                del buf[-1]
                s = Class_str_FUT_PCK()
                s.ind_s = i_str[0]
                for cn, item in enumerate(buf):
                    if cn == 0 : s.dt = item.split(' ')[0:2]
                    ind_0 = 0 if cn != 0 else 2
                    s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                arr_pck.append(s)
                if len(arr_pck) % 1000 == 0:  print(len(arr_pck), end='\r')

                if (len(arr_pck) == 0):
                    #for item in self.nm:
                    for item in self.cfg_pck:  arr_pck.append([])
        except Exception as ex:
            return [1, ex]
        return [0, arr_pck]
    
    def append_hist(self):
        # ATTENTION !!! list 'buf_hist' HIST 1 minute 07.00 ... 18.45
        #--- read HIST file ---
        buf_hist_arch, buf_str, frm = [], [], '%d.%m.%Y %H:%M:%S'
        path_hist = sg.PopupGetFile( 'select TXT hist file',
                title = 'append hist file from TXT in table')
        if path_hist != None:
            try:
                with open(path_hist,"r") as fh:
                    buf_str = fh.read().splitlines()
                #--- create list 'buf_hist' HIST 1 minute 07.00 ... 18.45
                mn_pr, mn_cr, buf_hist = '', '00', []
                for cnt, item in enumerate(buf_str):
                    h_m_s = item.split('|')[0].split(' ')[1].split(':')
                    mn_cr = h_m_s[1]
                    if int(h_m_s[0]) < 7: continue
                    if int(h_m_s[0]) > 23: break
                    if mn_pr != mn_cr:
                        buf_hist.append(item)
                    mn_pr = mn_cr
                #--- prepaire 'buf_hist' for update table 'hist_fut' ---
                for item in buf_hist:
                    dtt_cr = datetime.strptime(item.split('|')[0], frm)
                    ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
                    buf_hist_arch.append([ind_sec, item])
                #--- db_ARCHV.update_tbl -------------------------------
                rep = _db_arc.update_tbl('hist_FUT', buf_hist_arch, val = ' VALUES(?,?)', p_append = True)

            except Exception as ex:
                err_lmb('append_hist_FUT_ARCHIV', s_lmb('Error  TRY!') + str(ex))
                return

    def get_period_hist_pack(self, db_pk_arch, db_pk_today, period_days):
        #--- read ALL hist_FUT archiv  -----------------------------
        req = db_pk_today.read_tbl('hist_PACK')
        if req[0] > 0:
            #_gl.err_status = 'GRAPH_One_PACK / Not read db_ARCHV *hist_PACK*!  ' + s_lmb(req[1])
            #_gl.err_DB(err_pop = True, err_log = True)
            return [1, req[1]]
        rep = db_pk_arch.read_tbl('hist_PACK')
        if rep[0] > 0:
            #_gl.err_status = 'GRAPH_One_PACK / Not read db_ARCHV *hist_PACK*!  ' + s_lmb(rep[1])
            #_gl.err_DB(err_pop = True, err_log = True)
            return [1, rep[1]]
        #
        period_tm = period_days
        index_last_day = len(rep[1])
        df = rep[1][-1][1].split('|')[0].split(' ')[0]
        #print('df = ', df)
        for item in reversed(rep[1]):
            index_last_day -= 1
            if item[1].split('|')[0].split(' ')[0] != df:
                df = item[1].split('|')[0].split(' ')[0]
                period_tm -= 1
            if period_tm == 0:
                break
        index_last_day += 1
        req = self.unpack_str_pck(rep[1][index_last_day:] + req[1])
        print('req[1][0] => ',req[1][0])
        if req[0] > 0:
            #err_lmb('main', s_lmb('Error unpack_str_pck!') + s_lmb(req[1]))
            return [1, req[1]]
        else:
            return [0, req[1]]

def event_MENU(tbl_hist_FUT, wndw, ev, val):
    c = _consts
    #----------------------------------------
    if ev == 'clr_hist_PACK_tbls_today':
        tbl_hist_FUT.arr_pck_t = []
        rep = _db_tod.update_tbl('hist_PACK', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_PACK* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_PACK* !' + rep[1])
    #----------------------------------------
    if ev == 'clr_hist_FUT_tbls_today':
        tbl_hist_FUT.arr_fut_t = []
        rep = _db_tod.update_tbl('hist_FUT', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_FUT* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_FUT* !' + rep[1])
    #----------------------------------------
    if ev == 'clr_hist_FUT_tbls_arch':
        tbl_hist_FUT.arr_fut_a = []
        rep = _db_arc.update_tbl('hist_FUT', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_FUT* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_FUT* !' + rep[1])
    #----------------------------------------
    if ev == 'clr_hist_PACK_tbls_arch':
        tbl_hist_FUT.arr_pck_a = []
        rep = _db_arc.update_tbl('hist_PACK', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_PACK* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_PACK* !' + rep[1])
    #----------------------------------------
    if ev == 'view_hist_FUT_tod':
        wndw.disappear()
        # 1.Read ALL data from DB today
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'hist_FUT':
                    # 2.Parsing data from table 'hist_FUT'
                    res = tbl_hist_FUT.parse_hist_FUT(item[1])
                    if res[0] == 0:
                        tbl_hist_FUT.arr_fut_t = res[1]
                        arr = tbl_hist_FUT.arr_fut_t
                        if len(arr) < 5:
                            sg.popup('view_hist_FUT_tod',
                                     'Lench of arr_fut_t is too small',
                                     '   less then 5',
                                     'LEN(arr_fut_t) = ' + str(len(arr)),
                                     grab_anywhere=True)
                        else:
                            sg.popup('view_hist_FUT_tod',
                                     str(arr[0].dt),
                                     str(arr[1].dt),
                                     '.........',
                                     str(arr[-1].dt),
                                     grab_anywhere=True)
                    else:
                        err_lmb('view_hist_FUT_tod',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'calc_ASK_BID_tod':
        wndw.disappear()
        # 1.Read ALL data from DB today
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'cfg_PACK':
                    # 2.Parsing data from table 'cfg_PACK'
                    res = _cfg_pack.parse_cfg_PACK(item[1])
                    # 3. Calc ASK/BID arr_pck_t  for  arr_fut_t
                    #    LEN(arr_fut_t) should be not ZERO !!!
                    res = tbl_hist_FUT.clc_ASK_BID(tbl_hist_FUT.arr_fut_t)
                    if res[0] == 0:
                        sg.popup_ok(s_lmb('calc_ASK_BID_tod successfully !'),
                                background_color='LightGreen', title='main')
                        tbl_hist_FUT.arr_pck_t = res[1]
                        print('tbl_hist_FUT.arr_pck_t = ', len(tbl_hist_FUT.arr_pck_t))
                        sg.popup('view_hist_PACK 1 last day',
                            str(tbl_hist_FUT.arr_pck_t[-1]))
                        #--- calc EMA hist_PACK today  -----------------
                        sg.popup('tbl_hist_FUT.cfg_pck',
                            str(tbl_hist_FUT.cfg_pck.cfg_PACK[-1]))
                        print('tbl_hist_FUT.arr_pck_a = ', len(tbl_hist_FUT.arr_pck_a))
                        rep = tbl_hist_FUT.clc_EMA(tbl_hist_FUT.arr_pck_t, tbl_hist_FUT.arr_pck_a[-1])
                        if rep[0] > 0:
                            err_lmb('clc_EMA ARCHIV => ',rep[1])
                        else:
                            tbl_hist_FUT.arr_pck_t = rep[1][1:]
                            sg.popup_ok(s_lmb('clc_EMA successfully !'),
                                    background_color='LightGreen', title='main')
                        # 4. PACK & UPDATE arr_pck_t => update table hist_PACK (today)
                        rep = tbl_hist_FUT.pack_arr_pck(tbl_hist_FUT.arr_pck_t, _db_tod, 'hist_PACK')
                        if rep[0] == 0:
                            sg.popup_ok(s_lmb('pack_arr_pck TODAY successfully !'),
                                    background_color='LightGreen', title='main')
                        else:
                            err_lmb('pack_arr_pck TODAY => ',rep[1])
                    else:
                        err_lmb('calc_ASK_BID_tod',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'append_hist_FUT_arc':
        tbl_hist_FUT.append_hist()
    #----------------------------------------
    if ev == 'view_hist_FUT_arc':
        wndw.disappear()
        res = _db_arc.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'hist_FUT':
                    # 2.Parsing data from table 'hist_FUT'
                    res = tbl_hist_FUT.parse_hist_FUT(item[1])
                    if res[0] == 0:
                        tbl_hist_FUT.arr_fut_a = res[1]
                        arr = tbl_hist_FUT.arr_fut_a
                        if len(arr) < 5:
                            sg.popup('view_hist_FUT_tod',
                                     'Lench of arr_fut_t is too small',
                                     '   less then 5',
                                     'LEN(arr_fut_t) = ' + str(len(arr)),
                                     grab_anywhere=True)
                        else:
                            sg.popup('view_hist_FUT_tod',
                                     str(arr[0].dt),
                                     str(arr[1].dt),
                                     '.........',
                                     str(arr[-1].dt),
                                     grab_anywhere=True)
                    else:
                        err_lmb('view_hist_FUT_tod',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'calc_ASK_BID_arc':
        wndw.disappear()
        # 1.Read ALL data from DB arch
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'cfg_PACK':
                    # 2.Parsing data from table 'cfg_PACK'
                    res = _cfg_pack.parse_cfg_PACK(item[1])
                    #sg.popup('_cfg_pack',
                        #str(_cfg_pack.cfg_PACK[-1]))
                    #sg.popup('tbl_hist_FUT.cfg_pck',
                        #str(tbl_hist_FUT.cfg_pck.cfg_PACK[-1]))
                    # 3. Calc ASK/BID arr_pck_t  for  arr_fut_t
                    #--- prepair kNul to calc hist_PACK archiv -----------------
                    for i in range(len(tbl_hist_FUT.cfg_pck.cfg_PACK)):
                        tbl_hist_FUT.cfg_pck.cfg_PACK[i][c.kNul] = 0
                    res = tbl_hist_FUT.clc_ASK_BID(tbl_hist_FUT.arr_fut_a)
                    if res[0] == 0:
                        sg.popup_ok(s_lmb('calc_ASK_BID  successfully !'),
                                background_color='LightGreen', title='main')
                        tbl_hist_FUT.arr_pck_a = res[1]
                        print('tbl_hist_FUT.arr_pck_a = ', len(tbl_hist_FUT.arr_pck_a))
                        sg.popup('view_hist_PACK 1 last day',
                            str(tbl_hist_FUT.arr_pck_a[-1]))
                        #--- calc EMA hist_PACK archiv  ----------------------------
                        sg.popup('tbl_hist_FUT.cfg_pck',
                            str(tbl_hist_FUT.cfg_pck.cfg_PACK[-1]))
                        rep = tbl_hist_FUT.clc_EMA(tbl_hist_FUT.arr_pck_a, Class_str_FUT_PCK())
                        if rep[0] > 0:
                            #self.err_status = 'calc_arr_pck / Did not CALC EMA *hist_PACK*!  ' + s_lmb(rep[1])
                            #self.err_DB(err_pop = True, err_log = True)
                            #return [4, self.err_status]
                            err_lmb('clc_EMA ARCHIV => ',rep[1])
                        else:
                            tbl_hist_FUT.arr_pck_a = rep[1]
                            sg.popup_ok(s_lmb('clc_EMA successfully !'),
                                    background_color='LightGreen', title='main')
                        # 4. PACK & UPDATE arr_pck_t => update table hist_PACK (today)
                        rep = tbl_hist_FUT.pack_arr_pck(tbl_hist_FUT.arr_pck_a, _db_arc, 'hist_PACK')
                        if rep[0] == 0:
                            sg.popup_ok(s_lmb('pack_arr_pck ARCHIV successfully !'),
                                    background_color='LightGreen', title='main')
                        else:
                            err_lmb('pack_arr_pck ARCHIV => ',rep[1])
                    else:
                        err_lmb('calc_ASK_BID_arc',res[1])
        wndw.reappear()
    #----------------------------------------
    if ev == 'get_period_hist_pack_1':
        wndw.disappear()
        res = tbl_hist_FUT.get_period_hist_pack(_db_arc, _db_tod, 1)
        if res[0] == 0:
            tbl_hist_FUT.view_arr_PACK(res[1], 'view_hist_PACK 1 last day')
        wndw.reappear()
    #----------------------------------------
    if ev == 'get_period_hist_pack_3':
        wndw.disappear()
        res = tbl_hist_FUT.get_period_hist_pack(_db_arc, _db_tod, 3)
        if res[0] == 0:
            tbl_hist_FUT.view_arr_PACK(res[1], 'view_hist_PACK 3 last days')
        wndw.reappear()
    #----------------------------------------
    if ev == 'get_period_hist_pack_0':
        wndw.disappear()
        res = tbl_hist_FUT.get_period_hist_pack(_db_arc, _db_tod, 0)
        if res[0] == 0:
            tbl_hist_FUT.view_arr_PACK(res[1], 'view_hist_PACK 0 last days')
        wndw.reappear()
    #----------------------------------------
    if ev == 'get_period_hist_pack_333':
        wndw.disappear()
        res = tbl_hist_FUT.get_period_hist_pack(_db_arc, _db_tod, 333)
        if res[0] == 0:
            tbl_hist_FUT.view_arr_PACK(res[1], 'view_hist_PACK 333 last days')
        wndw.reappear()
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
#=======================================================================
def main():
    tbl_hist_FUT = Class_HIST_FUT()
    tbl_hist_FUT.cfg_pck = _cfg_pack
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'clr_hist_FUT_tbls_arch',
                'clr_hist_PACK_tbls_arch',
                'append_hist_FUT_arc',
                'view_hist_FUT_arc',
                'calc_ASK_BID_arc',
                '---',
                'clr_hist_FUT_tbls_today',
                'clr_hist_PACK_tbls_today',
                'view_hist_FUT_tod',
                'calc_ASK_BID_tod',
                '---',
                'get_period_hist_pack_0',
                'get_period_hist_pack_1',
                'get_period_hist_pack_3',
                'get_period_hist_pack_333',
                '---',
                'About...',]
        #---------------------------------------------------------------
        # !!! move INIT-block into class Class_DATA_HIST  ???
        res = _db_arc.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if item[0] == 'hist_FUT':
                    if len(item[1]) > 0:
                        print('arr_fut_a = ', len(item[1]))
                        res = tbl_hist_FUT.parse_hist_FUT(item[1])
                        if res[0] == 0:
                            tbl_hist_FUT.arr_fut_a = res[1]
                            tbl_hist_FUT.view_arr_FUT(res[1], 'arr_fut_a')
                        else:
                            err_lmb('error INIT hist_FUT_arc',res[1])
                if item[0] == 'hist_PACK':
                    if len(item[1]) > 0:
                        print('arr_pck_a = ', len(item[1]))
                        req = tbl_hist_FUT.unpack_str_pck(item[1])
                        if req[0] == 0:
                            tbl_hist_FUT.arr_pck_a = req[1]
                            tbl_hist_FUT.view_arr_PACK(req[1], 'arr_pck_a')
                        else:
                            err_lmb('error INIT hist_PACK_arc',req[1])
        else:
            err_lmb('_db_arc ERR',res[1])
        #
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                #if item[0] == 'cfg_SOFT':
                    #_cfg_soft.parse_cfg_SOFT(item[1])
                    #_cfg_soft.view_cfg_SOFT()
                if item[0] == 'cfg_PACK':
                    if len(item[1]) > 0:
                        print('_cfg_pack = ', len(item[1]))
                        _cfg_pack.parse_cfg_PACK(item[1])
                        _cfg_pack.view_cfg_PACK()
                #if item[0] == 'data_FUT':
                    #_data_fut.parse_data_FUT(item[1])
                    #_data_fut.view_data_FUT()
                    #_data_fut.view_ACOUNT()
                if item[0] == 'hist_FUT':
                    if len(item[1]) > 0:
                        print('arr_fut_t = ', len(item[1]))
                        res = tbl_hist_FUT.parse_hist_FUT(item[1])
                        if res[0] == 0:
                            tbl_hist_FUT.arr_fut_t = res[1]
                            tbl_hist_FUT.view_arr_FUT(res[1], 'arr_fut_t')
                        else:
                            err_lmb('error INIT hist_FUT_tod',res[1])
                if item[0] == 'hist_PACK':
                    if len(item[1]) > 0:
                        print('arr_pck_t = ', len(item[1]))
                        req = tbl_hist_FUT.unpack_str_pck(item[1])
                        if req[0] == 0:
                            tbl_hist_FUT.arr_pck_t = req[1]
                            tbl_hist_FUT.view_arr_PACK(req[1], 'arr_pck_t')
                        else:
                            err_lmb('error INIT hist_PACK_tod',req[1])
        else:
            err_lmb('_db_tod ERR',res[1])
        #---------------------------------------------------------------
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
        window.set_title('py_hist_FUT_class')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(tbl_hist_FUT, window, event, values)
    return 0

if __name__ == '__main__':
    main()

