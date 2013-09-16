from Tkinter import *
import serial

root = Tk()

class Program:

	def __init__(self, parent):
		self.parent = parent

		self.port = "/dev/tty.usbmodem1421"
		
		#self.serialPort = serial.Serial(self.port, 9600)

		Label(parent, text="Speed (*10um/s)").grid(row=0, sticky=W)

		self.spd = Entry(parent)

		self.spd.grid(row=0, column=1, columnspan=2)

		self.b1 = Button(parent, text="Move Up", command=self.moveUp)
		self.b2 = Button(parent, text="Move Down", command=self.moveDown)
		self.b6 = Button(parent, text="Stop", command=self.kill_drill)

		self.b1.grid(row=3, column=0)
		self.b2.grid(row=3, column=1)
		self.b6.grid(row=3, column=2)

	def moveUp(self):
		i = int(self.spd.get())
		if i > 500:
			print "Can't Move That Fast!"
		else:
			text = "FU" + str(self.dis.get()) + "," + str(i) + ";"
			ba = bytearray(text)
			wr = self.serialPort.write(ba)
			c = self.serialPort.read(1)
# MOVE TO TIMER	self.pos.set(str(self.position) + "mm")

	def moveDown(self):
		i = int(self.spd.get())
		if i > 500:
			print "Can't Move That Fast!"
		else:
			text = "FD" + str(self.dis.get()) + "," + str(i) + ";"
			ba = bytearray(text)
			wr = self.serialPort.write(ba)
			c = self.serialPort.read(1)


	def kill_drill(self):
		wr = self.serialPort.write(bytearray('K'))

	def setZero(self):
		self.pos.set("0mm")
		self.position = 0

p = Program(root)
root.mainloop()
