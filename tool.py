import PySimpleGUI as sg
from serial import Serial
import serial.tools.list_ports
from threading import Thread
import os
import pandas as pd

sg.theme('DefaultNoMoreNagging')

ser = Serial()

com = list(serial.tools.list_ports.comports())

def _get_serial_ports():
    ports = []
    for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
        ports.append(port)
    return ports


def main_window():
    port_layout = [[sg.Text('Port:   ', font=('Helvetica', 24)),
                    sg.InputCombo([], size=(30, 1), font=('Helvetica', 24), key='serial_load'),
                    sg.RButton('Reload', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('Connect', size=(10, 1), font=('Helvetica', 24)),
                    sg.Exit(size=(10, 1), font=('Helvetica', 24))]]

    mode_layout = [[sg.RButton('RESET', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('Buzzer off', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('FAIL \n PASS', size=(10, 2), font=('Helvetica', 24)),
                    sg.RButton('LEFT', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('RIGHT', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('Config', size=(10, 1), font=('Helvetica', 24))]]

    items_layout = [[sg.Button('CON o/s', font=('Helvetica', 24), size=(12, 1), key='con')],
                    [sg.Button('POGO o/s', font=('Helvetica', 24), size=(12, 1), key='pogo')],
                    [sg.Button('LED', font=('Helvetica', 24), size=(12, 1), key='led')],
                    [sg.Button('HALL SENSOR', font=('Helvetica', 24), size=(12, 1), key='hall')],
                    [sg.Button('VBAT ID', font=('Helvetica', 24), size=(12, 1), key='vbat')],
                    [sg.Button('C TEST', font=('Helvetica', 24), size=(12, 1), key='c')],
                    [sg.Button('BATTERY', font=('Helvetica', 24), size=(12, 1), key='bat')],
                    [sg.Button('PROX', font=('Helvetica', 24), size=(12, 1), key='prox')],
                    [sg.Button('MIC', font=('Helvetica', 24), size=(12, 1), key='mic')]]

    log_layout = [[sg.Text('PASS', font=('Helvetica', 80), size=(12, 1), justification='center', relief=sg.RELIEF_RIDGE,
                           key='result')],
                  [sg.Multiline('', key='message', size=(38, 15), font=('Helvetica', 24), autoscroll=True, focus=True)]]

    layout = [[sg.Frame('', port_layout)],
              [sg.Frame('', mode_layout)],
              [sg.Frame('', items_layout), sg.Frame('', log_layout)],
              [sg.Button('STOP', font=('Helvetica', 32), button_color='red', size=(51, 1), key='stop_inspection')]]
    return sg.Window('종합검사기', layout, finalize=True)


def result_window():
    conn_tab = [[sg.Text('Connector Open Short')], [sg.Input(key='-conn-')]]
    pogo_tab = [[sg.Text('POGO Open Short')], [sg.Input(key='-pogo-')]]
    led_tab = [[sg.Text('LED')], [sg.Input(key='-led-')]]
    hall_tab = [[sg.Text('Hall Sensor')], [sg.Input(key='-hall-')]]
    vbat_tab = [[sg.Text('VBAT ID')], [sg.Input(key='-vbat-')]]
    battery_tab = [[sg.Text('Battery')], [sg.Input(key='-battery-')]]
    prox_tab = [[sg.Text('Proximity')], [sg.Input(key='-prox-')]]
    mic_tab = [[sg.Text('Mic')], [sg.Input(key='-led-')]]

    vertical_tab = [
        [
            sg.Tab('Conn', conn_tab, key='-Conn-tab-'),
            sg.Tab('Pogo', pogo_tab, key='-pogo-tab-'),
            sg.Tab('LED', led_tab, key='-led-tab-'),
            sg.Tab('Hall', hall_tab, key='-hall-tab-'),
            sg.Tab('VBAT', vbat_tab, key='-vbat-tab-'),
            sg.Tab('Batt', battery_tab, key='-batt-tab-'),
            sg.Tab('Prox', prox_tab, key='-prox-tab-'),
            sg.Tab('MIC', mic_tab, key='-mic-tab-')
        ]
    ]
    layout = [
        [sg.TabGroup(vertical_tab, key='-CONFIG-', tab_location='left')],
        [sg.Exit()],
    ]
    return sg.Window('Config', layout, finalize=True)


text = ''
isRun = True


def readData():
    global isRun
    global text
    while isRun:
        if ser is not None and ser.is_open:
            if text.count('\n') > 1000:
                text = text[text.index('\n') + 1:]
            text += ser.read().decode('cp1252')


window_main, window_result = main_window(), None

while True:
    window, event, values = sg.read_all_windows(timeout=100)
    window_main.find_element('message').Update(text)
    print(values)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        window.close()
        if window == window_result:  # if closing win 2, mark as closed
            window_result = None
        elif window == window_main:  # if closing win 1, exit program
            break

    elif event == 'Config' and not window_result:
        window_result = result_window()

    elif event == 'Reload':
        window['serial_load'].update(_get_serial_ports())

    elif event == 'Connect':
        ser.port = values['serial_load']
        ser.baudrate = 115200
        ser.stopbits = 1
        ser.bytesize = 8
        ser.parity = 'N'

        try:
            ser.open()
            sg.popup_auto_close('connected')
            t = Thread(target=readData, name='read_data')
            t.start()
        except Exception as e:
            sg.Popup('failed')

    elif event == 'Quit':
        try:
            ser.close()
            sg.popup_auto_close('good bye')
            os._exit(1)
        except Exception as e:
            sg.popup_auto_close('failed')
window.close()
