from Tkinter import *
import serial
import threading

root = Tk()

class Program:

    def __init__(self, parent):
        self.parent = parent

        Label(parent, text="Speed (*20um/s)").grid(row=0, sticky=E)
        Label(parent, text="Serial Port (eg COM5)").grid(row=1, sticky=E)

        self.com = Entry(parent)
        self.spd = Entry(parent)

        self.spd.grid(row=0, column=1, columnspan=3)
        self.com.grid(row=1, column=1, columnspan=3)

        self.button_connect = Button(parent, text="Connect", command=self.conn)
        self.button_up = Button(parent, text="Up", command=self.moveUp)
        self.button_down = Button(parent, text="Down", command=self.moveDown)
        self.button_stop = Button(parent, text="Stop", command=self.kill_drill)
        self.button_char = Button(parent, text="Characterise Head", command=self.head_char)

        self.button_up['state'] = 'disabled'
        self.button_down['state'] = 'disabled'
        self.button_stop['state'] = 'disabled'
        self.button_char['state'] = 'disabled'

        self.button_connect.grid(row=3, column=0, sticky=W+E)
        self.button_up.grid(row=3, column=1, sticky=W+E)
        self.button_down.grid(row=3, column=2, sticky=W+E)
        self.button_stop.grid(row=3, column=3, sticky=W+E)
        self.button_char.grid(row=4, column=0, columnspan=4, sticky=W+E)

        self._timer = None
        self.speeds = range(10, 120, 10)
        self.current = 0

    def conn(self):
        self.port = self.com.get()
        self.serialPort = serial.Serial(self.port, 9600)
        self.button_up['state'] = 'enabled'
        self.button_down['state'] = 'enabled'
        self.button_stop['state'] = 'enabled'
        self.button_char['state'] = 'enabled'

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
        wr = self.serialPort.write(bytearray('K'))

    def head_char(self):
        self._timer = Timer(4, self.send_next)
        self._timer.start()

    def send_next(self):
        if self.current <= 10: 
            i = self.speeds[self.current]
            self.send_down_command(i)
            self.current = self.current + 1
        else:
            self.kill_drill()


p = Program(root)
root.mainloop()
