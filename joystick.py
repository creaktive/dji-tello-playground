#!/usr/bin/env python3
from djitellopy import Tello
import pygame
import signal
import socket
import subprocess

pygame.init()
# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

def main():
    tello = Tello(socket.gethostbyname('tello'), 1)
    video = None
    speed = 10
    try:
        tello.connect()
        tello.set_speed(speed)
        tello.streamoff()
        tello.streamon()

        video = subprocess.Popen(['./video-receiver.sh'])

        # Set the width and height of the screen (width, height), and name the window.
        screen = pygame.display.set_mode((500, 700))
        pygame.display.set_caption("Joystick example")

        # Used to manage how fast the screen updates.
        clock = pygame.time.Clock()

        # Get ready to print.
        text_print = TextPrint()

        # This dict can be left as-is, since pygame will generate a
        # pygame.JOYDEVICEADDED event for every joystick connected
        # at the start of the program.
        joysticks = {}

        done = False
        airborne = False
        trimming = False
        rc = [0, 0, 0, 0]
        trim = rc
        while not done:
            # Event processing step.
            # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
            # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Flag that we are done so we exit this loop.

                if event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                    print(event)
                    if airborne and event.button == 0:
                        trimming = True
                    elif event.button == 1:
                        trim = [0, 0, 0, 0]
                    elif not airborne and event.button == 5:
                        tello.takeoff()
                        airborne = True
                    elif airborne and event.button == 3:
                        tello.land()
                        airborne = False
                    elif airborne and event.button == 4:
                        speed = min(speed + 30, 100)
                        tello.set_speed(speed)
                    elif airborne and event.button == 2:
                        speed = max(speed - 30, 10)
                        tello.set_speed(speed)

                if event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")
                    if event.button == 0:
                        trimming = False

                # Handle hot-plugging
                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connected")

                if event.type == pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")

                if event.type == pygame.JOYHATMOTION:
                    print("Joystick hat motion.")
                    print(event)
                    if airborne and event.value[0] == -1:
                        tello.flip_left()
                    elif airborne and event.value[0] == 1:
                        tello.flip_right()
                    elif airborne and event.value[1] == -1:
                        tello.flip_back()
                    elif airborne and event.value[1] == 1:
                        tello.flip_forward()

            # Drawing step
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            screen.fill((255, 255, 255))
            text_print.reset()

            # Get count of joysticks.
            joystick_count = pygame.joystick.get_count()

            text_print.tprint(screen, f"control axis: {rc}")
            text_print.tprint(screen, f"battery: {tello.get_battery()}")
            text_print.indent()

            # For each joystick:
            for joystick in joysticks.values():
                jid = joystick.get_instance_id()

                text_print.tprint(screen, f"Joystick {jid}")
                text_print.indent()

                # Get the name from the OS for the controller/joystick.
                name = joystick.get_name()
                text_print.tprint(screen, f"Joystick name: {name}")

                guid = joystick.get_guid()
                text_print.tprint(screen, f"GUID: {guid}")

                power_level = joystick.get_power_level()
                text_print.tprint(screen, f"Joystick's power level: {power_level}")

                # Usually axis run in pairs, up/down for one, and left/right for
                # the other. Triggers count as axes.
                axes = joystick.get_numaxes()
                text_print.tprint(screen, f"Number of axes: {axes}")
                text_print.indent()

                for i in range(axes):
                    axis = joystick.get_axis(i)
                    text_print.tprint(screen, f"Axis {i} value: {axis:>6.3f}")
                text_print.unindent()

                buttons = joystick.get_numbuttons()
                text_print.tprint(screen, f"Number of buttons: {buttons}")
                text_print.indent()

                for i in range(buttons):
                    button = joystick.get_button(i)
                    text_print.tprint(screen, f"Button {i:>2} value: {button}")
                text_print.unindent()

                hats = joystick.get_numhats()
                text_print.tprint(screen, f"Number of hats: {hats}")
                text_print.indent()

                # Hat position. All or nothing for direction, not a float like
                # get_axis(). Position is a tuple of int values (x, y).
                for i in range(hats):
                    hat = joystick.get_hat(i)
                    text_print.tprint(screen, f"Hat {i} value: {str(hat)}")
                text_print.unindent()

                text_print.unindent()

                if airborne:
                    rc = [joystick.get_axis(i) for i in range(axes)]
                    rc[1] *= -1
                    rc[3] *= -1
                    if trimming:
                        trim = rc
                    rc = [round(pow(rc[i] - trim[i], 3) * 100) for i in range(axes)]
                    tello.send_rc_control(rc[0], rc[1], rc[3], rc[2])

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # Limit to 30 frames per second.
            clock.tick(30)

    except BaseException as msg:
        print(msg)

    finally:
        if video != None:
            video.send_signal(signal.SIGKILL)
            video.wait()

        tello.end()

if __name__ == "__main__":
    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
