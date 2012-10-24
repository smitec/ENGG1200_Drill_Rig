from Tkinter import *
import serial

root = Tk()

class Program:

	def __init__(self, parent):
		self.parent = parent

		self.port = "/dev/tty.usbserial-A9007OD1"
		
		self.serialPort = serial.Serial(self.port, 9600)

		Label(parent, text="Speed (*10um/s)").grid(row=0, sticky=W)
		Label(parent, text="Distance (*10um)").grid(row=1, sticky=W)
		Label(parent, text="Steps (Down Only)").grid(row=2, sticky=W)

		self.spd = Entry(parent)
		self.dis = Entry(parent)
		self.steps = Entry(parent)

		self.spd.grid(row=0, column=1, columnspan=2)
		self.dis.grid(row=1, column=1, columnspan=2)
		self.steps.grid(row=2, column=1, columnspan=2)

		self.b1 = Button(parent, text="Move Up", command=self.moveUp)
		self.b2 = Button(parent, text="Move Down", command=self.moveDown)
		self.b4 = Button(parent, text="Set Zero", command=self.setZero)
		self.b5 = Button(parent, text="TMS Test", command=self.inst_test)
		self.b6 = Button(parent, text="Kill Feed Motor", command=self.kill_drill)

		self.b1.grid(row=3, column=0)
		self.b2.grid(row=3, column=1)
		self.b4.grid(row=3, column=2)
		self.b5.grid(row=3, column=3)
		self.b6.grid(row=3, column=4)

		self.pos = StringVar()
		self.pos.set("0mm")
		Label(parent, textvariable=self.pos).grid(row=4, sticky=W)

		self.csize = (700, 512)
		self.canvas = Canvas(self.parent, width=self.csize[0], height=self.csize[1])
		self.canvas.grid(row=5, column=0, columnspan=7)

		self.pot = StringVar()
		self.pot.set("0")
		Label(parent, textvariable=self.pot).grid(row=4, sticky=E)

		self.position = 0
		self.lastRot = 0
		self.data = []

		self.setZero()

	def moveUp(self):
		i = int(self.spd.get())
		if i > 500:
			print "Can't Move That Fast!"
		else:
			text = "FU" + str(self.dis.get()) + "," + str(i) + ";"
			ba = bytearray(text)
			wr = self.serialPort.write(ba)
			c = self.serialPort.read(1)
			if (c == 'A'):
				self.position -= int(self.dis.get())/100.0
				self.pos.set(str(self.position) + "mm")
				self.pollPot()

	def moveDown(self):
		for j in range(int(self.steps.get())):
			i = int(self.spd.get())
			if i > 100:
				print "Can't Move That Fast!"
			else:
				text = "FD" + str(self.dis.get()) + "," + str(i) + ";"
				ba = bytearray(text)
				wr = self.serialPort.write(ba)
				c = self.serialPort.read(1)
				if (c == 'A'):
					oldPos = self.position
					oldRot = self.lastRot
					self.position += int(self.dis.get())/100.0
					self.pos.set(str(self.position) + "mm")
					self.pollPot()

					self.data += [(self.position, self.lastRot)]

					self.drawMove()

	def pollPot(self):
		wr = self.serialPort.write(bytearray('P'))
		c = self.serialPort.read(1)
		num = 0
		while c != 'A':
			num = num * 10
			num = num + int(c)
			c = self.serialPort.read(1)

		self.lastRot = num
		self.pot.set(str(num))

	def kill_drill(self):
		wr = self.serialPort.write(bytearray('K'))

	def inst_test(self):
		wr = self.serialPort.write(bytearray('I'))
		for i in range(3):
			c = self.serialPort.read(1)
			num = 0
			dp = 0
			nums = 0
			while c != 'A':
				if c == '.':
					dp = 1
				else:
					num = num * 10
					num = num + int(c)
					if (dp == 1):
						nums = nums + 1
				c = self.serialPort.read(1)

			num = num / (10.0**(dp+1))

			print num

		

	def clearCanvas(self):
		self.canvas.delete(ALL)
		self.canvas.create_rectangle(0,0,self.csize[0],self.csize[1], fill="black")

	def setZero(self):
		self.pos.set("0mm")
		self.position = 0
		self.lastRot = 0
		self.data = []
		self.pot.set("0")
		self.clearCanvas()

	def drawMove(self):
		#draw a line form oldpos to current pos at pot reading
		maxP = self.data[0][0]
		minP = self.data[0][0]
		maxR = self.data[0][1]
		minR = self.data[0][1]
		for p,r in self.data:
			if p > maxP:
				maxP = p
			elif p < minP:
				minP = p

			if r > maxR: 
				maxR = r
			elif r < minR:
				minR = r

		self.clearCanvas()

		mapped = [(0,0)]
		for pt in self.data:
			mapped += [self.map(pt, (minP, minR), (maxP, maxR), (0,10), (self.csize[0], self.csize[1] - 10))]
			self.canvas.create_line(mapped[-2][0], self.csize[1] - mapped[-2][1], mapped[-2][0], self.csize[1] - mapped[-1][1], fill="yellow")
			self.canvas.create_line(mapped[-2][0], self.csize[1] - mapped[-1][1], mapped[-1][0], self.csize[1] - mapped[-1][1], fill="yellow")
		

		

	def map(self, val, low, high, newLow, newHigh):
		#map a data pair so the graph is always full
		pos = val[0]
		rot = val[1]

		pos -= low[0]
		rot -= low[1]

		pos /= 1.0*(high[0] - low[0])
		
		if (high[1] - low[1]) != 0:
			rot /= 1.0*(high[1] - low[1])
		else:
			rot = 1

		#both are now percentages
		newPos = pos*(newHigh[0] - newLow[0])
		newRot = rot*(newHigh[1] - newLow[1])

		newPos += newLow[0]
		newRot += newLow[1]

		return (newPos, newRot)


p = Program(root)
root.mainloop()