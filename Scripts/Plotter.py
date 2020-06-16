
import RPi.GPIO as GPIO
from time import sleep
import readchar
import math
import numpy
import json
import pigpio


class Plotter():
    def __init__(self):
        ### STEPPER MOTORS
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.motor_channel_2 = (6, 13, 19, 26)
        self.motor_channel_1 = (12, 16, 20, 21)
        GPIO.setup(self.motor_channel_1, GPIO.OUT)
        GPIO.setup(self.motor_channel_2, GPIO.OUT)
        self.delay = 0.01
        ### SERVO MOTORS
        self.servo_pin = 3
        self.rpi = pigpio.pi()
        self.rpi.set_PWM_frequency(self.servo_pin, 50)
        self.rpi.set_servo_pulsewidth(self.servo_pin, 1500)
        ### Početni položaj manipulatora
        self.arm_1 = 9.2   # Stvaran dužina unutarnje ruke izmjerena na konstrukciji[cm]
        self.arm_2 = 10.5 # Stvarna dužina vanjske ruke izmjerena na konstrukciji[cm]
        self.current_x = 10.5   # Trenutni x prema matematičkom modelu[cm]
        self.current_y = 9.2   # Trenutni y prema matematičkom modelu[cm]
        self.alfa = 90  # Trenutni/početni kut prvog koračnog motroa
        self.beta = 90  # Trenutni/početni kut drugog koračnog motroa
        #Stupanj za koji se koračni motor rotira za jedan korak
        self.step_angle = 0.703125
        # Greška koju manipulator stvara zbog prevelikog stupnja pomaka koračnog motra
        self.error1 = 0  # Greška za prvi motor
        self.error2 = 0  # Greška za drugi motor
        # Brojač broja koraka koje manipulatori naprave tokom ispisa fotografije
        self.final_steps_count1 = 0  # Ukupan broj koraka prvog koračnog motora
        self.final_steps_count2 = 0  # Ukupan broj koraka drugog koračnog motora
        # Broj koraka koje manipulator napravi da dođe iz jednog položaja u drugi
        self.round_steps_count1 = 0  # Broj koraka prvog koračnog motora
        self.round_steps_count2 = 0 # Broj koraka drugog koračnog motora
        # Granice rada manipulatora
        self.bounds = (6, -8, 17, 8)
        # Brojač linija
        self.count_line2 = 0
        self.count_line1 = 0
        # Okidač
        self.first1  = True
        self.first2 = True

    ### METODA ZA PODIZANJE KEMIJSKE OLOVKE OD PODLOGE MANIPULATORA
    def pen_up(self):
        self.rpi.set_servo_pulsewidth(self.servo_pin, 1500)
        sleep(0.1)
    ### METODA ZA SPUŠTANJE KEMIJSKE OLOVKE NA PODLOGU MANIPULATORA
    def pen_down(self):
        self.rpi.set_servo_pulsewidth(self.servo_pin, 1000)
        sleep(0.1)

    ### mETODA ZA POKRETANJE PRVOG KORAČNOG MOTORA U OBRNUTOM SMJERU KAZALJKE NA SATU
    def move_anti_clockwise_1(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)

    ### METODA ZA POKRETANJE DRUGOG KORAČNOG MOTORA U SMJERU KAZALJKE NA SATU
    def move_clockwise_2(self):
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)

    ### METODA ZA POKRETANJE PRVOG KORAČNOG MOTORA U SMJERU KAZALJKE NA SATU
    def move_clockwise_1(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)

    ### METODA ZA POKRETANJE DRUGOG KORAČNOG MOTORA U OBRNUTOM SMJERU KAZALJKE NA SATU
    def move_anti_clockwise_2(self):
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)

    ### METODA ZA POKRETANJE PRVOG KORAČNOG MOTORA U OBRNUTOM SMJERU KAZALJE NA SATU I DRUGOG MOTORA U SMJERU KAZALJKE NA SATU
    def move_anti1_clock2(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)

    ### METODA ZA POKRETANJE PRVOG KORAČNOG MOTORA U SMJERU KAZALJE NA SATU I DRUGOG MOTORA U SMJERU OBRNUTOM OD KAZALJKE NA SATU
    def move_clock1_anti2(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)

    ### METODA ZA POKRETANJE KORAČNIH MOTORA U OBRNUTOM SMJERU KAZALJKE NA SATU
    def move_anti_clockwise_12(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)

    ### METODA ZA POKRETANJE OBA KORAČNA MOTORA U SMJERU KAZALJKE NA SATU
    def move_clocwise_12(self):
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        GPIO.output(self.motor_channel_2, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        sleep(self.delay)
        GPIO.output(self.motor_channel_1, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
        GPIO.output(self.motor_channel_2, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
        sleep(self.delay)

    ### METODA ZA POKRETANJE KORAČNIH MOTORA U ODNOSU NA IZRAČUNATI BROJ KORAKA
    def move_motors_by_step_count(self):
        while self.round_steps_count1 != 0 or self.round_steps_count2 != 0:
            if self.round_steps_count1 >= 1 and self.round_steps_count2 >= 1:
                self.move_clocwise_12()
                self.round_steps_count1 -= 1
                self.round_steps_count2 -= 1
                print(self.round_steps_count1,self.round_steps_count2)
            elif self.round_steps_count1 <= -1 and self.round_steps_count2 >= 1:
                self.move_anti1_clock2()
                self.round_steps_count1 += 1
                self.round_steps_count2 -= 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count1 <= -1 and self.round_steps_count2 <= -1:
                self.move_anti_clockwise_12()
                self.round_steps_count1 += 1
                self.round_steps_count2 += 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count1 >= 1 and self.round_steps_count2 <= -1:
                self.move_clock1_anti2()
                self.round_steps_count1 -= 1
                self.round_steps_count2 += 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count1 >= 1:
                self.move_clockwise_1()
                self.round_steps_count1 -= 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count1 <= -1:
                self.move_anti_clockwise_1()
                self.round_steps_count1 += 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count2 >= 1:
                self.move_clockwise_2()
                self.round_steps_count2 -= 1
                print(self.round_steps_count1, self.round_steps_count2)
            elif self.round_steps_count2 <= -1:
                self.move_anti_clockwise_2()
                self.round_steps_count2 += 1
                print(self.round_steps_count1, self.round_steps_count2)

    def get_position_xy(self):

        ###IMPLEMENTACIJA MATEMATIČKOG MODELA
        omega_x = math.atan(self.current_y / self.current_x)
        AC = self.current_x / math.cos(omega_x)
        gama = math.acos((AC ** 2 + self.arm_1 ** 2 - self.arm_2 ** 2) / (2 * self.arm_1 * AC))
        new_alfa = omega_x +  gama
        new_alfa_degrees = math.degrees(new_alfa)
        epsilon = math.acos((self.arm_1 ** 2 + self.arm_2 ** 2 - AC ** 2) / (2 * self.arm_1 * self.arm_2))
        new_beta = epsilon
        new_beta_degrees = math.degrees(new_beta)
        ### RAČUNAJE BROJA KORAKA KOJE MOTOR TREBA NAPRAVIT DA ZAUZME NOVI KUT
        delta_1 = self.alfa - new_alfa_degrees
        # self.alfa = new_alfa_degrees
        delta_2 = self.beta - new_beta_degrees
        # self.beta = new_beta_degrees
        print('Stepper_angle1: ', self.alfa, ' degrees', 'Stepper_angle2: ',
              self.beta, ' degrees')
        count_steps1 = delta_1 / self.step_angle
        count_steps2 = delta_2 / self.step_angle
        count_steps1 += self.error1
        count_steps2 += self.error2
        self.round_steps_count1 = round(count_steps1)
        self.round_steps_count2= round(count_steps2)
        self.final_steps_count1 += self.round_steps_count1
        self.final_steps_count2 += self.round_steps_count2
        # self.error1 = count_steps1 - self.round_steps_count1
        # self.error2 = count_steps2 - self.round_steps_count2
        self.alfa -= self.round_steps_count1 * self.step_angle
        self.beta -= self.round_steps_count2 * self.step_angle
        print(self.round_steps_count1,self.round_steps_count2)
        #POKRETANJE MOTORA
        self.move_motors_by_step_count()


    ### METODA ZA UPRAVLJANJE MANIPULATOROM U X-Y KOORDINATNOM SUSTAVU MANIPULATORA
    def drive_xy(self):
        while True:
            key = readchar.readchar()
            if key == "q":
                return
            elif key == "w":
                self.current_y = self.current_y + 0.1
            elif key == "s":
                self.current_y = self.current_y - 0.1
            elif key == "d":
                self.current_x = self.current_x + 0.1
            elif key == "a":
                self.current_x = self.current_x - 0.1
            elif key == 't':
                self.pen_up()
                print('Pen up!')
            elif key == 'g':
                self.pen_down()
                print('Pen down!')
            print('X_Y: ', round(self.current_x,1), round(self.current_y,1))
            self.get_position_xy()



    ### METODA ZA DOBIVANJE LINIJA GRANICA MANIPULATORA
    def get_box(self):
        start_point = (self.bounds[0], self.bounds[1])
        line = list(zip(numpy.linspace(self.current_x, start_point[0], 50),
                        numpy.linspace(self.current_y, start_point[1], 50)))
        print(line)
        for x_y in line:
            self.current_x = x_y[0]
            self.current_y = x_y[1]
            self.get_position_xy()

    ### METODA ZA ISPIS GRANICA MANIPULATORA ODREĐENOG PRAVOKUTNIKOM U KOJEM JE OMOGUĆENO ISPISIVANJE
    def draw_box(self):
        self.pen_up()
        self.get_box()
        self.pen_down()
        for y in numpy.arange(self.bounds[1], self.bounds[3], 0.05):
            self.current_y = y
            self.get_position_xy()
        for x in numpy.arange(self.bounds[0], self.bounds[2], 0.05):
            self.current_x = x
            self.get_position_xy()
        for y in numpy.arange(self.bounds[3], self.bounds[1], -0.05):
            self.current_y = y
            self.get_position_xy()
        for x in numpy.arange(self.bounds[2], self.bounds[0], -0.05):
            self.current_x = x
            self.get_position_xy()

    ###METODA ZA  ISPISIVANJE TAMNIH TONOVA FOTOGRAFIJE
    def plot_dark_lines(self,file):

        with open(file, 'r') as dict_points:
            points = json.load(dict_points)
            drawing_line_points = points['dark_points']
            move_to_new_line_points = points['move_to_new_line_dark']

        for l in drawing_line_points:
            self.pen_up()
            print('Going to line: ', self.count_line2 + 1, '/', len(drawing_line_points))
            for xy in move_to_new_line_points[self.count_line2]:
                print('X_Y: ', xy)
                self.current_x = xy[0]
                self.current_y = xy[1]
                self.get_position_xy()
            self.first2 = True
            for x_y in l:
                print('Drawing line: ', self.count_line2 + 1, '/', len(drawing_line_points))
                print('X_Y: ', x_y)
                if self.first2:
                    self.pen_down()
                    self.first2 = False
                self.current_x = x_y[0]
                self.current_y = x_y[1]
                self.get_position_xy()

            self.count_line2 += 1
        print('Line :', self.count_line2, '/', len(drawing_line_points), ' drawn')

    ### METODA ZA CRTANJE SVIJETLIH TONOVA FOTOGRAFIJE
    def plot_light_lines(self,file):

        with open(file, 'r') as dict_points:
            points = json.load(dict_points)
            drawing_line_points = points['light_points']
            move_to_new_line_points = points['move_to_new_line_light']

        for l in drawing_line_points:
            self.pen_up()
            print('Going to line: ', self.count_line2 + 1,'/', len(drawing_line_points))
            for xy in move_to_new_line_points[self.count_line2]:
                print('X_Y: ', xy)
                self.current_x = xy[0]
                self.current_y = xy[1]
                self.get_position_xy()
            self.first2 = True
            for x_y in l:
                print('Drawing line: ', self.count_line2 + 1, '/', len(drawing_line_points))
                print('X_Y: ', x_y)
                if self.first2:
                    self.pen_down()
                    self.first2 = False
                self.current_x = x_y[0]
                self.current_y = x_y[1]
                self.get_position_xy()

            self.count_line2 += 1
        print('Line :', self.count_line2,'/', len(drawing_line_points) ,' drawn')

    ### METODA ZA POSTAVLJANJE MANIPULATORA U POČETNI POLOŽAJ PRIJE POKRETANJA ISPISIVANJA
    def move_to_start_point(self):

        while True:
            key = readchar.readchar()

            if key == "e":
                self.move_clockwise_1()
                print('Moving stepper_1 anticlockwise')
            elif key == "w":
                self.move_anti_clockwise_1()
                print('Moving stepper_1 clockwise')
            elif key == "s":
                self.move_anti_clockwise_2()
                print('Moving stepper_2 anticlockwise')
            elif key == "d":
                self.move_clockwise_2()
                print('Moving stepper_2 clockwise')
            elif key == 't':
                self.pen_up()
                print('Pen up!')
            elif key =='g':
                self.pen_down()
                print('Pen down!')
            elif key == "q":
                break

    ### METODA ZA VRAČANJE MANIPULATORA U POČETNI POLOŽAJ
    def default_pisition(self):
        print('going to starting position')
        self.error1 = 0
        self.error2 = 0
        self.alfa = 90
        self.beta  = 90
        self.count_line2 = 0
        self.count_line1 = 0
        self.first1 = True
        self.first2 = True
        while self.final_steps_count1 != 0 or self.final_steps_count2 != 0:
            print(self.final_steps_count1, self.final_steps_count2)
            if self.final_steps_count1 >= 1:
                self.move_anti_clockwise_1()
                self.final_steps_count1 -= 1
            if self.final_steps_count1 <= -1:
                self.move_clockwise_1()
                self.final_steps_count1 += 1
            if self.final_steps_count2 >= 1:
                self.move_anti_clockwise_2()
                self.final_steps_count2 -= 1
            if self.final_steps_count2 <= -1:
                self.move_clockwise_2()
                self.final_steps_count2 += 1
            
