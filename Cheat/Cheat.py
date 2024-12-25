import math
import ctypes

import Utils
import Configs as cfg
import RCS

user32 = ctypes.windll.user32
pm = Utils.get_pyMeow()
rq = Utils.get_requests()
rcs = RCS.RCS()

weapon_names = { 
        1: "deagle", 
        2: "elite", 
        3: "fiveseven", 
        4: "glock", 
        7: "ak47", 
        8: "aug", 
        9: "awp", 
        10: "famas", 
        11: "g3Sg1", 
        13: "galilar", 
        14: "m249", 
        17: "mac10", 
        19: "p90", 
        23: "mp5sd", 
        24: "ump45", 
        25: "xm1014", 
        26: "bizon", 
        27: "mag7", 
        28: "negev", 
        29: "sawedoff", 
        30: "tec9", 
        31: "zeus", 
        32: "p2000", 
        33: "mp7", 
        34: "mp9", 
        35: "nova", 
        36: "p250", 
        38: "scar20", 
        39: "sg556", 
        40: "ssg08", 
        42: "ct_knife", 
        43: "flashbang", 
        44: "hegrenade", 
        45: "smokegrenade", 
        46: "molotov", 
        47: "decoy", 
        48: "incgrenade", 
        49: "c4", 
        16: "m4a1", 
        61: "usp", 
        60: "m4a1_silencer", 
        63: "cz75a", 
        64: "revolver", 
        59: "t_knife"
    }

AimKey = 0x01

class Offsets:
    m_pBoneArray = 496


class Colors:
    green = pm.get_color("#00FF00")
    orange = pm.fade_color(pm.get_color("#FFA500"), 0.3)
    black = pm.get_color("black")
    cyan = pm.fade_color(pm.get_color("#00F6F6"), 0.3)
    white = pm.get_color("white")
    grey = pm.fade_color(pm.get_color("#242625"), 0.7)


class Entity:

    def __init__(self, ptr, pawn_ptr, proc):
        self.ptr = ptr
        self.pawn_ptr = pawn_ptr
        self.proc = proc
        self.pos2d = None
        self.head_pos2d = None

    @property
    def name(self):
        return pm.r_string(self.proc, self.ptr + Offsets.m_iszPlayerName)

    @property
    def health(self):
        return pm.r_int(self.proc, self.pawn_ptr + Offsets.m_iHealth)

    @property
    def team(self):
        return pm.r_int(self.proc, self.pawn_ptr + Offsets.m_iTeamNum)

    @property
    def pos(self):
        return pm.r_vec3(self.proc, self.pawn_ptr + Offsets.m_vOldOrigin)
    
    @property
    def dormant(self):
        return pm.r_bool(self.proc, self.pawn_ptr + Offsets.m_bDormant)

    @property
    def weaponIndex(self):
        currentWeapon = pm.r_int64(self.proc, self.pawn_ptr + Offsets.m_pClippingWeapon)
        weaponIndex = pm.r_int(self.proc, currentWeapon + Offsets.m_AttributeManager + Offsets.m_Item + Offsets.m_iItemDefinitionIndex)
        return weaponIndex
    
    def get_weapon_name(self):
        return weapon_names.get(self.weaponIndex, "None")
        
    def get_distance(self, localPos):
        dx = self.pos["x"] - localPos["x"]
        dy = self.pos["y"] - localPos["y"]
        dz = self.pos["z"] - localPos["z"]
        return int(math.sqrt(dx * dx + dy * dy + dz * dz) / 100)

    def bone_pos(self, bone):
        game_scene = pm.r_int64(self.proc, self.pawn_ptr + Offsets.m_pGameSceneNode)
        bone_array_ptr = pm.r_int64(self.proc, game_scene + Offsets.m_pBoneArray)
        return pm.r_vec3(self.proc, bone_array_ptr + bone * 32)
    
    def wts(self, view_matrix):
        try:
            self.pos2d = pm.world_to_screen(view_matrix, self.pos, 1)
            self.head_pos2d = pm.world_to_screen(view_matrix, self.bone_pos(6), 1)
        except:
            return False
        return True

class Render:
    def draw_health(max, current, PosX, PosY, width, height):
        if cfg.ESP.show_health:
            Proportion = current / max
            Height = height * Proportion
            offsetY = height * (max - current) / max

            pm.draw_rectangle(PosX + 1, PosY + 1 + offsetY, width / 2, Height, Colors.green)
            pm.draw_rectangle_lines(PosX, PosY, width, height, Colors.black)

    def draw_box(PosX, PosY, width, height, color, filled_color):
        if cfg.ESP.show_filled_box:
            pm.draw_rectangle(PosX, PosY, width, height, filled_color)
        if cfg.ESP.show_box:
            pm.draw_rectangle_lines(PosX + 1, PosY + 1, width, height, Colors.black, 1.2)   # Shadow
            pm.draw_rectangle_lines(PosX, PosY, width, height, color, 1.2)
    
    def draw_distance(distance, PosX, PosY, Color):
        pm.draw_text(f"{distance}m", PosX + 1, PosY + 1, 15, Colors.black)  # Shadow
        pm.draw_text(f"{distance}m", PosX, PosY, 15, Color)

    def draw_weapon(weaponName, PosX, PosY, Color):
        pm.draw_text(f"{weaponName}", PosX + 1, PosY + 1, 15, Colors.black)  # Shadow
        pm.draw_text(f"{weaponName}", PosX, PosY, 15, Color)

class Aimbot:
    def run(viewAngle, localPos, AimPos, viewMatrix):
        smooth = 3
        AimFov = 5

        CenterX = pm.get_screen_width() / 2
        CenterY = pm.get_screen_height() / 2
        OppPos = pm.vec3_subtract(AimPos, localPos)
        Distance = math.sqrt(math.pow(OppPos["x"], 2) + math.pow(OppPos["y"], 2))
        TargetX: int
        TargetY: int

        Yaw = viewAngle["y"] - CenterY
        Pitch = viewAngle["x"] - CenterX
        Norm = math.sqrt(math.pow(Yaw, 2) + math.pow(Pitch, 2))

        Yaw = Yaw*2 - smooth + viewAngle["y"]
        Pitch = Pitch*2 - smooth + viewAngle["x"]

        ScreenPos = pm.world_to_screen(viewMatrix, AimPos, 1)

        if Norm > AimFov:
            if ScreenPos["x"] > CenterX:
                TargetX = -(CenterX - ScreenPos["x"])
                TargetX /= smooth
                if TargetX + CenterX > CenterX * 2:
                    TargetX = 0
            if ScreenPos["x"] < CenterX:
                TargetX = CenterX - ScreenPos["x"]
                TargetX /= smooth
                if TargetX + CenterX < 0:
                    TargetX = 0

            if ScreenPos["y"] != 0:
                if ScreenPos["y"] > CenterY:
                    TargetY = -(CenterY - ScreenPos["y"])
                    TargetY /= smooth
                    if TargetY + ScreenPos["y"] > CenterY * 2:
                        TargetY = 0
                if ScreenPos["y"] < CenterY:
                    TargetY = ScreenPos["y"] - CenterY
                    TargetY /= smooth
                    if TargetY + ScreenPos["y"] < 0:
                        TargetY = 0
            
            TargetX /= 10
            TargetY /= 10
            if math.fabs(TargetX) < 1:
                if TargetX > 0:
                    TargetX = 1
                if TargetX < 0:
                    TargetX = -1
            if math.fabs(TargetY) < 1:
                if TargetY > 0:
                    TargetY = 1
                if TargetY < 0:
                    TargetY = -1

            pm.mouse_move(int(TargetX), int(TargetY))

class Cheat:
    def __init__(self):
        self.proc = pm.open_process("cs2.exe")
        self.mod = pm.get_module(self.proc, "client.dll")["base"]

        offsets_name = ["dwViewMatrix", "dwEntityList", "dwLocalPlayerController", "dwLocalPlayerPawn"]
        offsets = rq.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
        [setattr(Offsets, k, offsets["client.dll"][k]) for k in offsets_name]
        client_dll_name = {
            "m_iIDEntIndex": "C_CSPlayerPawnBase",
            "m_hPlayerPawn": "CCSPlayerController",
            "m_fFlags": "C_BaseEntity",
            "m_iszPlayerName": "CBasePlayerController",
            "m_iHealth": "C_BaseEntity",
            "m_iTeamNum": "C_BaseEntity",
            "m_vOldOrigin": "C_BasePlayerPawn",
            "m_pGameSceneNode": "C_BaseEntity",
            "m_bDormant": "CGameSceneNode",
            "m_flFlashDuration": "C_CSPlayerPawnBase",
            "m_pClippingWeapon": "C_CSPlayerPawnBase",
            "m_iShotsFired": "C_CSPlayerPawn",
            "m_angEyeAngles": "C_CSPlayerPawnBase",
            "m_aimPunchAngle": "C_CSPlayerPawn",

            "m_AttributeManager": "C_EconEntity",
            "m_Item": "C_AttributeContainer",
            "m_iItemDefinitionIndex": "C_EconItemView"
        }
        clientDll = rq.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
        [setattr(Offsets, k, clientDll["client.dll"]["classes"][client_dll_name[k]]["fields"][k]) for k in client_dll_name]

    def it_entities(self):
        ent_list = pm.r_int64(self.proc, self.mod + Offsets.dwEntityList)
        local = pm.r_int64(self.proc, self.mod + Offsets.dwLocalPlayerController)
        for i in range(1, 65):
            try:
                entry_ptr = pm.r_int64(self.proc, ent_list + (8 * (i & 0x7FFF) >> 9) + 16)
                controller_ptr = pm.r_int64(self.proc, entry_ptr + 120 * (i & 0x1FF))
                if controller_ptr == local:
                    continue
                controller_pawn_ptr = pm.r_int64(self.proc, controller_ptr + Offsets.m_hPlayerPawn)
                list_entry_ptr = pm.r_int64(self.proc, ent_list + 0x8 * ((controller_pawn_ptr & 0x7FFF) >> 9) + 16)
                pawn_ptr = pm.r_int64(self.proc, list_entry_ptr + 120 * (controller_pawn_ptr & 0x1FF))
            except:
                continue

            yield Entity(controller_ptr, pawn_ptr, self.proc)

    def get_local_pawn(self):
        return pm.r_int64(self.proc, self.mod + Offsets.dwLocalPlayerPawn)

    def get_local_player_pos(self):
        return pm.r_vec3(self.proc, self.get_local_pawn() + Offsets.m_vOldOrigin)
    
    def run(self):
        pm.overlay_init("Counter-Strike 2", fps=144)
        while pm.overlay_loop():
            view_matrix = pm.r_floats(self.proc, self.mod + Offsets.dwViewMatrix, 16)

            pm.begin_drawing()
            pm.draw_fps(0, 0)
            for ent in self.it_entities():
                if ent.wts(view_matrix) and ent.health > 0 and not ent.dormant:
                    color = Colors.cyan if ent.team != 2 else Colors.orange
                    head = ent.pos2d["y"] - ent.head_pos2d["y"]
                    width = head / 2
                    center = width / 2

                    if cfg.ESP.show_line:
                        pm.draw_line(pm.get_screen_width() / 2 + 1, 1, ent.head_pos2d["x"], ent.head_pos2d["y"] - center / 2, Colors.black, 0.5)
                        pm.draw_line(pm.get_screen_width() / 2, 0, ent.head_pos2d["x"], ent.head_pos2d["y"] - center / 2, Colors.white, 0.5)
                    
                    Render.draw_box(ent.head_pos2d["x"] - center, ent.head_pos2d["y"] - center / 2, width, head + center / 2, Colors.white, color)
                    Render.draw_health(100, ent.health, 
                                        ent.head_pos2d["x"] + center + 2,
                                        ent.head_pos2d["y"] - center / 2, 
                                        4, 
                                        head + center / 2)
                    if cfg.ESP.show_distance:
                        distance = ent.get_distance(self.get_local_player_pos())
                        Render.draw_distance(distance, ent.head_pos2d["x"] + center + 8, ent.head_pos2d["y"] - center / 2, pm.get_color("#00FFFF"))
                    if cfg.ESP.show_weapon:
                        Render.draw_weapon(ent.get_weapon_name(), ent.head_pos2d["x"] + center + 8, ent.head_pos2d["y"] - center / 2 + 15, pm.get_color("#FF7700"))

            pm.end_drawing()
            rcs.update()