import Configs as cfg

from dearpygui.dearpygui import create_context, destroy_context, start_dearpygui,create_viewport, setup_dearpygui, show_viewport, is_dearpygui_running, render_dearpygui_frame, set_primary_window
from dearpygui.dearpygui import window, child_window, tab_bar, tab
from dearpygui.dearpygui import add_checkbox, add_text, add_combo, add_input_text

GUI_WIDTH = 340
GUI_HEIGHT = 420

checkbox_config_map1 = {
    "Show Box": ("ESP", "show_box"),
    "Filled Box": ("ESP", "show_filled_box"), 
    "Show Line": ("ESP", "show_line"), 
    "Show Health Bar": ("ESP", "show_health"),
    "Show Distance": ("ESP", "show_distance"),
    "Show Weapon": ("ESP", "show_weapon"),
    }

checkbox_config_map2 = {
    "Recoil Control": ("MISC", "rcs"),
    }

def checkbox_callback(sender, app_data, user_data):
    class_name, attr_name = user_data
    setattr(getattr(cfg, class_name), attr_name, app_data)

def render():
    create_context()
    with window(label="", width=GUI_WIDTH, height=GUI_HEIGHT, no_move=True, no_resize=True, no_title_bar=True, tag="Primary Window"):
        with tab_bar():
            with tab(label="ESP"):
                for label, (class_name, attr_name) in checkbox_config_map1.items():
                    initial_value = getattr(getattr(cfg, class_name), attr_name)
                    add_checkbox(label=label, default_value=initial_value, callback=checkbox_callback, user_data=(class_name, attr_name))
            with tab(label="Misc"):
                for label, (class_name, attr_name) in checkbox_config_map2.items():
                    initial_value = getattr(getattr(cfg, class_name), attr_name)
                    add_checkbox(label=label, default_value=initial_value, callback=checkbox_callback, user_data=(class_name, attr_name))
        
    create_viewport(title="CS2", width=GUI_WIDTH, height=GUI_HEIGHT, x_pos=0, y_pos=0, resizable=False)
    setup_dearpygui()
    show_viewport()
    set_primary_window("Primary Window", True)

    while is_dearpygui_running():
        render_dearpygui_frame()

    destroy_context()

if __name__ == '__main__':
    render()