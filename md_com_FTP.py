#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_com_FTP.py
#   
#  Copyright 2021  <>
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
from prettytable import PrettyTable
from ftpretty import ftpretty
import PySimpleGUI as sg    # vers >= 4.29
import md_db_SQLite as dbs
#=======================================================================
_consts = dbs.Class_CNST()
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_FTP():
    def __init__(self):
        print(_consts.hst + '.beget.tech')
        print(_consts.usr)
        print(_consts.pas + _consts.ssw + _consts.sword)
        self.f = ftpretty(_consts.hst + '.beget.tech',
                          _consts.usr,
                          _consts.pas + _consts.ssw + _consts.sword)
        dirr = self.f.list('/images/', extra=False)
        for item in dirr:
            print(item)
#=======================================================================
def event_MENU(send_by_ftp, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'send_by_ftp_pack_0_9':
        wndw.disappear()
        for i in [0,1,2,3,4,5,6,7,8,9]:
            send_by_ftp.f.put('c:\\1_pack_'+str(i)+'.png', '/images/')
            send_by_ftp.f.put('c:\\10_pack_'+str(i)+'.png', '/images/')
            print('sending pack_' + str(i) + '.png')
            #wndw['-STATUS_BAR-'].update('sending pack_' + str(i))
        wndw.reappear()
    #----------------------------------------
    if ev == 'send_by_ftp_get_tm_VTB':
        wndw.disappear()
        send_by_ftp.f.put('c:\\get_tm_VTB.txt', '/')
        wndw.reappear()
    #----------------------------------------

    
#=======================================================================
def main():
    send_by_ftp = Class_FTP()    # init new obj !!!
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'send_by_ftp_pack_0_9',
                'send_by_ftp_get_tm_VTB',
                'send_by_ftp_message_002',
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
        window.set_title('py_Class_SMTP')
        break
    while True: #--- Main Cycle ---------------------------------------#
        #event, values = window.read() # .read(timeout = 1000)
        event, values = window.read(timeout = 61000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in ['__TIMEOUT__']:
            event = 'send_by_ftp_pack_0_9'
        #
        if event in func:
            event_MENU(send_by_ftp, window, event, values)

    return 0

if __name__ == '__main__':
    main()

