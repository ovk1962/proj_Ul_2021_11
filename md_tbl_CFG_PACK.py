#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_tbl_CFG_PACK.py
### calc_cfg_pack  could be calculate for 'dt_fut'
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
#from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
import md_tbl_DATA_FUT as tbl_data_fut
#=======================================================================
_db_tod = dbs.Class_DB_SQLite()
_consts = dbs.Class_CNST()
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_CFG_PACK():
    def __init__(self, lst_cfg_PACK):
        self.lst_cfg_PACK = lst_cfg_PACK
        self.cfg_PACK     = []
        if len(self.lst_cfg_PACK) != 0:
            self.parse_cfg_PACK(self.lst_cfg_PACK)

    def parse_cfg_PACK(self, lst_cfg):
        #print(lst_cfg)
        #print('lench = ', len(lst_cfg))
        self.cfg_PACK = []
        c = _consts
        for item in lst_cfg:
            #print(item)
            arr_k    = item[c.kKoef].split(',')
            arr_koef, buf = [], []
            for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
            buf = [item[c.kNm],
                    arr_koef,
                    int(item[c.kNul]),
                    [int(e) for e in item[c.kEma].split(':')],
                    int(item[c.kGo]),
                    int(item[c.kPos]),
                    int(item[c.kNeg])]
            while len(c.head_cfg_pack)-1 > len(buf):
                buf.append('')
            self.cfg_PACK.append(buf)
        #print(80*'=')
        #for ppp in self.cfg_PACK: print(ppp)

    def calc_cfg_PACK(self, dt_fut):
        c = _consts
        print('lench = ', len(dt_fut.dt_fut))
        if len(dt_fut.dt_fut) == 0:
            err_lmb('calc_cfg_PACK', 'LEN dt_fut = 0 \n should be init')
            return
        # calc_cfg_pack  +++++++++++++++++++++++++++++++
        mtrx = []
        for item in dt_fut.dt_fut:
            mtrx.append([item[0]] + item[1])
        # kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
        # kKoef => [0, 2, 'SR'] =>  list =>
        #           0 -index FUT   1 - number fut's  2 - name fut
        cfg_go_pos_neg = []
        for item in self.cfg_PACK:
            pck_go, pck_pos, pck_neg = 0, 0, 0
            #print(item[c.kKoef])
            for pck in item[c.kKoef]:
                prc = int((mtrx[pck[0]][c.sAsk] + mtrx[pck[0]][c.sBid])/2)
                if pck[0] != 9:     # it's not MXI fut !!!
                    pck_go += int(abs(pck[1]) * mtrx[pck[0]][c.sFut_go])
                else:
                    pck_go += int(abs(pck[1]/10) * mtrx[pck[0]][c.sFut_go])
                if pck[1] > 0:  pck_pos += int(prc * pck[1])
                else:           pck_neg += int(prc * abs(pck[1]))
            cfg_go_pos_neg.append( [pck_go, pck_pos, pck_neg] )
        for i, item in enumerate(cfg_go_pos_neg):
            self.cfg_PACK[i][-3:] = item
            
    def view_cfg_PACK(self):
        c = _consts
        def checked_select_row():
            if len(v['_CFG_PACK_table_']) == 0:
                #wrn_lmb('event_menu_CFG_PACK', '\n You MUST choise ROW !\n')
                sg.PopupOK('\n You MUST choise ROW !\n',
                    title='event_menu_CFG_PACK', background_color = 'Gold',
                    no_titlebar = False, keep_on_top=True)
                return False
            return True

        mtrx = []
        for item in self.cfg_PACK:
            ratio = str(round(item[c.kPos]/item[c.kNeg],2))
            mtrx.append(item + [ratio])

        layout = [[sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 35),
                            headings = c.head_cfg_pack,
                            key      = '_CFG_PACK_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'coral',
                            )],
                        [#sg.Button(' READ ', key='-READ_CFG_PACK-'),
                         sg.Button(' EDIT ', key='-EDIT_CFG_PACK-'),
                         sg.Button(' ADD  ', key='-ADD_CFG_PACK-' ),
                         sg.Button(' DEL  ', key='-DEL_CFG_PACK-' ),
                         sg.Button(' SAVE ', key='-SAVE_CFG_PACK-'),
                         sg.T(90*' '), sg.Button('Close')],]

        wnd_4 = sg.Window('DB_TABL / CONF_PACK_TABL', layout, no_titlebar=False, modal=True)

        while True: #--- Main Cycle -----------------------------------#
            e, v = wnd_4.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
            #-----------------------------------------------------------
            # You must calc_cfg_pack After EDIT/CHANGE parametrs PACKET
            #-----------------------------------------------------------
            #-----------------------------------------------------------
            if e == '-EDIT_CFG_PACK-' and checked_select_row():
                print('-EDIT_CFG_PACK-')
                slct = self.cfg_PACK[v['_CFG_PACK_table_'][0]]
                chng = c.head_cfg_pack[:]
                for i, item in enumerate(slct):
                    print(item)
                    if i in [c.kNm, c.kKoef, c.kEma]:
                        pop_txt = item
                        if i == c.kKoef:
                            pop_txt = ''
                            for ss in item:
                                pop_txt += ':'.join((str(s) for s in ss)) + ','
                            pop_txt = pop_txt[:-1]
                        if i == c.kEma:
                            pop_txt = ':'.join(str(s) for s in item)
                        txt = sg.PopupGetText(c.head_cfg_pack[i],
                                    size=(95,1), default_text = pop_txt)
                        if (txt == None) or (txt == pop_txt): chng[i] = item
                        else:
                            if i == c.kNm:
                                chng[i] = txt
                            if i == c.kKoef:
                                arr_k    = txt.split(',')
                                arr_koef = []
                                for item_k in arr_k:
                                    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                                chng[i] = arr_koef
                            if i == c.kNul or i == c.kGo or i == c.kPos or i == c.kNeg:
                                if txt.isdigit():   chng[i] = int(txt)
                                else:               chng[i] = item
                            if i == c.kEma:
                                chng[i] = [int(e) for e in txt.split(':')]
                    else:
                        chng[i] = item
                    print(chng[i], pop_txt)
                self.cfg_PACK[v['_CFG_PACK_table_'][0]] = chng
                wnd_4.FindElement('_CFG_PACK_table_').Update(self.cfg_PACK)
                slct = self.cfg_PACK[v['_CFG_PACK_table_'][0]]
                e = '-SAVE_CFG_PACK-'
            #-----------------------------------------------------------
            if e == '-ADD_CFG_PACK-' and checked_select_row():
                print('-ADD_CFG_PACK-')
                slct = self.cfg_PACK[v['_CFG_PACK_table_'][0]]
                self.cfg_PACK.append(slct)
                print('append slct  ', slct)
                print('len cfg_PACK => ', len(self.cfg_PACK))
                wnd_4.FindElement('_CFG_PACK_table_').Update(self.cfg_PACK)
                e = '-SAVE_CFG_PACK-'
            #-----------------------------------------------------------
            if e == '-DEL_CFG_PACK-' and checked_select_row():
                print('-DEL_CFG_PACK-')
                del self.cfg_PACK[v['_CFG_PACK_table_'][0]]
                wnd_4.FindElement('_CFG_PACK_table_').Update(self.cfg_PACK)
                e = '-SAVE_CFG_PACK-'
            #-----------------------------------------------------------
            if e == '-SAVE_CFG_PACK-':
                print('-SAVE_CFG_PACK-')
                rep = self.update_tbl_cfg_pack()
                if rep[0] > 0:
                    print('Did not update cfg_PACK!  => ', rep[0])
                    err_lmb('event_menu_CFG_PACK', s_lmb('Did not update cfg_PACK!') + s_lmb(rep[1]))
                else:
                    #ok_lmb('event_menu_CFG_PACK','Updated *cfg_PACK* successfully !')
                    sg.popup_ok(s_lmb('Updated *cfg_PACK* successfully !'),
                            background_color='LightGreen', title='main')
        wnd_4.close();
        
    def update_tbl_cfg_pack(self):
        kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
        head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go', 'pos', 'neg', 'ratio']
        print('=> update_tbl_cfg_pack ')
        try:
            cfg_lst, cfg = [], self.cfg_PACK
            #  ['pack1', [[0, 3, 'SR'], [1, 2, 'GZ']], 7517, [1111, 150], 0, 0, 0]
            #  ['pack1', '0:3:SR,1:2:GZ', 7517, '1111:150', 0, 0, 0]
            for j in range(len(cfg)):
                str_koef = ''
                for ss in cfg[j][kKoef]:
                    str_koef += ':'.join((str(s) for s in ss)) + ','
                cfg_lst.append([cfg[j][kNm],       # kNm
                                str_koef[:-1],          # kKoef
                                cfg[j][kNul],      # kNul
                                ':'.join(str(s) for s in cfg[j][kEma]),
                                cfg[j][kGo],       # kGo
                                cfg[j][kPos],      # kPos
                                cfg[j][kNeg]       # kNeg
                                ])
            rep = _db_tod.update_tbl('cfg_PACK', cfg_lst, val = ' VALUES(?,?,?,?,?,?,?)')
            if rep[0] > 0:
                                
            #rep = self.db_TODAY.update_tbl('cfg_PACK', cfg_lst, val = ' VALUES(?,?,?,?,?,?,?)')
            #if rep[0] > 0:
                #self.err_status = 'update_tbl_cfg_pack   ' + s_lmb(rep[1])
                #self.err_DB(err_log = True)
                return [2, rep[1]]
        except Exception as ex:
            #self.err_status = 'update_tbl_cfg_pack / try  ' + s_lmb(ex)
            #self.err_DB(err_log = True)
            return [1, ex]
        return [0, cfg_lst]
#=======================================================================
def event_MENU(tbl_data_FUT, tbl_cfg_PACK, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev in ['view_data_FUT', 'view_cfg_PACK']:
        wndw.disappear()
        res = _db_tod.read_all_tbl()
        if res[0] == 0:
            for item in res[1]:
                if (item[0] == 'data_FUT') and (ev == 'view_data_FUT'):
                    tbl_data_FUT.parse_data_FUT(item[1])
                    tbl_data_FUT.view_data_FUT()
                if (item[0] == 'cfg_PACK') and (ev == 'view_cfg_PACK'):
                    tbl_cfg_PACK.parse_cfg_PACK(item[1])
                    tbl_cfg_PACK.calc_cfg_PACK(tbl_data_FUT)
                    tbl_cfg_PACK.view_cfg_PACK()
        else:
            err_lmb('view =>',res[1])
        wndw.reappear()
#=======================================================================
def main():
    tbl_data_FUT = tbl_data_fut.Class_DATA_FUT()
    tbl_cfg_PACK = Class_CFG_PACK([])    # init new obj !!!
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'view_data_FUT',
                'view_cfg_PACK',
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
        window.set_title('py_cfg_PACK_class')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(tbl_data_FUT, tbl_cfg_PACK, window, event, values)

    return 0

if __name__ == '__main__':
    main()

