#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  md_com_SMTP.py
#  
#  Copyright 2021  <>
#  
#=======================================================================
import os, sqlite3, sys
#from datetime import datetime, timezone
from prettytable import PrettyTable
import PySimpleGUI as sg    # vers >= 4.29
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import md_db_SQLite as dbs
#=======================================================================
_consts = dbs.Class_CNST()
#=======================================================================
locationXY = (700, 50)
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#=======================================================================
class Class_SMTP():
    def __init__(self, message, subject):
        self.message  = message
        self.subject  = subject
        self.password = _consts.pa + _consts.ss + _consts.word
        # create message object instance

    def send_mail(self):
        self.msg = MIMEMultipart()        
        self.msg['From']    = _consts.msg_from
        self.msg['To']      = _consts.msg_from
        self.msg['Subject'] = self.subject
        # add in the message body
        self.msg.attach(MIMEText(self.message, 'plain'))

        # Assume we know that the image files are all in PNG format
        #for fl in pngfiles:
        pngfiles = [9,0,1,2,3,4,5,6,7,8]
        for i in pngfiles:
            fl = 'c:\\1_pack_'+str(i)+'.png'
            # Open the files in binary mode.  Let the MIMEImage class automatically
            # guess the specific image type.
            fp = open(fl, 'rb')
            img = MIMEImage(fp.read())
            fp.close()
            self.msg.attach(img)
        #for i in pngfiles:
            #fl = 'c:\\10_pack_'+str(i)+'.png'
            #fp = open(fl, 'rb')
            #img = MIMEImage(fp.read())
            #fp.close()
            #self.msg.attach(img)
            
        try:
            #create server
            server = smtplib.SMTP('smtp.gmail.com: 587')# 587
            server.ehlo()
            server.starttls()
        
            # Login Credentials for sending the mail
            server.login(self.msg['From'], self.password)
        
            # send the message via the server.
            server.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())
            #server.sendmail(self.msg['From'], self.msg['To'], self.message)
        
            server.quit()
        
        except Exception as ex:
            msg_status = "Something went wrong..." + ex
            print(msg_status)
            return [1, msg_status]

        msg_status = "Successfully sent email"
        print(msg_status)
        return [0, msg_status]
#=======================================================================
def event_MENU(send_by_smtp, wndw, ev, val):
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.1',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 grab_anywhere=True)
        wndw.reappear()
    #----------------------------------------
    if ev == 'send_by_smtp_message_000':
        wndw.disappear()
        send_by_smtp.subject = str(111) + '   ' + str(-222)
        send_by_smtp.message = 'send_by_smtp_000'
        send_by_smtp.send_mail()
        wndw.reappear()
    #----------------------------------------
    if ev == 'send_by_smtp_message_001':
        wndw.disappear()
        send_by_smtp.subject = str(1111) + '   ' + str(-2222)
        send_by_smtp.message = 'send_by_smtp_001'
        send_by_smtp.send_mail()
        wndw.reappear()
    #----------------------------------------
    if ev == 'send_by_smtp_message_002':
        wndw.disappear()
        send_by_smtp.subject = str(11) + '   ' + str(-22)
        send_by_smtp.message = 'send_by_smtp_002'
        send_by_smtp.send_mail()
        wndw.reappear()
    #----------------------------------------
#=======================================================================
def main():
    send_by_smtp = Class_SMTP('Test SMTP', '')    # init new obj !!!
    while True: #--- Init  --------------------------------------------#
        sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
        func = [
                'send_by_smtp_message_000',
                'send_by_smtp_message_001',
                'send_by_smtp_message_002',
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
        event, values = window.read() # .read(timeout = 1000)
        os.system('cls')  # on windows
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in func:
            event_MENU(send_by_smtp, window, event, values)

    return 0

if __name__ == '__main__':
    main()

