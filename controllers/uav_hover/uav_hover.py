"""Take off and hover at a fixed height (Mavic 2 Pro)."""
from controller import Robot

TARGET_ALTITUDE = 3.0   # metres

K_VERTICAL_THRUST = 68.5   # propeller speed that roughly cancels gravity
K_VERTICAL_OFFSET = 0.6
K_VERTICAL_P = 3.0
K_ROLL_P = 50.0
K_PITCH_P = 30.0


def clamp(value, low, high):
    return max(low, min(value, high))


robot = Robot()
timestep = int(robot.getBasicTimeStep())

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

while robot.step(timestep) != -1:
    roll, pitch, _ = imu.getRollPitchYaw()
    altitude = gps.getValues()[2]
    roll_velocity, pitch_velocity, _ = gyro.getValues()

    roll_input = K_ROLL_P * clamp(roll, -1.0, 1.0) + roll_velocity
    pitch_input = K_PITCH_P * clamp(pitch, -1.0, 1.0) + pitch_velocity
    diff = clamp(TARGET_ALTITUDE - altitude + K_VERTICAL_OFFSET, -1.0, 1.0)
    vertical_input = K_VERTICAL_P * diff ** 3

    front_left.setVelocity(K_VERTICAL_THRUST + vertical_input + pitch_input - roll_input)
    front_right.setVelocity(-(K_VERTICAL_THRUST + vertical_input + pitch_input + roll_input))
    rear_left.setVelocity(-(K_VERTICAL_THRUST + vertical_input - pitch_input - roll_input))
    rear_right.setVelocity(K_VERTICAL_THRUST + vertical_input - pitch_input + roll_input)