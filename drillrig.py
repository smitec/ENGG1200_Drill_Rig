try:
    from tkinter import *
except ImportError:
    from Tkinter import *
import serial
import threading
import time
import os
from serial.tools import list_ports

root = Tk()

class Program:

    def __init__(self, parent):
        self.parent = parent

        # Group Input Box r 0
        rowg = 0
        Label(parent, text="Group: ").grid(row=rowg, column=0, columnspan=2, sticky=W+E, pady=10)
        self.groupName = Entry(parent)

        self.groupName.grid(row=rowg, column=2, columnspan=4, sticky=W+E)
        rowg = rowg + 1

        # Com Port Selection Area r 1 - 3
        rowcom=rowg

        Label(parent, text="Select Serial Ports").grid(row=rowcom, column=0, columnspan=6, sticky=W+E, pady=10)
        rowcom = rowcom+1
        
        Label(parent, text="Student Arduino").grid(row=rowcom, column=0, columnspan=3, sticky=E+W)
        Label(parent, text="Drill Rig Arduino").grid(row=rowcom, column=3, columnspan=3, sticky=E+W)
        rowcom = rowcom+1
        
        self.com_students = Listbox(parent, exportselection=0)
        self.com_drillrig = Listbox(parent, exportselection=0)
        
        for i in list_serial_ports():
            self.com_students.insert(END, i)
            self.com_drillrig.insert(END, i)
        
        self.com_students.grid(row=rowcom, column=0, columnspan=3)
        self.com_drillrig.grid(row=rowcom, column=3, columnspan=3)
        rowcom = rowcom+1
        
        self.button_connect_student = Button(parent, text="Connect", command=self.conn)
        self.button_connect_drillrig = Button(parent, text="Connect", command=self.conn)

        self.button_connect_student.grid(row=rowcom, column=0, columnspan=3, sticky=W+E)
        self.button_connect_drillrig.grid(row=rowcom, column=3, columnspan=3, sticky=W+E)
        rowcom = rowcom+1
        
        # Testing Area r 4 - 6
        rowtest=rowcom
        Label(parent, text="Testing").grid(row=rowtest, column=0, columnspan=6, sticky=W+E, pady=10)
        rowtest=rowtest+1
        
        self.button_up = Button(parent, text="Up", command=self.moveUp)
        self.button_down = Button(parent, text="Down", command=self.moveDown)
        self.button_stop = Button(parent, text="Stop", command=self.kill_drill)
        self.button_char = Button(parent, text="Characterise Head", command=self.head_char)

        self.button_up['state'] = 'disabled'
        self.button_down['state'] = 'disabled'
        self.button_stop['state'] = 'disabled'
        self.button_char['state'] = 'disabled'

        self.button_up.grid(row=rowtest, column=0, columnspan=2, sticky=W+E)
        self.button_down.grid(row=rowtest, column=2, columnspan=2, sticky=W+E)
        self.button_stop.grid(row=rowtest, column=4, columnspan=2, sticky=W+E)
        rowtest=rowtest+1
        
        self.button_char.grid(row=rowtest, column=0, columnspan=6, sticky=W+E)
        rowtest=rowtest+1
        
        self._timer = None
        self.speeds = range(10, 120, 10)
        self.current = 0

    def conn(self):
        self.port = self.com.get(ACTIVE)
        self.serialPort = serial.Serial(self.port, 9600)
        self.button_up['state'] = 'active'
        self.button_down['state'] = 'active'
        self.button_stop['state'] = 'active'
        self.button_char['state'] = 'active'

    def moveUp(self):
        i = int(self.spd.get())
        self.send_up_command(i)

    def send_up_command(self, i):
        text = "FU" + str(i) + ";"
        ba = bytearray(text)
        wr = self.serialPort.write(ba)
        c = self.serialPort.read(1)

    def moveDown(self):
        i = int(self.spd.get())
        self.send_down_command(i)

    def send_down_command(self, i):
        text = "FD" + str(i) + ";"
        ba = bytearray(text)
        wr = self.serialPort.write(ba)
        c = self.serialPort.read(1)

    def kill_drill(self):
        if self._timer != None:
            self._timer.cancel()
            self.current = 999
        wr = self.serialPort.write(bytearray('K'))

    def head_char(self):
        self.current = 0
        self._timer = threading.Timer(4, self.send_next)
        self._timer.start()

    def send_next(self):
        while 1:
            if self.current <= 10: 
                i = self.speeds[self.current]
                print ("Speed : "  + str(i*20) + " um/sec")
                self.send_down_command(i)
                self.current = self.current + 1
                time.sleep(4)
            else:
                print ("Done!")
                self.kill_drill()
                break
            

def list_serial_ports():
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        return [port[0] for port in list_ports.comports()]

p = Program(root)
root.mainloop()
print("ok")
