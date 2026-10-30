"""Fly to one waypoint and hover there (Mavic 2 Pro)."""
import math
from controller import Robot

TARGET = (30.0, -8.0, 3.0)   # x, y, height in metres

K_VERTICAL_THRUST = 68.5
K_VERTICAL_OFFSET = 0.6
K_VERTICAL_P = 3.0
K_ROLL_P = 50.0
K_PITCH_P = 30.0

K_POS = 1.0          # how hard to push towards the target
K_VEL = 2.0          # how hard to brake
MAX_TILT_CMD = 2.0   # limit on how far the drone may lean


def clamp(value, low, high):
    return max(low, min(value, high))


robot = Robot()
timestep = int(robot.getBasicTimeStep())
dt = timestep / 1000.0

imu = robot.getDevice("inertial unit")
imu.enable(timestep)
gps = robot.getDevice("gps")
gps.enable(timestep)
gyro = robot.getDevice("gyro")
gyro.enable(timestep)

front_left = robot.getDevice("front left propeller")
front_right = robot.getDevice("front right propeller")
rear_left = robot.getDevice("rear left propeller")
rear_right = robot.getDevice("rear right propeller")
for motor in (front_left, front_right, rear_left, rear_right):
    motor.setPosition(float("inf"))
    motor.setVelocity(1.0)

# let the sensors settle for one second
while robot.step(timestep) != -1:
    if robot.getTime() > 1.0:
        break

prev_x, prev_y, _ = gps.getValues()
last_print = 0.0

while robot.step(timestep) != -1:
    roll, pitch, yaw = imu.getRollPitchYaw()
    x, y, altitude = gps.getValues()
    roll_velocity, pitch_velocity, _ = gyro.getValues()

    vx = (x - prev_x) / dt
    vy = (y - prev_y) / dt
    prev_x, prev_y = x, y

    # push towards the target (world directions)
    cmd_x = K_POS * (TARGET[0] - x) - K_VEL * vx
    cmd_y = K_POS * (TARGET[1] - y) - K_VEL * vy
    # turn that into the drone's own forward and left directions
    forward = math.cos(yaw) * cmd_x + math.sin(yaw) * cmd_y
    left = -math.sin(yaw) * cmd_x + math.cos(yaw) * cmd_y
    pitch_disturbance = -clamp(forward, -MAX_TILT_CMD, MAX_TILT_CMD)
    roll_disturbance = clamp(left, -MAX_TILT_CMD, MAX_TILT_CMD)

    roll_input = K_ROLL_P * clamp(roll, -1.0, 1.0) + roll_velocity + roll_disturbance
    pitch_input = K_PITCH_P * clamp(pitch, -1.0, 1.0) + pitch_velocity + pitch_disturbance
    diff = clamp(TARGET[2] - altitude + K_VERTICAL_OFFSET, -1.0, 1.0)
    vertical_input = K_VERTICAL_P * diff ** 3

    front_left.setVelocity(K_VERTICAL_THRUST + vertical_input + pitch_input - roll_input)
    front_right.setVelocity(-(K_VERTICAL_THRUST + vertical_input + pitch_input + roll_input))
    rear_left.setVelocity(-(K_VERTICAL_THRUST + vertical_input - pitch_input - roll_input))
    rear_right.setVelocity(K_VERTICAL_THRUST + vertical_input - pitch_input + roll_input)

    if robot.getTime() - last_print >= 2.0:
        last_print = robot.getTime()
        print("t=%.0fs  x=%.1f  y=%.1f  z=%.1f" % (last_print, x, y, altitude))