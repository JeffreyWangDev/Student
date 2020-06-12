"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

A simple program which can be used to manually test racecar_utils functionality.
"""

########################################################################################
# Imports
########################################################################################

import math
import sys

sys.path.insert(0, "../library")
from racecar_core import Racecar
import racecar_utils as rc_utils

########################################################################################
# DO NOT MODIFY: Create Racecar Instance
########################################################################################

rc: Racecar

# Create a RaceacarSim (used to interface with the Unity simulation) if the user ran
# the program with the -s flag
if len(sys.argv) > 1 and sys.argv[1] == "-s":
    sys.path.insert(0, "../library/simulation")
    from racecar_core_sim import RacecarSim

    rc = RacecarSim()

# Otherwise, create a RacecarReal (used to run on the physical car)
else:
    sys.path.insert(0, "../library/real")
    from racecar_core_real import RacecarReal

    rc = RacecarReal()

########################################################################################
# Global variables
########################################################################################

max_speed = 0
show_triggers = False
show_joysticks = False

RED = ((170, 50, 50), (10, 255, 255))

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    global max_speed
    global show_triggers
    global show_joysticks

    print("Start function called")
    rc.set_update_slow_time(0.5)
    rc.drive.stop()

    max_speed = 0.25
    show_triggers = False
    show_joysticks = False

    assert rc_utils.remap_range(5, 0, 10, 0, 50) == 25
    assert rc_utils.remap_range(5, 0, 20, 1000, 900) == 975
    assert rc_utils.remap_range(2, 0, 1, -10, 10) == 30
    assert rc_utils.remap_range(2, 0, 1, -10, 10, True) == 10


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # Display the color image cropped to the top left
    if rc.controller.was_pressed(rc.controller.Button.A):
        image = rc.camera.get_color_image()
        cropped = rc_utils.crop(
            image, (0, 0), (rc.camera.get_height() // 2, rc.camera.get_width() // 2)
        )
        rc.display.show_color_image(cropped)

    # Find and display the largest red contour in the color image
    if rc.controller.was_pressed(rc.controller.Button.B):
        image = rc.camera.get_color_image()
        contours = rc_utils.find_contours(image, RED[0], RED[1])
        largest_contour = rc_utils.get_largest_contour(contours)

        if largest_contour is not None:
            center = rc_utils.get_contour_center(largest_contour)
            area = rc_utils.get_contour_area(largest_contour)
            print("Largest red contour: center={}, area={:.2f}".format(center, area))
            rc_utils.draw_contour(image, largest_contour, rc_utils.ColorBGR.green.value)
            rc_utils.draw_circle(image, center, rc_utils.ColorBGR.yellow.value)
            rc.display.show_color_image(image)
        else:
            print("No red contours found")

    # Print depth image statistics and show the cropped upper half
    if rc.controller.was_pressed(rc.controller.Button.X):
        depth_image = rc.camera.get_depth_image()
        center_distance = rc_utils.get_pixel_average_distance(
            depth_image, (rc.camera.get_width() // 4, rc.camera.get_height() // 2),
        )
        left_distance = rc_utils.get_depth_image_center_distance(depth_image)
        right_distance = rc_utils.get_pixel_average_distance(
            depth_image, (3 * rc.camera.get_width() // 4, rc.camera.get_height() // 2),
        )
        print("Depth image center distance: {:.2f} cm".format(center_distance))
        print("Depth image left distance: {:.2f} cm".format(left_distance))
        print("Depth image right distance: {:.2f} cm".format(right_distance))

        cropped = rc_utils.crop(
            depth_image, (0, 0), (rc.camera.get_height() // 2, rc.camera.get_width())
        )
        closest_point = rc_utils.get_closest_pixel(depth_image)
        print(
            "Depth image closest point (upper half): (row={}, col={})".format(
                closest_point[0], closest_point[1]
            )
        )
        rc.display.show_depth_image(cropped)

    # Print lidar statistics and show visualization
    if rc.controller.was_pressed(rc.controller.Button.Y):
        lidar = rc.lidar.get_samples()
        rc.display.show_lidar(lidar)
        front_distance = rc_utils.get_lidar_average_distance(lidar, 0)
        right_distance = rc_utils.get_lidar_average_distance(lidar, 90)
        back_distance = rc_utils.get_lidar_average_distance(lidar, 180)
        left_distance = rc_utils.get_lidar_average_distance(lidar, 270)
        print("Front LIDAR distance: {:.2f} cm".format(front_distance))
        print("Right LIDAR distance: {:.2f} cm".format(right_distance))
        print("Back LIDAR distance: {:.2f} cm".format(back_distance))
        print("Left LIDAR distance: {:.2f} cm".format(left_distance))

        closest_angle, closest_distance = rc_utils.get_lidar_closest_point(lidar)
        print(
            "Closest LIDAR point: {:.2f} degrees, {:2f} cm".format(
                closest_angle, closest_distance
            )
        )

    # Print lidar distance in the direction the right joystick is pointed
    rjoy_x, rjoy_y = rc.controller.get_joystick(rc.controller.Joystick.RIGHT)
    if abs(rjoy_x) > 0 or abs(rjoy_y) > 0:
        lidar = rc.lidar.get_samples()
        angle = (math.atan2(rjoy_x, rjoy_y) * 180 / math.pi) % 360
        print(
            "LIDAR distance at angle {:.2f} = {:.2f} cm".format(
                angle, rc_utils.get_lidar_average_distance(lidar, angle)
            )
        )

    # Default drive-style controls
    left_trigger = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    right_trigger = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    left_joystick = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
    rc.drive.set_speed_angle(right_trigger - left_trigger, left_joystick[0])


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
