# -*- coding: utf-8 -*-
"""
Created on Fri May 11 14:52:40 2018

@author: vvivek
"""

import win32api, win32con
import time, random, math

class Mouse:
    def __init__(self):
        self.name = "XXX"
    
    def get_position(self): return win32api.GetCursorPos()
    
    def click(self, x, y): 
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    
    def move(self, x, y): win32api.SetCursorPos((x,y))
    
    def circle(self, center, radius, run_time = 60):
        ang = 0
        pi = math.pi
        start = time.time()
        r = radius
        while time.time() - start < run_time:
            point = int(center[0] + r*math.cos(ang)), int(center[1] + r*math.sin(ang))
            self.move(point[0], point[1])
            time.sleep(.01)
            ang = ang + pi/100

mouse = Mouse()
print(mouse.get_position())
hist = (74, 63)
cons = (1255, 662)
r = 0

print("Running...")
while True:
        mouse.circle((656, 597), 50, 5)
        #mouse.click(656, 597)
        time.sleep(10)

while True:
    mouse.move(random.randint(1, 1365), random.randint(1, 767))
    print(r)
    r+=1
    start = time.time()
    while time.time() - start < 120 : 
        print('\rSleeping: %.2f' % (120 - time.time() + start), end = '')
        time.sleep(.1)
    mouse.click(hist[0], hist[1])
    mouse.click(cons[0], cons[1])