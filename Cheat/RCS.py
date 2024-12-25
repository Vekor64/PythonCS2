import win32api
import time
import pyMeow as pm
import win32api
import win32con

import Utils
import Configs

class Offsets:
    dwLocalPlayerPawn = 0

class RCS:
    def __init__(self):
        self.proc = pm.open_process("cs2.exe")
        self.mod = pm.get_module(self.proc, "client.dll")["base"]
        self.enabled = True
        self.old_punch = {"x": 0, "y": 0}
        self.rcs_bullet = 0
        self.rcs_scale = {"x": 2.0, "y": 2.0}
        
        self.load_offsets()
        
        self.rcs_config = {
            'intensity': 2.5,
            'recovery_time': 0.3,
            'max_shots': 30,
            'vertical_scale': 1.0,
            'horizontal_scale': 0.0,
            'smoothing': 1.0,
        }
    
    def load_offsets(self):

        offsets_name = ["dwViewMatrix", "dwEntityList", "dwLocalPlayerController", "dwLocalPlayerPawn"]
        offsets = Utils.rq.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
        [setattr(Offsets, k, offsets["client.dll"][k]) for k in offsets_name]
        self.dwLocalPlayerPawn = Offsets.dwLocalPlayerPawn
    
        client_dll_name = {
            "m_iShotsFired": "C_CSPlayerPawn",
            "m_aimPunchAngle": "C_CSPlayerPawn",
        }
        clientDll = Utils.rq.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
        [setattr(Offsets, k, clientDll["client.dll"]["classes"][client_dll_name[k]]["fields"][k]) for k in client_dll_name]
        self.m_iShotsFired = Offsets.m_iShotsFired
        self.m_aimPunchAngle = Offsets.m_aimPunchAngle
    
    def get_local_player(self):
        return pm.r_int64(self.proc, self.mod + self.dwLocalPlayerPawn)
    
    def get_shots_fired(self, local_player):
        return pm.r_int(self.proc, local_player + self.m_iShotsFired)
    
    def get_aim_punch(self, local_player):
        return pm.r_vec2(self.proc, local_player + self.m_aimPunchAngle)
    
    def is_shooting(self):
        return win32api.GetKeyState(0x01) < 0
    
    def update(self):
        if Configs.MISC.rcs == False:
            return
        
        if not self.enabled:
            return
        
        try:
            local_player = self.get_local_player()
            if not local_player:
                return
            
            shots_fired = self.get_shots_fired(local_player)
            if shots_fired <= self.rcs_bullet:
                self.old_punch = {"x": 0, "y": 0}
                return
            
            aim_punch = self.get_aim_punch(local_player)
            
            sensitivity = 3.0
            delta = {
                "x": (aim_punch["x"] - self.old_punch["x"]) * 2.0,
                "y": (aim_punch["y"] - self.old_punch["y"]) * 2.0
            }
            
            mouse_x = int(delta["y"] / (sensitivity * 0.11) * self.rcs_scale["x"] * self.rcs_config['intensity'])
            mouse_y = int(delta["x"] / (sensitivity * 0.11) * self.rcs_scale["y"] * self.rcs_config['intensity'])
            
            if self.is_shooting():
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mouse_x, -mouse_y, 0, 0)
            
            self.old_punch = aim_punch
            
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    rcs = RCS()
    print("Press END to exit.")
    
    try:
        while True:
            if win32api.GetKeyState(0x23) < 0:
                break
            rcs.update()
            time.sleep(0.001)
    except KeyboardInterrupt:
        pass
    finally:
        print("Cheat has exited.")

if __name__ == "__main__":
    main()