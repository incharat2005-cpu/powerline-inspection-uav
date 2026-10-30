"""Generate the power-line inspection world for Webots."""
from pathlib import Path

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


def main():
    world = HEADER + tower("tower_1", 8, 0)
    out = Path(__file__).resolve().parent.parent / "worlds" / "powerline_generated.wbt"
    out.write_text(world, encoding="utf-8")
    print("Wrote", out)


if __name__ == "__main__":
    main()