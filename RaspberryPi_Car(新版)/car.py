import RPi.GPIO as GPIO
import time
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import Adafruit_PCA9685
from tornado.options import define,options

define("port",default=8081,help="run on the given port",type=int)

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

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
        self.render("newCar.html")
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

class ReceiveXYHandler(tornado.web.RequestHandler):
    def post(self):
        x = int(float(self.get_argument("x"))*0.9)
        y = int(float(self.get_argument("y"))*0.9)
        print("x坐标为：", x)
        print("y坐标为：", y)
        self.write("OK") # 发送响应
        if(y<=0):
            end_y = 90 - y
            set_servo_angle(channel2,end_y)
        else:
            end_y = 90 - y
            set_servo_angle(channel2,end_y)
        if(x<=0):
            end_x = 90 - x
            set_servo_angle(channel1,end_x)
        else:
            end_x = 90 - x
            set_servo_angle(channel1,end_x)

if __name__ == '__main__':
    beangle = 90 #初始角度
    beangle0 = 140
    
    #舵机插的通道口
    channel1 = 4 #左右
    channel2 = 8 #上下
    
    #变化幅度（这个越大，舵机动的幅度就越大）
    angleFreq = 1
    
    #初始化角度
    set_servo_angle(channel1,beangle)
    set_servo_angle(channel2,beangle0)
    
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/",IndexHandler),(r"/receiveXY", ReceiveXYHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("start success!!")
    tornado.ioloop.IOLoop.instance().start()
