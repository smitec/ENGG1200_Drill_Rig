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
        self.studeSerialPot = None
        self.drillSerialPort = None
        rowcom=rowg

        Label(parent, text="Select Serial Ports").grid(row=rowcom, column=0, columnspan=6, sticky=W+E, pady=10)
        rowcom = rowcom+1
        
        Label(parent, text="Student Arduino").grid(row=rowcom, column=0, columnspan=3, sticky=E+W)
        Label(parent, text="Drill Rig Arduino").grid(row=rowcom, column=3, columnspan=3, sticky=E+W)
        rowcom = rowcom+1
        
        self.comboStudent = Listbox(parent, exportselection=0)
        self.comboDrillrig = Listbox(parent, exportselection=0)
        
        for i in list_serial_ports():
            self.comboStudent.insert(END, i)
            self.comboDrillrig.insert(END, i)
        
        self.comboStudent.grid(row=rowcom, column=0, columnspan=3)
        self.comboDrillrig.grid(row=rowcom, column=3, columnspan=3)
        rowcom = rowcom+1
        
        self.btnConnectStudent = Button(parent, text="Connect", command=lambda: self.connect_to_serial(True))
        self.btnConnectDrillrig = Button(parent, text="Connect", command=lambda: self.connect_to_serial(False))

        self.btnConnectStudent.grid(row=rowcom, column=0, columnspan=3, sticky=W+E)
        self.btnConnectDrillrig.grid(row=rowcom, column=3, columnspan=3, sticky=W+E)
        rowcom = rowcom+1
        
        # Testing Area r 4 - 6
        rowtest=rowcom
        Label(parent, text="Testing").grid(row=rowtest, column=0, columnspan=6, sticky=W+E, pady=10)
        rowtest=rowtest+1
        
        self.btnUp = Button(parent, text="Up", command=self.move_up)
        self.btnDown = Button(parent, text="Down", command=self.move_down)
        self.btnStop = Button(parent, text="Stop", command=self.kill_drill)
        self.btnChar = Button(parent, text="Characterise Head", command=self.head_char)

        self.btnUp['state'] = 'disabled'
        self.btnDown['state'] = 'disabled'
        self.btnStop['state'] = 'disabled'
        self.btnChar['state'] = 'disabled'

        self.btnUp.grid(row=rowtest, column=0, columnspan=2, sticky=W+E)
        self.btnDown.grid(row=rowtest, column=2, columnspan=2, sticky=W+E)
        self.btnStop.grid(row=rowtest, column=4, columnspan=2, sticky=W+E)
        rowtest=rowtest+1
        
        self.btnChar.grid(row=rowtest, column=0, columnspan=6, sticky=W+E)
        rowtest=rowtest+1
        
        self._timer = None
        self.speeds = range(10, 120, 10)
        self.current = 0

        # Demo Day area
        rowdemo=rowtest
        Label(parent, text="Demo Day").grid(row=rowdemo, column=0, columnspan=6, sticky=W+E, pady=10)
        rowdemo=rowdemo+1

        self.btnStartDemo = Button(parent, text="Start Student Control", command=self.start_demo)
        self.btnStopDemo = Button(parent, text="Stop", command=self.kill_drill)

        self.btnStartDemo.grid(row=rowdemo, column=0, columnspan=4, sticky=W+E)
        self.btnStopDemo.grid(row=rowdemo, column=4, columnspan=2, sticky=W+E)

        rowdemo = rowdemo+1

        self.demo = None
        self.logFile = None
        self.auto_kill = None

        # message log
        rowmessage = rowdemo

        Label(parent, text="Messages").grid(row=rowmessage, column=0, columnspan=6, sticky=W+E, pady=10)

        rowmessage = rowmessage+1
        
        self.messageLog = Text(parent, exportselection=0)

        self.messageLog.grid(row=rowmessage, column=0, columnspan=6, rowspan=6, sticky=E+W)

        rowmessage = rowmessage+1

        #Canvas?
        self.graph = Canvas(parent, width=400, height=500)
        #self.graph.grid(row=0, column=6, rowspan=rowmessage-1) 

    def log_message(self, sender, message):
        self.messageLog.insert(END, sender+ " : " + message + "\n")

    def start_demo(self):
        self.studentRunning = True
        self.demo = threading.Timer(4, self.run_demo)
        self.log_message("Demo Day", "Student Control in 4 Seconds")
        self.demo.start()

    def run_demo(self):
        self.log_message("Student Control", "Started")

        group = self.groupName.get()

        self.logFile = open(group + ".txt", "w")

        ba = bytearray('G')
        self.studentSerialPort.write(ba)
        self.studentSerialPort.read(1)

        current_depth = 0
        start_time = current_time = time.time()
        current_speed = 0

        while self.studentRunning:
            bt = self.studentSerialPort.read(4)
            
            #we blocked so double check the conditions
            if self.studentRunning == False:
                break

            if len(bt) != 4:
                continue

            #convert to two ints
            a =  ord(bt[0]) + (ord(bt[1])<< 8)
            b =   ord(bt[2]) + (ord(bt[3]) << 8)

            #self.log_message("Student Serial", "Got " + str(a) + "  " + str(b))

            if a == 1:
                self.log_message("Student Code", "Sent Feed Rate")
                if b <= 110:
                    #self.send_down_command(b)
                    #set a timer for (200-depth)/speed so it kills the drill when it needs to
                    current_time = time.time()
                    current_depth = 0.2*current_speed*(current_time - start_time) + current_depth
                    start_time = current_time
                    current_speed = b

                    depth_remaining = 200 - current_depth
                    time_needed = depth_remaining/(0.2*current_speed)

                    if (self.auto_kill != None):
                        self.auto_kill.cancel()
                        self.auto_kill = None

                    self.auto_kill = threading.Timer(time_needed, self.kill_dill)

                    self.log_message("Student Code", "Setting Feed to: " + str(b))
                    pass
                else:
                    self.log_message("ERROR", "Students Cannot Exceed 110")
            elif a == 2:
                self.log_message("Student Code", "Sent Depth (" + str(b) + ")")
                self.logFile.write("d:"+str(b)+"\n")
            elif a == 3:
                self.log_message("Student Code", "Sent Torque(" + str(b/1000.0) + ")")
                self.logFile.write("t:"+str(b/1000.0)+"\n")
            elif a == 4:
                self.log_message("Student Code", "Sent Density (" + str(b) + ")")
                self.logFile.write("m:"+str(b)+"\n")
            elif a == 5: #end of demo message
                self.log_message("Student Code", "Sent End")
                self.logFile.write("e:0\n")
                self.kill_drill()
            else:
                self.log_message("Student Code", "Sent Rubbish")
                #laugh
            
    def connect_to_serial(self, student):
        if student:
            self.studentPort = self.comboStudent.get(ACTIVE)
            self.studentSerialPort = serial.Serial(self.studentPort, 9600, timeout=1)
            c = self.studentSerialPort.read(1)
            if c == 's':
                # it's a student arduino 
                self.log_message("Connections", "Student Arduino Connected")
        else:
            self.drillPort = self.comboDrillrig.get(ACTIVE)
            self.drillSerialPort = serial.Serial(self.drillPort, 9600, timeout=1)
            # recieve the init code and check
            c = self.drillSerialPort.read(1)
            if c == 'd':
                self.log_message("Connections", "Drill Rig Connected")
                self.btnUp['state'] = 'active'
                self.btnDown['state'] = 'active'
                self.btnStop['state'] = 'active'
                self.btnChar['state'] = 'active'
            else:
                self.log_message("Connections", "Drill Rig Connection Failed, Correct Port?")

    def move_up(self):
        i = int(self.spd.get())
        self.send_up_command(i)

    def send_up_command(self, i):
        text = "FU" + str(i) + ";"
        ba = bytearray(text)
        wr = self.drillSerialPort.write(ba)
        c = self.drillSerialPort.read(1)
        self.log_message("Drill Control", "Moving Up @ " + str(i*20) + " um/sec (" + str(i) + ")")

    def move_down(self):
        i = int(self.spd.get())
        self.send_down_command(i)

    def send_down_command(self, i):
        text = "FD" + str(i) + ";"
        ba = bytearray(text)
        wr = self.drillSerialPort.write(ba)
        c = self.drillSerialPort.read(1)
        self.log_message("Drill Control", "Moving Down @ " + str(i*20) + " um/sec (" + str(i) + ")")

    def kill_drill(self):
        if self.demo != None:
            self.demo.cancel()
            self.studentRunning = False
            self.studentSerialPort.timeout = 2
            if self.logFile != None:
                self.logFile.close()
                self.logFile = None

        if self._timer != None:
            self._timer.cancel()
            self.current = 999
            self.studentRunning = False
            
        if self.drillSerialPort != None:
            wr = self.drillSerialPort.write(bytearray('K'))
        self.log_message("Drill Control", "Stopping Drill")

    def head_char(self):
        self.current = 0
        self._timer = threading.Timer(4, self.send_next)
        self._timer.start()
        self.log_message("Testing", "Characterisation Started");

    def send_next(self):
        while 1:
            if self.current <= 10: 
                i = self.speeds[self.current]
                self.send_down_command(i)
                self.current = self.current + 1
                time.sleep(4)
            else:
                self.log_message("Testing", "Characterisation Done");
                self.kill_drill()
                break

    def save_files(self):
        if self.logFile != None:
            self.logFile.close()
            

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
p.save_files()
