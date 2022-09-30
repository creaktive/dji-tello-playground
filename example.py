from djitellopy import Tello

tello = Tello('192.168.178.42')

tello.connect()
tello.takeoff()

tello.move_left(100)
tello.rotate_counter_clockwise(90)
tello.move_forward(100)

tello.land()
