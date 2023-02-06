import PySimpleGUI as sg
from serial import Serial
import serial.tools.list_ports
from threading import Thread
import os
import pandas as pd

sg.theme('DefaultNoMoreNagging')

ser = Serial()

com = list(serial.tools.list_ports.comports())
mode = "1", "2", "3", "4", "5"


def _get_serial_ports():
    ports = []
    for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
        ports.append(port)
    return ports


def main_window():
    port_layout = [[sg.Text('Port:   ', font=('Helvetica', 24)),
                    sg.InputCombo(com, size=(30, 1), font=('Helvetica', 24), key='serial_load'),
                    sg.RButton('Reload', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('Connect', size=(10, 1), font=('Helvetica', 24))]]

    mode_layout = [[sg.Text('Mode: ', font=('Helvetica', 24)),
                    sg.InputCombo(mode, size=(30, 1), font=('Helvetica', 24)),
                    sg.RButton('Buzzer off', size=(10, 1), font=('Helvetica', 24)),
                    sg.RButton('Result view', size=(10, 1), font=('Helvetica', 24))]]

    items_layout = [[sg.Button('RESET', font=('Helvetica', 24), size=(12, 1), key='reset')],
                    [sg.Button('JIG DOWN', font=('Helvetica', 24), size=(12, 1), key='jig')],
                    [sg.Button('CON o/s', font=('Helvetica', 24), size=(12, 1), key='con')],
                    [sg.Button('POGO o/s', font=('Helvetica', 24), size=(12, 1), key='pogo')],
                    [sg.Button('LED', font=('Helvetica', 24), size=(12, 1), key='led')],
                    [sg.Button('HALL SENSOR', font=('Helvetica', 24), size=(12, 1), key='hall')],
                    [sg.Button('VBAT ID', font=('Helvetica', 24), size=(12, 1), key='vbat')],
                    [sg.Button('C TEST', font=('Helvetica', 24), size=(12, 1), key='c')],
                    [sg.Button('BATTERY', font=('Helvetica', 24), size=(12, 1), key='bat')],
                    [sg.Button('PROX', font=('Helvetica', 24), size=(12, 1), key='prox')],
                    [sg.Button('MIC', font=('Helvetica', 24), size=(12, 1), key='mic')]]

    log_layout = [[sg.Text('RESULT', font=('Helvetica', 24), size=(38, 1), justification='center')],
                  [sg.Text('PASS', font=('Helvetica', 80), size=(12, 1), justification='center', relief=sg.RELIEF_RIDGE,
                           key='result')],
                  [sg.Multiline('', key='message', size=(38, 15), font=('Helvetica', 24), autoscroll=True, focus=True)]]

    layout = [[sg.Frame('', port_layout)],
              [sg.Frame('', mode_layout)],
              [sg.Frame('', items_layout), sg.Frame('', log_layout)]]
    return sg.Window('종합검사기', layout, finalize=True)


def result_window():
    headings = ['', 'LOW<=', 'VALUE', '<=HIGH', 'RESULT']
    header = [[sg.Text('  ')] + [sg.Text(h, size=(14, 1)) for h in headings]]

    file = r'data.xlsx'

    df = pd.read_csv(file, header=None)
    values = df.values.tolist()
    headings = values[0]
    data = values[1:]

    # input_rows = [[sg.Input(size=(15, 1), pad=(0, 0)) for col in range(5)] for row in range(10)]
    input_rows = [[sg.Table(data, headings=headings, key='-TABLE-')]]
    layout = header + input_rows

    # layout = [
    #     [sg.TabGroup([[
    #         sg.Tab('OPEN/SHORT TEST', tab1_layout),
    #         sg.Tab('POGO TEST', tab2_layout),
    #         sg.Tab('LED', tab3_layout),
    #         sg.Tab('HALL SENSOR', tab4_layout),
    #         sg.Tab('VBAT ID', tab5_layout),
    #         sg.Tab('C TEST', tab6_layout),
    #         sg.Tab('BATTERY TEST', tab7_layout),
    #         sg.Tab('PROXIMITY TEST', tab8_layout),
    #         sg.Tab('MIC', tab9_layout),
    #     ]])],
    #     [sg.Button('Exit', font=('Helvetica', 24))]
    # ]
    return sg.Window('RESULT', layout, finalize=True)


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

    elif event == 'Result view' and not window_result:
        window_result = result_window()

    elif event == 'Reload':
        window['serial_load'].update(_get_serial_ports())

    elif event == 'Connect':
        ser.port = values[0].device
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
