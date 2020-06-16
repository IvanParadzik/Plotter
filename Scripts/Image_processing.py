from numpy import interp
import json
import numpy as np
import math
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import subprocess

from Functions_image import *

###### STATIČKE FUNKCIJE ##############

# FUNKCIJA ZA ZAOKRUŽIVANJE BROJEVA NA ODREĐENI DECIMALNI BROJ
def round_nearest(x, a):
    return round(round(x / a) * a, -int(math.floor(math.log10(a))))

# FUNKCIJA ZA ROTIRANJE FOTOGRAFIJE
def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))



class Image_processing():
    def __init__(self,photo):
        self.photo = photo
        # Vrijednosti na koje ukazuju na kojoj su udaljenosti paralelene linije ispisivanja
        self.width_between_line_light = 0.1   # za svijetle tonove 0.1 cm
        self.width_between_line_dark = 0.05  # za tamne tonove 0.05 cm
        self.width_y = 0.05
        # Brojka s kojom dobivamo cijeli broj zaokruženih točaka gibanja manipulatora
        self.get_round_01 = 10
        self.get_round_005 = 100
        # Pragovi tonovoa za koje manipulator ispisuje fotografiju
        self.threshold_dark = 75
        self.threshold_light = 110
        #Granice pravokutnika unutar kojih manipulator ispisjue fotografije
        self.bounds = [5, -8, 17, 10]
        # Liste u koje spremamo vrijedosti piksela
        self.Vertical_light_lines = [] # Liste točaka koje predstavljaju tamne tonove u koordinatno sustavu fotografije
        self.Vertical_dark_lines = []
        # Liste u koje se spremaju transformirane točke
        self.Vertical_light_lines_transformed = []
        self.Vertical_dark_lines_transformed = []
        # Liste u koje se spremaju zaokružene točke u koordinatnom sustavu manipulatora
        self.Vertical_dark_lines_round = []
        self.Vertical_light_lines_round = []
        # Starting pen position
        self.default_position = [10.5, 9.2]
        # Defining list for point which defines movement of manipulator when not drawing
        self.Move_to_line_dark = []
        self.Move_to_line_light = []



    def import_image(self):
        self.image = cv2.imread(self.photo,cv2.IMREAD_GRAYSCALE )
        (self.height, self.width) = self.image.shape[:2]
        # Rotiranje ako je širina veća od visine fotografije
        if self.width > self.height:
            self.image= rotate_bound(self.image, angle=-90)
            (self.height, self.width) = self.image.shape[:2]
            cv2.imshow('Imported Image',self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            cv2.imshow('Imported Image', self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        cv2.imwrite('gray.jpg', self.image)
    def upper_frame(self):
        threshold_line_dark = 0
        threshold_line_light = self.threshold_light - 10
        thickness_line_dark = int(self.height/65)
        thickness_line_light = thickness_line_dark*2
        start_point1 = (0, 0)
        end_point1 = (self.width, 0)
        color1 = (threshold_line_dark,threshold_line_dark , threshold_line_dark)
        color2 = (threshold_line_light, threshold_line_light, threshold_line_light)
        start_point2 = (0, int((thickness_line_dark + thickness_line_light) / 2))
        end_point2 = (self.width, int((thickness_line_dark + thickness_line_light) / 2))
        self.line_image = cv2.line(self.image, start_point1, end_point1, color1, thickness_line_light)
        self.line_image = cv2.line(self.line_image, start_point2, end_point2, color2, thickness_line_dark)
        self.framed_photo = self.photo[:-4] + '_line.jpg'
        cv2.imwrite(self.framed_photo, self.line_image)
        cv2.imshow('line_image', self.line_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def define_bounds(self):
        # getting new bound (because of scaling)
        self.bounds[3] = round((self.bounds[1] + (self.bounds[2] - self.bounds[0]) * (self.height / self.width)), 1)
        if self.bounds[3] > 8:
            self.bounds[3] = 8
            self.bounds[2] = round(self.bounds[0] + (self.bounds[3] - self.bounds[1]) * self.width / self.height)
        self.bounds[3] += 1.3
        if (self.height / self.width) * 10 > 14:
            print('Please import photo where ratio of height and width of image is not bigger then 1.4')


        print('Bounds for this image is: ', self.bounds)

    def getting_points_pixels(self):
        self.pixel_image = Image.open(self.framed_photo)
        # self.pixel_image = self.pixel_image.convert("L")
        self.pixels = self.pixel_image.load()
        for x0 in range(self.width):
            line = []
            line_light = []
            for y0 in range(self.height):
                if self.pixels[x0, y0] <= self.threshold_dark:
                    line.append([x0, y0])
                if self.pixels[x0, y0] > self.threshold_dark and self.pixels[x0, y0] <= self.threshold_light:
                    line_light.append([x0, y0])
            self.Vertical_dark_lines.append(line)
            self.Vertical_light_lines.append(line_light)

    def image_transformation(self):
        for line in self.Vertical_dark_lines:
            xy = []
            for points in line:
                x = interp(points[0], [0, self.width], [self.bounds[0], self.bounds[2]])
                y = interp(points[1], [0, self.height], [self.bounds[3], self.bounds[1]])
                x_y = [x, y]
                xy.append(x_y)
            self.Vertical_dark_lines_transformed.append(xy)
        for line in self.Vertical_light_lines:
            xy = []
            for points in line:
                x = interp(points[0], [0, self.width], [self.bounds[0], self.bounds[2]])
                y = interp(points[1], [0, self.height], [self.bounds[3], self.bounds[1]])
                x_y = [x, y]
                xy.append(x_y)
            self.Vertical_light_lines_transformed.append(xy)

    def round_drawing_points(self):
        for line in self.Vertical_dark_lines_transformed:
            round_line = []
            for x_y in line:
                xy = []
                x = round_nearest(x_y[0], self.width_between_line_dark)
                y = round_nearest(x_y[1], self.width_y)
                xy.append(x)
                xy.append(y)
                round_line.append(xy)
            self.Vertical_dark_lines_round.append(round_line)
        for line in self.Vertical_light_lines_transformed:
            round_line = []
            for x_y in line:
                xy = []
                x = round_nearest(x_y[0], self.width_between_line_light)
                y = round_nearest(x_y[1], self.width_y)
                xy.append(x)
                xy.append(y)
                round_line.append(xy)
            self.Vertical_light_lines_round.append(round_line)



    def drawing_points_processing(self):


        # Removed_small_lines_dark_1 = remove_small_lines(self.Vertical_dark_lines_round)
        # Removed_small_lines_light_1 = remove_small_lines(self.Vertical_light_lines_round)

        Removed_same_lines_in_column_dark = remove_same_lines_x(self.Vertical_dark_lines_round, self.get_round_005)
        Removed_same_lines_in_column_light = remove_same_lines_x(self.Vertical_light_lines_round,self.get_round_01 )

        Splitting_lines_from_one_row_dark = split_lines(Removed_same_lines_in_column_dark)
        Splitting_lines_from_one_row_light = split_lines(Removed_same_lines_in_column_light)


        Removed_small_lines_dark = remove_small_lines(Splitting_lines_from_one_row_dark)
        Removed_small_lines_light= remove_small_lines(Splitting_lines_from_one_row_light)

        Removed_same_points_in_one_line_dark = remove_same_points_in_line(Removed_small_lines_dark,
                                                                         self.get_round_005,
                                                                         self.get_round_005,
                                                                        self.width_between_line_dark,
                                                                         self.width_y)
        Removed_same_points_in_one_line_light = remove_same_points_in_line(Removed_small_lines_light,
                                                                         self.get_round_01,
                                                                         self.get_round_005,
                                                                         self.width_between_line_light,
                                                                         self.width_y)


        self.Final_lines_dark = remove_small_lines(Removed_same_points_in_one_line_dark)
        self.Final_lines_light  =remove_small_lines(Removed_same_points_in_one_line_light)
        print(self.Final_lines_dark)

    def get_move_to_new_drawing_line(self):

        x = self.default_position[0]
        y = self.default_position[1]
        for line in self.Final_lines_dark:
            first_point = line[0]
            to_new_line = list(zip(np.linspace(x, first_point[0], 100),
                                   np.linspace(y, first_point[1], 100)))
            self.Move_to_line_dark.append(to_new_line)
            for points in line:
                x= points[0]
                y= points[1]

        x = self.default_position[0]
        y = self.default_position[1]
        for line in self.Final_lines_light:
            first_point = line[0]
            to_new_line = list(zip(np.linspace(x, first_point[0], 100),
                                   np.linspace(y, first_point[1], 100)))
            self.Move_to_line_light.append(to_new_line)
            for points in line:
                x = points[0]
                y = points[1]


    def move_to_line_processing(self):

        Round_move_to_new_line_dark = round_points(self.Move_to_line_dark, self.width_between_line_dark,self.width_y)
        Round_move_to_new_line_light = round_points(self.Move_to_line_light, self.width_between_line_light, self.width_y)
        self.Final_move_to_new_line_dark = remove_same_points_in_line(Round_move_to_new_line_dark,
                                                                      self.get_round_005,
                                                                      self.get_round_005,
                                                                      self.width_between_line_dark,
                                                                      self.width_y)
        self.Final_move_to_new_line_light = remove_same_points_in_line(Round_move_to_new_line_light,
                                                                       self.get_round_01,
                                                                       self.get_round_01,
                                                                       self.width_between_line_light,
                                                                       self.width_y)



    def plot_points(self):
        fig = plt.figure(figsize=(7.5,8))
        plt.xlabel('X [cm]')
        plt.ylabel('Y [cm]')
        plt.xscale("linear")
        plt.yscale("linear")
        for line in self.Final_lines_dark:
            for point in line:
                plt.plot(point[0],point[1], marker='.', markersize=1, color="black")
        for line in self.Final_lines_light:
            for point in line:
                plt.plot(point[0],point[1], marker = '.', markersize = 1, color = 'gray')
        # Draw manipulator arms
        # unutarnja ruka
        plt.plot([0, 0], [0, 10], linewidth=1, color='red')
        # vanjska ruka
        plt.plot([0, 10], [10, 10], linewidth=1, color='blue')
        plt.show()
        fig.savefig('Point_figure.png')

    def plot_drawing_lines(self):
        fig = plt.figure(figsize=(7,8))
        plt.xlabel('X [cm]')
        plt.ylabel('Y [cm] ')
        plt.xscale('linear')
        plt.yscale('linear')
        for line in self.Final_lines_dark:
            x_first = line[0][0]
            y_first = line[0][1]
            x_last = line[-1][0]
            y_last = line[-1][1]
            x = [x_first,x_last]
            y = [y_first,y_last]
            plt.plot(x,y,color= 'black', linewidth = 0.1)
        for line in self.Final_lines_light:
            x_first = line[0][0]
            y_first = line[0][1]
            x_last = line[-1][0]
            y_last = line[-1][1]
            x = [x_first, x_last]
            y = [y_first, y_last]
            plt.plot(x, y, color='black', linewidth = 0.1)
        # Draw manipulator arms
        # unutarnja ruka
        plt.plot([0, 0], [0, 10],linewidth = 1, color='red')
        # vanjska ruka
        plt.plot([0, 10], [10, 10], linewidth = 1, color='blue')
        plt.show()
        fig.savefig('Line_figure.png')




    def Save_results(self):

        self.name_of_txt_file = self.photo[:-4] + '_hatch.txt'
        with open(self.name_of_txt_file, 'w') as point_dic:
            points = {}
            points["dark_points"] = self.Final_lines_dark
            points["move_to_new_line_dark"] = self.Final_move_to_new_line_dark
            points["light_points"] = self.Final_lines_light
            points["move_to_new_line_light"] = self.Final_move_to_new_line_light
            json.dump(points, point_dic, indent=8)

    def Send_results(self):

        cmd = ['scp', 'C:\\Users\\Ivan\\PycharmProjects\\ploter\\'+ self.name_of_txt_file, 'pi@raspberrypi.local:']
        proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


