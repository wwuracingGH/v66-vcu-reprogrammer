from gui import GUI
from yapper import setUpChannel, tearDownChannel
import dearpygui.dearpygui as dpg
import time

from canlib import canlib, Frame

if __name__ == '__main__':
    GUI.init()

    ch0 = setUpChannel(0)

    ch0.write(Frame(id_=8, data=[0]))

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

        if GUI.WRITE_QUEUE == True:
            GUI.WRITE_QUEUE = False
            
            ch0.write(Frame(id_=6, data=GUI.get_bytestr()))
            ch0.write(Frame(id_=7, data=GUI.get_bytestr_t()))

        try:
            while (frame := ch0.read()) is not canlib.canNoMsg:
                match frame.id:
                    case 1:
                        apps2 = int.from_bytes(frame.data[0:2], byteorder='little')
                        apps1 = int.from_bytes(frame.data[6:8], byteorder='little')
                        GUI.recalc(apps1, apps2)
                    case 9:
                        apps1_min = int.from_bytes(frame.data[0:2], byteorder='little')
                        apps1_max = int.from_bytes(frame.data[2:4], byteorder='little')
                        apps2_min = int.from_bytes(frame.data[4:6], byteorder='little')
                        apps2_max = int.from_bytes(frame.data[6:8], byteorder='little')
                        GUI.adj_vals(apps1_min, apps1_max, apps2_min, apps2_max)
                        print(apps1_min, apps1_max, apps2_min, apps2_max)
                    case 10:
                        max_tr = int.from_bytes(frame.data[0:2], byteorder='little')
                        max_rg = int.from_bytes(frame.data[2:4], byteorder='little')
                        min_rgs = int.from_bytes(frame.data[4:6], byteorder='little')
                        brakes = int.from_bytes(frame.data[6:8], byteorder='little')
                        GUI.adj_torque(max_tr, max_rg, min_rgs, brakes)
                        print(max_tr)
        except (canlib.canNoMsg) as ex:
            pass
        except (canlib.canError) as ex:
            print(ex)

    

    GUI.destroy()
