from Image_processing import *

image = 'mona.jpg'
mona_lisa = Image_processing(image)
mona_lisa.import_image()
mona_lisa.upper_frame()
mona_lisa.define_bounds()
mona_lisa.threshold_dark = 60
mona_lisa.threshold_light = 100
mona_lisa.getting_points_pixels()
mona_lisa.image_transformation()
mona_lisa.round_drawing_points()
mona_lisa.drawing_points_processing()
mona_lisa.get_move_to_new_drawing_line()
mona_lisa.move_to_line_processing()
mona_lisa.plot_points()
mona_lisa.plot_drawing_lines()
mona_lisa.Save_results()
mona_lisa.Send_results()

image = 'author.jpg'
author = Image_processing(image)
author.import_image()
author.upper_frame()
author.define_bounds()
author.threshold_dark = 90
author.threshold_light = 120
author.getting_points_pixels()
author.image_transformation()
author.round_drawing_points()
author.drawing_points_processing()
author.get_move_to_new_drawing_line()
author.move_to_line_processing()
author.plot_points()
author.plot_drawing_lines()
author.Save_results()
author.Send_results()