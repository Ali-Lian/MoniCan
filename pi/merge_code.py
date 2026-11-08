import RPi.GPIO as GPIO
import time
import mysql.connector
from mysql.connector import Error
from mfrc522 import SimpleMFRC522
from datetime import datetime

# 重量感測器
class HX711:
    def setup(self):
        self.SCK = 27  # GPIO 27 (Physical Pin 13)
        self.DT = 17   # GPIO 17 (Physical Pin 11)
        self.flag = 1
        self.initweight = 0
        self.weight = 0
        self.delay = 0.09
        self.scale_factor = 20  # Example scale factor, need calibration
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.DT, GPIO.IN)
        GPIO.setup(self.DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.output(self.SCK, 0)
        if GPIO.input(self.SCK):
            time.sleep(self.delay)
        value = 0
        while GPIO.input(self.DT):
            time.sleep(self.delay)
        for i in range(24):
            GPIO.output(self.SCK, 1)
            if GPIO.input(self.SCK) == 0:
                time.sleep(self.delay)
            value = value << 1
            GPIO.output(self.SCK, 0)
            if GPIO.input(self.SCK):
                time.sleep(self.delay)
            if GPIO.input(self.DT) == 1:
                value += 1
        GPIO.output(self.SCK, 1)
        GPIO.output(self.SCK, 0)
        value = int(value / self.scale_factor)
        if self.flag == 1:
            self.flag = 0
            self.initweight = value
        else:
            self.weight = abs(value - self.initweight)
            print(self.weight)
        return self.weight

# 超音波感測器
class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)
        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        elapsed_time = stop_time - start_time
        distance = (elapsed_time * 34300) / 2
        return distance

# 伺服馬達
class ServoMotor:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)  # 50Hz PWM frequency
        self.pwm.start(0)

    def rotate(self, angle):
        duty_cycle = self.angle_to_duty_cycle(angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(2)  # Give the servo time to move
        self.pwm.ChangeDutyCycle(0)  # Stop the PWM signal

    def angle_to_duty_cycle(self, angle):
        return 2 + (angle / 18)

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup(self.pin)

# Connect to the MySQL/MariaDB database
connection = mysql.connector.connect(
    host='192.168.137.1',          # Hostname
    database='canproj',             # Database name
    user='pi',                      # Username
    password='0000'                 # Password
)

try:
    if connection.is_connected():
        print("Connected to the database")
        cursor = connection.cursor()

        # Setup GPIO mode once
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        reader = SimpleMFRC522()
        hx711 = HX711()
        hx711.setup()

        ultrasonic_sensor = UltrasonicSensor(trig_pin=23, echo_pin=24)
        servo_motor = ServoMotor(pin=18)

        while True:
            print("Please place the RFID tag near the reader...")
            id, text = reader.read()
            print("Tag ID:", id)
            print("Tag Content:", text)

            cursor.execute("SELECT RFID_id FROM customer WHERE RFID_id = %s", (id,))
            result = cursor.fetchone()

            if result: # 資料庫中有RFID ID，開始測量
                print("RFID ID found in the database. Starting weight measurement.")
                time.sleep(1.5)
                servo_motor.rotate(85)  # Rotate servo to 85 degrees (開垃圾桶)
                time.sleep(1.5)  # Wait for the servo to finish moving

                weight = hx711.start()
                time.sleep(2)
                print(f'Weight: {weight:.2f} grams')  # Print the weight each loop iteration
                time.sleep(2)
                distance = ultrasonic_sensor.get_distance()
                print(f'Distance: {distance:.2f} cm')  # Print the distance each loop iteration

                # Get current time
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 將物聯網數據傳入資料庫
                insert_query = "INSERT INTO record (trashCanID, weight, distance, timeStamp) VALUES (%s, %s, %s, %s)"
                data = (1, weight, distance, current_time)
                cursor.execute(insert_query, data)
                connection.commit()

                servo_motor.rotate(180)
            else: # 資料庫中無RFID ID，提示使用者重新嘗試
                print("RFID ID not found in the database. Please try again.")

            time.sleep(1)  # Wait for 1 second

except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
    servo_motor.cleanup()
    GPIO.cleanup()