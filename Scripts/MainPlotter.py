
from Plotter import *

plotter = Plotter()
plotter.move_to_start_point()
plotter.drive_xy()
txt_file = input('Enter_image_name:')
txt_file = str(txt_file)
plotter.plot_dark_lines(txt_file)
plotter.pen_up()
plotter.default_pisition()
plotter.plot_light_lines(txt_file)
plotter.pen_up()
plotter.default_pisition()
