import threading

from Cheat import Cheat
import gui

cheat = Cheat()

gui_thread = threading.Thread(target=gui.render)
cheat_thread = threading.Thread(target=cheat.run)

gui_thread.start()
cheat_thread.start()

gui_thread.join()
cheat_thread.join()