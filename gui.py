#imgui freak implementation

import dearpygui.dearpygui as dpg

#remaps t from a to b
def quick_remap(a1,a2,b1,b2,t):
    if a1 == a2: return 0
    if a1 == None or a2 == None: return 0
    return ((t - a1) / (a2 - a1)) * (b2 - b1) + b1 

class GUI:
    @staticmethod
    def queue_write(sender, app_data, user_data):
        GUI.WRITE_QUEUE = True

    @staticmethod
    def get_bytestr():
        b02 = GUI.APPS_VALS[GUI.APPS_1_MIN_SLIDER].to_bytes(2, 'little')
        b24 = GUI.APPS_VALS[GUI.APPS_1_MAX_SLIDER].to_bytes(2, 'little')
        b46 = GUI.APPS_VALS[GUI.APPS_2_MIN_SLIDER].to_bytes(2, 'little')
        b68 = GUI.APPS_VALS[GUI.APPS_2_MAX_SLIDER].to_bytes(2, 'little')

        return b02 + b24 + b46 + b68
    
    @staticmethod
    def vcb(sender, app_data, user_data):
        GUI.APPS_VALS[sender] = app_data
        
        a1maxy = quick_remap( 0, 4092, 300, 0, GUI.APPS_VALS[GUI.APPS_1_MAX_SLIDER])
        a1miny = quick_remap( 0, 4092, 300, 0, GUI.APPS_VALS[GUI.APPS_1_MIN_SLIDER])
        a2maxy = quick_remap( 0, 4092, 300, 0, GUI.APPS_VALS[GUI.APPS_2_MAX_SLIDER])
        a2miny = quick_remap( 0, 4092, 300, 0, GUI.APPS_VALS[GUI.APPS_2_MIN_SLIDER])

        dpg.configure_item(GUI.APPS_1_MIN_LINE, p1=(0,a1miny), p2=(20,a1miny))
        dpg.configure_item(GUI.APPS_1_MAX_LINE, p1=(0,a1maxy), p2=(20,a1maxy))
        dpg.configure_item(GUI.APPS_2_MIN_LINE, p1=(0,a2miny), p2=(20,a2miny))
        dpg.configure_item(GUI.APPS_2_MAX_LINE, p1=(0,a2maxy), p2=(20,a2maxy))

    @staticmethod
    def calibration(sender, app_data, user_data):
        if GUI.CALIBRATING:
            GUI.CALIBRATING = False
            dpg.configure_item(GUI.CALIB_BUTTON, label="   CALIBRATE   ")
        else:
            GUI.CALIBRATING = True
            GUI._CALIB_MIN_APPS1 = 4092
            GUI._CALIB_MAX_APPS1 = 0
            GUI._CALIB_MIN_APPS2 = 4092
            GUI._CALIB_MAX_APPS2 = 0
            dpg.configure_item(GUI.CALIB_BUTTON, label=" CALIBRATING...")

    @staticmethod
    def update_calibration(apps1, apps2):
        GUI._CALIB_MIN_APPS1 = min(GUI._CALIB_MIN_APPS1, apps1)
        GUI._CALIB_MAX_APPS1 = max(GUI._CALIB_MAX_APPS1, apps1)
        GUI._CALIB_MIN_APPS2 = min(GUI._CALIB_MIN_APPS2, apps2)
        GUI._CALIB_MAX_APPS2 = max(GUI._CALIB_MAX_APPS2, apps2)
        GUI.adj_vals(GUI._CALIB_MIN_APPS1 + 1, GUI._CALIB_MAX_APPS1 - 1, GUI._CALIB_MIN_APPS2 + 1, GUI._CALIB_MAX_APPS2 - 1)

    @staticmethod
    def adj_vals(apps1_min, apps1_max, apps2_min, apps2_max):
        GUI.APPS_VALS[GUI.APPS_1_MIN_SLIDER] = apps1_min
        GUI.APPS_VALS[GUI.APPS_1_MAX_SLIDER] = apps1_max
        GUI.APPS_VALS[GUI.APPS_2_MIN_SLIDER] = apps2_min

        dpg.set_value(GUI.APPS_1_MIN_SLIDER, apps1_min)
        dpg.set_value(GUI.APPS_1_MAX_SLIDER, apps1_max)
        dpg.set_value(GUI.APPS_2_MIN_SLIDER, apps2_min)
        dpg.set_value(GUI.APPS_2_MAX_SLIDER, apps2_max)

        GUI.vcb(GUI.APPS_2_MAX_SLIDER, apps2_max, None)

    @staticmethod
    def adj_torque(max_torque = None, min_torque = None, min_regen_rpm = None, brakes_threashold = None):
        if max_torque != None:
            dpg.set_value(GUI.TORQUE_MAX, max_torque)
        if min_torque != None:
            dpg.set_value(GUI.TORQUE_MIN, min_torque)

    @staticmethod
    def vct(sender, app_data, user_data):
        GUI.adj_torque()

    @staticmethod
    def recalc(apps1, apps2):
        dpg.set_value(GUI.APPS1_SLIDER, apps1) 
        dpg.set_value(GUI.APPS2_SLIDER, apps2)
        GUI.calc(None,None,None)

    @staticmethod
    def calc(sender, app_data, user_data):
        apps1 = dpg.get_value(GUI.APPS1_SLIDER) 
        apps2 = dpg.get_value(GUI.APPS2_SLIDER)
        
        if GUI.CALIBRATING:
            GUI.update_calibration(apps1, apps2)
        
        GUI.CALC_APPS_VALS[0] = quick_remap(GUI.APPS_VALS[GUI.APPS_1_MAX_SLIDER],GUI.APPS_VALS[GUI.APPS_1_MIN_SLIDER],1,0,apps1)
        GUI.CALC_APPS_VALS[1] = quick_remap(GUI.APPS_VALS[GUI.APPS_2_MAX_SLIDER],GUI.APPS_VALS[GUI.APPS_2_MIN_SLIDER],1,0,apps2)
        
        dpg.configure_item(GUI.APPS_1_CALC_TEXT, default_value="APPS1: {:.3f}".format(GUI.CALC_APPS_VALS[0]))
        dpg.configure_item(GUI.APPS_2_CALC_TEXT, default_value="APPS2: {:.3f}".format(GUI.CALC_APPS_VALS[1]))

        capp = (GUI.CALC_APPS_VALS[0] + GUI.CALC_APPS_VALS[1]) / 2.0
        if capp < 0: capp = 0
        if capp > 1: capp = 1
        fault = 0
        
        if abs(GUI.CALC_APPS_VALS[0] - GUI.CALC_APPS_VALS[1]) > 0.1:
            fault = 1
        elif (GUI.CALC_APPS_VALS[0] > 1.0 or GUI.CALC_APPS_VALS[1] > 1.0):
            fault = 2
        elif(GUI.CALC_APPS_VALS[0] < 0.0 or GUI.CALC_APPS_VALS[1] < 0.0):
            fault = 2

        torque = quick_remap(0.0,1.0,0.0,dpg.get_value(GUI.TORQUE_MAX),capp)

        dpg.configure_item(GUI.APPS_CALC_TEXT, default_value="VALUE: {:.3f} ".format(capp))
        dpg.configure_item(GUI.APPS_FAULT_STATE, default_value="FAULT: {i} ".format(i=fault))
        dpg.configure_item(GUI.TORQUE_CALC, default_value="TORQUE: {:.1f}Nm".format(float(torque) / 10))

    @staticmethod
    def init():
        dpg.create_context()

        GUI.WRITE_QUEUE = False
        GUI.CALIBRATING = False
        GUI.APPS_VALS = {}
        GUI.TRBP_VALS = {}
        GUI.CALC_APPS_VALS = [0,0]
    
        # add a font registry
        with dpg.font_registry():
            default_font = dpg.add_font("ComicMono-Bold.ttf", 20)

        with dpg.window(tag="Primary Window"):
            dpg.bind_font(default_font)
            
            with dpg.group(horizontal=True):
                dpg.add_text("APPS:")
                GUI.CALIB_BUTTON = dpg.add_button(label="CALIBRATE", callback=GUI.calibration)
            with dpg.group(horizontal=True):
                with dpg.group():
                    GUI.APPS_1_CALC_TEXT = dpg.add_text("APPS_1")

                    with dpg.group(horizontal=True):
                        GUI.APPS1_SLIDER = dpg.add_slider_int(vertical=True, max_value=4092, height=300, width=50, callback = GUI.calc)
                        with dpg.drawlist(pos = [0, 0], width = 70, height = 300):
                            GUI.APPS_1_MIN_LINE = dpg.draw_line((0,300), (30,300), thickness=4)
                            GUI.APPS_1_MAX_LINE = dpg.draw_line((0, 0), (30, 0), thickness=4)
                    
                    GUI.APPS_1_MAX_SLIDER = dpg.add_drag_int(label="MAX", width=60, max_value=4092, callback=GUI.vcb)
                    GUI.APPS_1_MIN_SLIDER = dpg.add_drag_int(label="MIN", width=60, max_value=4092, callback=GUI.vcb)
                    GUI.APPS_VALS[GUI.APPS_1_MIN_SLIDER] = 0
                    GUI.APPS_VALS[GUI.APPS_1_MAX_SLIDER] = 0

                with dpg.group():
                    GUI.APPS_2_CALC_TEXT = dpg.add_text("APPS_2")
        
                    with dpg.group(horizontal=True):
                        GUI.APPS2_SLIDER = dpg.add_slider_int(vertical=True, max_value=4092, height=300, width=50, callback = GUI.calc) 
                        with dpg.drawlist(pos = [0, 0], width = 70, height = 300):
                            GUI.APPS_2_MIN_LINE = dpg.draw_line((0,300), (10,300), thickness=4)
                            GUI.APPS_2_MAX_LINE = dpg.draw_line((0, 0), (10, 0), thickness=4)

                    GUI.APPS_2_MAX_SLIDER = dpg.add_drag_int(label="MAX", width=60, max_value=4092, callback=GUI.vcb)
                    GUI.APPS_2_MIN_SLIDER = dpg.add_drag_int(label="MIN", width=60, max_value=4092, callback=GUI.vcb)
                    GUI.APPS_VALS[GUI.APPS_2_MIN_SLIDER] = 0
                    GUI.APPS_VALS[GUI.APPS_2_MAX_SLIDER] = 0
            
            with dpg.group(horizontal=True):
                GUI.APPS_CALC_TEXT = dpg.add_text("ACCEL:     ")
                GUI.APPS_FAULT_STATE = dpg.add_text("FAULT:     ")
                dpg.add_button(enabled=True, label="Program", callback=GUI.queue_write)
            with dpg.group(horizontal=True):
                with dpg.group():
                    GUI.TORQUE_MAX = dpg.add_drag_int(label="T-MAX", width=100, max_value=2300, callback=GUI.vct)
                    GUI.TORQUE_MIN = dpg.add_drag_int(label="REGEN", width=100, max_value=2300, callback=GUI.vct)
                with dpg.group():
                    GUI.TORQUE_CALC = dpg.add_text("TORQUE: ")
               
        dpg.create_viewport(title='Custom Title', width=600, height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)

    def destroy():
        dpg.destroy_context()
