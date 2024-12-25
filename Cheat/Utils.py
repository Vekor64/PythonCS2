import requests as rq
import pyMeow as pm

def get_pyMeow(): 
    return pm

def get_requests():
    return rq

class Mem:
    def trace_address(proc, base_address, offsets):
        address = 0

        if len(offsets) == 0:
            return base_address
        
        address = pm.r_int(proc, base_address)
        if address == 0:
            return 0
        
        for i in range(len(offsets) - 1):
            address = pm.r_int(proc, address + offsets[i])
            if address == 0:
                return 0
            
        return address + offsets[-1] if address != 0 else 0