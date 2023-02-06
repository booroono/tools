import struct

import PySimpleGUI as sg
from serial import Serial
import serial.tools.list_ports
from threading import Thread
import serial_input_output as sss
from variables import *

# sg.theme('Default')
ser = Serial()
com = list(serial.tools.list_ports.comports())
text = ''
voltage_output = ''
resistance_output = ''
digital_output = ''
ad_type = VOLTAGE
isRun = True
toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

out_n = [str(num) for num in range(0, 49)]

layout_connector = [
    [sg.Text('Con +', justification='center', font=('Helvetica', 22), size=(6, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Con -', justification='center', font=('Helvetica', 22), size=(6, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Volt out', justification='center', font=('Helvetica', 22), size=(6, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('ETC X', justification='center', font=('Helvetica', 22), size=(6, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('ETC Y', justification='center', font=('Helvetica', 22), size=(6, 1), relief=sg.RELIEF_RIDGE)],
    [sg.InputCombo(out_n, size=(6, 1), font=('Helvetica', 20), key="Connector_Positive_input", default_value=out_n[0]),
     sg.InputCombo(out_n, size=(6, 1), font=('Helvetica', 20), key="Connector_Negative_input", default_value=out_n[0]),
     sg.InputCombo(out_n, size=(6, 1), font=('Helvetica', 20), key="Voltage_Out_input", default_value=out_n[0]),
     sg.InputCombo(out_n, size=(6, 1), font=('Helvetica', 20), key="ETC_X_Control_input", default_value=out_n[0]),
     sg.InputCombo(out_n, size=(6, 1), font=('Helvetica', 20), key="ETC_Y_Control_input", default_value=out_n[0])],
    [sg.Button('SEND', font=('Helvetica', 16), size=(51, 1), key='Send_Contact')]]

layout_mux = [
    [sg.Text('REF 전압 1', justification='center', font=('Helvetica', 22), size=(11, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('REF 전압 2', justification='center', font=('Helvetica', 22), size=(11, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('ETC', justification='center', font=('Helvetica', 22), size=(11, 1), relief=sg.RELIEF_RIDGE)],
    [sg.InputCombo(list(REF1.keys()), size=(13, 1), font=('Helvetica', 17), key="Ref_1_input", default_value=list(REF1.keys())[0]),
     sg.InputCombo(list(REF2.keys()), size=(13, 1), font=('Helvetica', 17), key="Ref_2_input", default_value=list(REF2.keys())[0]),
     sg.InputCombo(list(ETC.keys()), size=(13, 1), font=('Helvetica', 17), key="ETC_input", default_value=list(ETC.keys())[0])],
    [sg.Button('On', font=('Helvetica', 18), size=(6, 1), button_color='blue', key='Ref_1_On'),
     sg.Button('Off', font=('Helvetica', 17), size=(6, 1), button_color='red', key='Ref_1_Off'),
     sg.Button('On', font=('Helvetica', 18), size=(6, 1), button_color='blue', key='Ref_2_On'),
     sg.Button('Off', font=('Helvetica', 17), size=(6, 1), button_color='red', key='Ref_2_Off'),
     sg.Button('On', font=('Helvetica', 18), size=(6, 1), button_color='blue', key='ETC_On'),
     sg.Button('Off', font=('Helvetica', 17), size=(6, 1), button_color='red', key='ETC_Off')]]

layout_sol = [
    [sg.Text('Sol 1', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 2', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 3', justification='center', font=('Helvetica', 10), size=(4, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 4', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 5', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 6', justification='center', font=('Helvetica', 10), size=(4, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 7', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE),
     sg.Text('Sol 8', justification='center', font=('Helvetica', 10), size=(5, 1), relief=sg.RELIEF_RIDGE)],
    [sg.Button(image_data=toggle_btn_off, key='-sol1-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol2-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol3-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol4-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol5-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol6-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol7-', metadata=False),
     sg.Button(image_data=toggle_btn_off, key='-sol8-', metadata=False)]]

layout_Out_control = [
    [sg.Button('ALL OFF', font=('Helvetica', 16), button_color='red', size=(51, 1), key='all_off_button')],
    [sg.HorizontalSeparator(color='white')],
    [sg.Frame("접점제어", layout_connector, element_justification='center', font=('Helvetica', 28), pad=(5, 3), expand_x=True, expand_y=True,
              background_color='#404040', border_width=0, title_location=sg.TITLE_LOCATION_TOP)],
    [sg.HorizontalSeparator(color='white')],
    [sg.Frame("MUX 제어", layout_mux, element_justification='center', font=('Helvetica', 28), pad=(5, 3), expand_x=True, expand_y=True,
              background_color='#404040', border_width=0, title_location=sg.TITLE_LOCATION_TOP)],
    [sg.HorizontalSeparator(color='white')],
    [sg.Frame("Sol 제어", layout_sol, element_justification='center', font=('Helvetica', 28), pad=(5, 3), expand_x=True, expand_y=True,
              background_color='#404040', border_width=0, title_location=sg.TITLE_LOCATION_TOP)],
]

layout_AD_control = [
    [sg.Text('전압', justification='center', font=('Helvetica', 24), size=(8, 1)),
     sg.Text('저항', justification='center', font=('Helvetica', 24), size=(8, 1)),
     sg.Text('디지털', justification='center', font=('Helvetica', 24), size=(8, 1))],
    [sg.Text('', font=('Helvetica', 24), size=(8, 1), relief=sg.RELIEF_RIDGE, key='Voltage_output'),
     sg.Text('', font=('Helvetica', 24), size=(8, 1), relief=sg.RELIEF_RIDGE, key='Resistance_output'),
     sg.Text('', font=('Helvetica', 24), size=(8, 1), relief=sg.RELIEF_RIDGE, key='Digital_output')],
    [sg.HorizontalSeparator(color='white')],
    [sg.Button('MUX AD8', font=('Helvetica', 36), size=(5, 2), key='mux_ad8'),
     sg.Button('ETC AD', font=('Helvetica', 36), size=(5, 2), key='etc_ad'),
     sg.Button('REF 1.0V', font=('Helvetica', 36), size=(5, 2), key='ref_1.0v')],
    [sg.Button('REF 2.0V', font=('Helvetica', 36), size=(5, 2), key='ref_2.0v'),
     sg.Button('1.8V CC', font=('Helvetica', 36), size=(5, 2), key='1.8v_cc'),
     sg.Button('3.3V CC', font=('Helvetica', 36), size=(5, 2), key='3.3v_cc')],
    [sg.Button('AD CDS', font=('Helvetica', 36), size=(5, 2), key='ad_cds')]]

layout_Serial = [[sg.Text('Port:   ', font=('Helvetica', 24)),
                  sg.InputCombo(com, size=(38, 1), font=('Helvetica', 24), key='port'),
                  sg.Button('Connect', font=('Helvetica', 18), size=(8, 1), button_color='blue'),
                  sg.Button('Disconnect', font=('Helvetica', 18), size=(10, 1), button_color='red')],
                 [sg.Multiline('', key='message', size=(74, 15), font=('Helvetica', 24), autoscroll=True, focus=True)]]

layout = [
    [sg.Frame("Out control", layout_Out_control, font=('Helvetica', 28), size=(600, 600),
              title_location=sg.TITLE_LOCATION_TOP),
     sg.Frame("AD control", layout_AD_control, element_justification='center', font=('Helvetica', 28), size=(500, 600),
              title_location=sg.TITLE_LOCATION_TOP)],
    [sg.Frame("Serial", layout_Serial, font=('Helvetica', 28), size=(1100, 300),
              title_location=sg.TITLE_LOCATION_TOP)]
]


def ad_value_input(value):
    global voltage_output
    global digital_output
    global resistance_output
    if ad_type == VOLTAGE:
        voltage_output = str(value)+VOLTAGE
    elif ad_type == DIGITAL:
        digital_output = str(value)
    else:
        resistance_output = str(value)+RESISTANCE


def readData():
    global isRun
    global text
    global ad_type
    while isRun:
        if ser is not None and ser.is_open:
            if text.count('\n') > 10000:
                text = text[text.index('\n') + 1:]
            received_packet = ser.read_until(EOT)
            # print(received_packet)
            # text += ' '.join([f"{int(hex(row)[2:]):02d}" for row in received_packet]) + '\n'
            text += ' '.join([f"{'0' + hex(row)[2:] if len(hex(row)[2:]) == 1 else hex(row)[2:]}" for row in received_packet]) + '\n'
            if not sss.is_valid_packet(received_packet):
                continue

            if not (parsed_value := sss.parse_packet(received_packet)):
                continue

            if type(parsed_value) is int:
                value = parsed_value
            else:
                value, data_type = parsed_value
                if data_type:
                    ad_type = RESISTANCE
                else:
                    ad_type = VOLTAGE
            ad_value_input(value)
            # text += ser.read().decode('cp1252')


window = sg.Window("Manual", layout, margins=(2, 2), finalize=True)

while True:
    window.find_element('message').Update(text)
    window['Voltage_output'].update(voltage_output)
    window['Resistance_output'].update(resistance_output)
    window['Digital_output'].update(digital_output)
    event, values = window.read(timeout=10)

    # event, values = window.read()
    # print(event)
    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'Connect':
        ser.port = values.get('port').device
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

    elif event == 'Disconnect':
        ser.port = values.get('port').device
        try:
            ser.close()
            sg.popup_auto_close('Disconcected')
        except Exception as e:
            sg.popup_auto_close('Failed')

    elif event == 'all_off_button':
        all_off_cmd = sss.make_send_packet(CMD_ALL_OFF, b'')
        ser.write(all_off_cmd)

    elif event == 'Send_Contact':
        get_con_P = window.Element('Connector_Positive_input').Get()
        get_con_N = window.Element('Connector_Negative_input').Get()
        Vol_Out_ = window.Element('Voltage_Out_input').Get()
        ETC_X_Con = window.Element('ETC_X_Control_input').Get()
        ETC_Y_Con = window.Element('ETC_Y_Control_input').Get()
        data = struct.pack('B', int(get_con_P)) + \
               struct.pack('B', int(get_con_N)) + \
               struct.pack('B', int(Vol_Out_)) + \
               struct.pack('B', int(ETC_X_Con)) + \
               struct.pack('B', int(ETC_Y_Con))
        contact_values = sss.make_send_packet(CMD_CONTACT_CONTROL, data)
        ser.write(contact_values)

    elif event == 'Ref_1_On':
        #     0x0 : REF 1V 1KΩ,
        #     0x1 : REF 1V 10KΩ,
        #     0x2 : REF 1V 100KΩ,
        #     0x3 : REF 1V 1MΩ,
        #     0x4 : AMP 1.8V,
        #     0x5 : REF 2V,
        #     0x6 : AMP 3.3V,
        #     0x7 : TP1
        get_Ref_1 = window.Element('Ref_1_input').Get()
        send_packet = sss.make_send_packet(CMD_REF_VOLTAGE_CONTROL1, REF1[get_Ref_1])
        ser.write(send_packet)

    elif event == 'Ref_1_Off':
        send_packet = sss.make_send_packet(CMD_REF_VOLTAGE_CONTROL1, CONNECTION_OFF)
        ser.write(send_packet)

    elif event == 'Ref_2_On':
        #     0x0 : AMP 1.8V,
        #     0x1 : AMP 3.3V,
        #     0x2 : P1.8V,
        #     0x3 : P3.3V,
        get_Ref_2 = window.Element('Ref_2_input').Get()
        send_packet = sss.make_send_packet(CMD_REF_VOLTAGE_CONTROL2, REF2[get_Ref_2])
        ser.write(send_packet)

    elif event == 'Ref_2_Off':
        send_packet = sss.make_send_packet(CMD_REF_VOLTAGE_CONTROL2, CONNECTION_OFF)
        ser.write(send_packet)

    elif event == 'ETC_On':
        #     0x0 : ETC AD,
        #     0x1 : TP2-TP3,
        #     0x2 : I2C,
        #     0x3 : FREQ
        get_ETC = window.Element('ETC_input').Get()
        send_packet = sss.make_send_packet(CMD_ETC_CONTROL, ETC[get_ETC])
        ser.write(send_packet)

    elif event == 'ETC_Off':
        send_packet = sss.make_send_packet(CMD_ETC_CONTROL, CONNECTION_OFF)
        ser.write(send_packet)

    elif event in SOL_VALUE.keys():
        window[event].metadata = not window[event].metadata
        window[event].update(image_data=toggle_btn_on if window[event].metadata else toggle_btn_off)
        sol_value = window.Element(event).metadata
        # print(sol_value, SOL_VALUE[event])
        on_off_value = 1 if sol_value else 0
        data = struct.pack('2B', on_off_value, SOL_VALUE[event])
        send_packet = sss.make_send_packet(CMD_SOL_VALVE_CONTROL, data)
        ser.write(send_packet)

    elif event in AD_READ.keys():
        ad_type = AD_READ_TYPE[event]
        # voltage_output = AD_READ_TEXT[event]
        # resistance_output = AD_READ_TEXT[event]
        # digital_output = AD_READ_TEXT[event]
        # print(voltage_output)
        # window['Voltage_output'].update(AD_READ_TEXT[event])
        # window['Resistance_output'].update(AD_READ_TEXT[event])
        # window['Digital_output'].update(AD_READ_TEXT[event])
        send_packet = sss.make_send_packet(CMD_AD_READ, AD_READ[event])
        ser.write(send_packet)

window.close()
