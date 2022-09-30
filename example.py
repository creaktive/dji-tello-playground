from djitellopy import Tello
import socket

tello = Tello(socket.gethostbyname('tello'), 1)

tello.connect()
tello.takeoff()

tello.move_left(100)
tello.rotate_counter_clockwise(90)
tello.move_forward(100)

tello.land()
