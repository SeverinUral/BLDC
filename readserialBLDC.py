#!/usr/bin/python3
# Fomenko AV

import sys
import time
import serial
import datetime

from math import sqrt
from os import makedirs
from statistics import mean
from curses import wrapper, curs_set, echo

FR_q = 0.1 # период опроса порта в секундах
last_avg = 10 # количество крайних значений тока по которым считать среднее
port = "COM1"   
baudrate = 9600 

def main(window):
    # open serial port
    ser = serial.Serial(port, baudrate=baudrate, timeout=1, write_timeout=1)
    # list of currents
    currents = []
    # message to serial port
    message = b"\x01\x03\x80\x00\x00\x20\x6D\xD2"
    
    # config curses
    window.nodelay(True)
    curs_set(0)
    
    # output to console
    window.addstr(0, 0, 'For stop press <Esc>.')
    
    while True:
        # send message via rs232
        ser.write(message)
        
        # recive data
        data = ser.read(69)
        
        # add current to list
        currents.append(int.from_bytes(data[61:63], 'big')/100)
        
        # output to console
        window.addstr(2, 4, f'{currents[-1]:.2f} A - Current current')
        window.addstr(3, 4, f'{max(currents):.2f} A - Max current')
        window.addstr(4, 4, f'{RMS(currents):.2f} A - RMS current')
        window.addstr(5, 4, f'{mean(currents):.2f} A - Avg current (from begin)')
        if len(currents) > last_avg:
            window.addstr(6, 4, f'{mean(currents[(last_avg * -1):-1]):.2f} A - Avg current ({last_avg}\'s last measurements)')
        
        window.refresh()
        
        # stop by pressing Esc
        if window.getch() == 27: break
        
        # delay
        time.sleep(FR_q)
    
    # exit
    
    # config curses
    window.nodelay(False)

    window.addstr(8, 0, 'Save to file? Y/N')

    if window.getch() in [89, 121, 1085, 1053]:
        # config curses
        echo()
        curs_set(2)
        
        window.addstr(9, 0, 'Enter file name:')
        file_name = window.getstr(9, 16, 255).decode('utf-8')
        save_to_file(currents, file_name, last_avg)
        window.addstr(10, 0, 'Saved to <log> directory.')
        
    window.addstr(11, 0, 'Press any key for exit...')
    window.getch()
    
        
def save_to_file(currents, file_name, last_avg):
    makedirs('log', exist_ok=True)
    current_date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    
    with open(f"log/{current_date}_{file_name}.log", 'a') as f:
        s = f'''{file_name}
        {currents[-1]:.2f} A - Current current
        {max(currents):.2f} A - Max current
        {RMS(currents):.2f} A - RMS current
        {mean(currents):.2f} A - Avg current (from begin)
        {mean(currents[(last_avg * -1):-1]):.2f} A - Avg current ({last_avg}\'s last measurements)'''
        
        f.writelines(s)

def RMS (currents):
    summ = 0
    for current in currents: summ += current**2
    return round(sqrt(summ/len(currents)),2)
        
if __name__ == "__main__":
    wrapper(main)
    sys.exit(0)
