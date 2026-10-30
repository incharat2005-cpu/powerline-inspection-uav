"""Generate the power-line inspection world for Webots."""
from pathlib import Path
import math

HEADER = '''#VRML_SIM R2025a utf8

EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/floors/protos/Floor.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/appearances/protos/SandyGround.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/robots/dji/mavic/protos/Mavic2Pro.proto"

WorldInfo {
  title "Power line inspection"
  basicTimeStep 8
  defaultDamping Damping {
    linear 0.5
    angular 0.5
  }
}
Viewpoint {
  orientation 0.4875149969923638 -0.20520616026956953 0.8486575042353394 2.4875935185208675
  position 2.0242549269910293 -2.096088154411385 -4.153445586738199
  near 0.2
  follow "Mavic 2 PRO"
  followSmoothness 0.2
}
TexturedBackground {
  luminosity 3
}
TexturedBackgroundLight {
}
Floor {
  size 400 400
  tileSize 6 6
  appearance SandyGround {
  }
}
Mavic2Pro {
  translation 0 0 0.1
  rotation 0 0 1 3.141590777218456
  cameraSlot [
    Camera {
      width 400
      height 240
      near 0.2
    }
  ]
}
'''


def box(sx, sy, sz, x, y, z):
    """One grey box of size (sx, sy, sz) centred at (x, y, z)."""
    return """    Pose {
      translation %.2f %.2f %.2f
      children [
        Shape {
          appearance PBRAppearance {
            baseColor 0.55 0.55 0.6
            roughness 1
            metalness 0
          }
          geometry Box {
            size %.2f %.2f %.2f
          }
        }
      ]
    }
""" % (x, y, z, sx, sy, sz)


def tower(name, x, y, height=20.0, arm=6.0):
    """A simple tower: one tall post and one crossarm near the top."""
    post = box(0.8, 0.8, height, 0, 0, height / 2)
    crossarm = box(0.4, arm, 0.4, 0, 0, height - 1)
    return 'Solid {\n  translation %.2f %.2f 0\n  name "%s"\n  children [\n%s%s  ]\n}\n' % (
        x, y, name, post, crossarm)


NUM_TOWERS = 5      # how many towers in the line
SPAN = 40.0         # metres between towers
FIRST_X = 10.0      # where the first tower stands
SAG = 2.0           # how far each wire hangs down in the middle (metres)
ARM_UNDER = 18.8    # underside of the crossarm
POST_TOP = 20.0     # top of the tower post
INS_LEN = 1.5       # length of each insulator string (metres)
INS_DISCS = 8       # number of discs in each string
# (sideways position, direction): -1 = hangs down, +1 = stands up
PHASES = [(-3.0, -1), (0.0, 1), (3.0, -1)]


def cylinder(x, y, z, height, radius, color):
    """One upright cylinder centred at (x, y, z)."""
    return """    Pose {
      translation %.3f %.3f %.3f
      children [
        Shape {
          appearance PBRAppearance {
            baseColor %s
            roughness 0.6
            metalness 0
          }
          geometry Cylinder {
            height %.3f
            radius %.3f
          }
        }
      ]
    }
""" % (x, y, z, color, height, radius)


def insulator(name, x, y, z0, direction):
    """A string of ceramic discs starting at z0, hanging down (-1) or standing up (+1)."""
    parts = cylinder(x, y, z0 + direction * INS_LEN / 2, INS_LEN, 0.05, "0.35 0.25 0.15")
    for k in range(INS_DISCS):
        z = z0 + direction * INS_LEN * (k + 0.5) / INS_DISCS
        parts += cylinder(x, y, z, 0.06, 0.22, "0.8 0.7 0.5")
    return 'Solid {\n  name "%s"\n  children [\n%s  ]\n}\n' % (name, parts)


def wire(name, x1, x2, y, z, sag=SAG, segments=12):
    """One sagging wire from x1 to x2, made of short straight pieces."""
    pieces = ""
    for k in range(segments):
        t1 = k / segments
        t2 = (k + 1) / segments
        xa = x1 + (x2 - x1) * t1
        xb = x1 + (x2 - x1) * t2
        za = z - 4 * sag * t1 * (1 - t1)
        zb = z - 4 * sag * t2 * (1 - t2)
        length = math.hypot(xb - xa, zb - za)
        angle = -math.atan2(zb - za, xb - xa)
        pieces += """    Pose {
      translation %.3f %.3f %.3f
      rotation 0 1 0 %.4f
      children [
        Shape {
          appearance PBRAppearance {
            baseColor 0.1 0.1 0.1
            roughness 1
            metalness 0
          }
          geometry Box {
            size %.3f 0.08 0.08
          }
        }
      ]
    }
""" % ((xa + xb) / 2, y, (za + zb) / 2, angle, length)
    return 'Solid {\n  name "%s"\n  children [\n%s  ]\n}\n' % (name, pieces)


def main():
    world = HEADER
    for i in range(NUM_TOWERS):
        tx = FIRST_X + i * SPAN
        world += tower("tower_%d" % (i + 1), tx, 0)
        for j, (y, d) in enumerate(PHASES):
            z0 = POST_TOP if d > 0 else ARM_UNDER
            world += insulator("insulator_t%d_p%d" % (i + 1, j + 1), tx, y, z0, d)
    for i in range(NUM_TOWERS - 1):
        for j, (y, d) in enumerate(PHASES):
            z0 = POST_TOP if d > 0 else ARM_UNDER
            wire_z = z0 + d * INS_LEN
            name = "wire_span%d_phase%d" % (i + 1, j + 1)
            world += wire(name, FIRST_X + i * SPAN, FIRST_X + (i + 1) * SPAN, y, wire_z)
    out = Path(__file__).resolve().parent.parent / "worlds" / "powerline_generated.wbt"
    out.write_text(world, encoding="utf-8")
    print("Wrote", out)


if __name__ == "__main__":
    main()