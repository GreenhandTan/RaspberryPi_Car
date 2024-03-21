import RPi.GPIO as GPIO
import time
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import Adafruit_PCA9685
from tornado.options import define,options
from blinker import Device,ButtonWidget,JoystickWidget,RangeWidget

define("port",default=8081,help="run on the given port",type=int)

device = Device("c1b7916f1e5b")

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

button_qian = device.addWidget(ButtonWidget('btn-iza'))
button_hou = device.addWidget(ButtonWidget('btn-rkc'))
button_zuoqian = device.addWidget(ButtonWidget('btn-ysg'))
button_youqian = device.addWidget(ButtonWidget('btn-g3h'))
button_zuohou = device.addWidget(ButtonWidget('btn-8wl'))
button_youhou = device.addWidget(ButtonWidget('btn-pog'))
joy1 = device.addWidget(JoystickWidget("joy-g8k"))
range1 = device.addWidget(RangeWidget("ran-dpg"))
range2 = device.addWidget(RangeWidget("ran-kxj"))

#输入角度转换成12^精度的数值
def set_servo_angle(channel, angle):
    #进行四舍五入运算 date=int(4096*((angle*11)+500)/(20000)+0.5)
    date=int(4096*((angle*11)+500)/20000)
    pwm.set_pwm(channel, 0, date)

#定义Car类
class Car(object):
	def __init__(self):
		self.sleep = 0.2
		#self.enab_pin是使能端的pin
		self.enab_pin = [5,6,13,19]
		#self.inx_pin是控制端in的pin
		self.inx_pin = [21,22,23,24]
		#分别是右轮前进，右轮退后，左轮前进，左轮退后的pin
		self.RightAhead_pin = self.inx_pin[0]
		self.RightBack_pin = self.inx_pin[1]
		self.LeftAhead_pin = self.inx_pin[2]
		self.LeftBack_pin = self.inx_pin[3]
		self.setup()

	#setup函数初始化端口
	def setup(self):
		print("begin setup ena enb pin")
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		#初始化使能端pin，设置成高电平
		for pin in self.enab_pin: 
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,GPIO.HIGH)
		#初始化控制端pin，设置成低电平
		pin = None
		for pin in self.inx_pin:
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,GPIO.LOW)
		print("setup ena enb pin over")

	#fornt函数，小车前进
	def front(self):
		self.setup()
		GPIO.output(self.RightAhead_pin,GPIO.HIGH)
		GPIO.output(self.LeftAhead_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()

	#leftFront函数，小车左拐弯
	def leftFront(self):
		self.setup()
		GPIO.output(self.RightAhead_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()

	#rightFront函数，小车右拐弯
	def rightFront(self):
		self.setup()
		GPIO.output(self.LeftAhead_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()

	#rear函数，小车后退
	def rear(self):
		self.setup()
		GPIO.output(self.RightBack_pin,GPIO.HIGH)
		GPIO.output(self.LeftBack_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()

	#leftRear函数，小车左退
	def leftRear(self):
		self.setup()
		GPIO.output(self.RightBack_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()

	#rightRear函数，小车右退
	def rightRear(self):
		self.setup()
		GPIO.output(self.LeftBack_pin,GPIO.HIGH)
		time.sleep(self.sleep)
		GPIO.cleanup()
# Tornado
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("car.html")
    def post(self):
        car = Car()
        arg=self.get_argument('k')
        if(arg=='w'):
            car.front()
        elif(arg=='s'):
            car.rear()
        elif(arg=='a'):
            car.rightRear()
        elif(arg=='d'):
            car.leftRear()
        elif(arg=='q'):
            car.rightFront()
        elif(arg=='e'):
            car.leftFront()
        else:
            return False
        self.write(arg)

# Blinker
async def button_callback(msg):
	car = Car()
	state = list(msg)
	print("Button:{0}".format(state[0]))
	if state[0] == "btn-iza":
		car.front()
	elif state[0] == "btn-rkc":
		car.rear()
	elif state[0] == "btn-ysg":
		car.rightFront()
	elif state[0] == "btn-g3h":
		car.leftFront()
	elif state[0] == "btn-8wl":
		car.rightRear()
	elif state[0] == "btn-pog":
		car.leftRear()
	else:
		print("run false!!!!")
		return False

async def joys_callback(msg):
    x_y_list = list(msg["joy-g8k"])
    x = int(int(x_y_list[0])/1.42)
    y = int(int(x_y_list[1])/1.42)
    print('x:', x)
    print('y:', y)
    
    #change角度
    if x < 90:
	    for i in range(90,x,-1):
		    set_servo_angle(channel1,i)
    elif x > 90:
	    for i in range(90,x,1):
		    set_servo_angle(channel1,i)
    else:
	    set_servo_angle(channel1,x)
	    
    if y < 90:
	    for i in range(90,y,-1):
		    set_servo_angle(channel2,i)
    elif y > 90:
	    for i in range(90,y,1):
		    set_servo_angle(channel2,i)
    else:
	    set_servo_angle(channel2,y)

async def range_callback(msg):
	state = list(msg)
	print("Range:{0}".format(state[0]))
	if state[0] == "ran-dpg":
		x_list = msg["ran-dpg"]
		print('x:', x_list)
		if x_list <= 90:
			for x in range(90,x_list,-1):
				set_servo_angle(channel1,x)
		else:
			for x in range(90,x_list,1):
				set_servo_angle(channel1,x)
	elif state[0] == "ran-kxj":
		y_list = msg["ran-kxj"]
		print('y:', y_list)
		if y_list <= 90:
			for y in range(90,y_list,-1):
				set_servo_angle(channel2,y)
		else:
			for y in range(90,y_list,1):
				set_servo_angle(channel2,y)
	else:
		print("!!!!!!!!!!!!!!!!!!!!!!!!!")

button_qian.func = button_callback
button_hou.func = button_callback
button_zuoqian.func = button_callback
button_youqian.func = button_callback
button_zuohou.func = button_callback
button_youhou.func = button_callback
joy1.func = joys_callback
range1.func = range_callback
range2.func = range_callback

if __name__ == '__main__':
    beangle = 90 #初始角度
    beangle0 = 90
    
    #舵机插的通道口
    channel1 = 4 #左右
    channel2 = 8 #上下
    
    #初始化角度
    set_servo_angle(channel1,beangle)
    set_servo_angle(channel2,beangle0)
    
    print("choose A or Other:")
    ch = input()
    if ch == "A":
        device.run()
    else:
        tornado.options.parse_command_line()
        app = tornado.web.Application(handlers=[(r"/",IndexHandler)])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        print("Demo is runing at "+str(options.port))
        tornado.ioloop.IOLoop.instance().start()
