# adapted from: https://github.com/gianlucoDev/braccino

from collections import namedtuple
from math import *


Position = namedtuple('Position', field_names=('x', 'y', 'z'))
IkAngles = namedtuple('IkAngles',
                      field_names=('base', 'shoulder', 'elbow', 'wrist_ver'))

class Link:
    def __init__(self, length, angle_min, angle_max):
        self.length = length
        self.angle_min = angle_min
        self.angle_max = angle_max

    def in_range(self, angle):
        return self.angle_min <= angle <= self.angle_max


BASE = Link(
    0,  # this actually indicates the heigth of the base
    radians(0),
    radians(180))

UPPERARM = Link(
    125,
    radians(15),
    radians(165))

FOREARM = Link(
    125,
    radians(0),
    radians(180))

HAND = Link(
    195,
    radians(0),
    radians(180))


def invert_angle(angle):
    # invert the angle but keeping it in the 0 - 2pi range
    return (angle + pi) % (2 * pi)


def find_base_angle(pos):
    # convert from cartesian coordinates to polar coordinates
    r = sqrt(pos.x ** 2 + pos.y ** 2)
    phi = atan2(pos.y, pos.x)

    # if the angle is reachable, return polar coordinates
    if BASE.in_range(phi):
        return False, r, phi

    # If the angles is not reachable, try inverting it.
    # If we invert the angle then we should also invert the length, this way the
    # polar coordinates will indicate the same point: (r, phi) = (-r, -phi)
    inverted_phi = invert_angle(phi)
    if BASE.in_range(inverted_phi):
        return True, -r, inverted_phi

    # the angle is not reachable
    return None


def cos_rule(opposite, adjacent1, adjacent2):
    delta = 2 * adjacent1 * adjacent2
    if delta == 0:
        return None

    calculated_cos = (adjacent1 ** 2 + adjacent2 ** 2 - opposite ** 2) / delta
    if calculated_cos > 1 or calculated_cos < -1:
        return None

    angle = acos(calculated_cos)
    return angle


def solve_triangle(a, b, c):
    alpha = cos_rule(a, b, c)
    beta = cos_rule(b, c, a)
    gamma = cos_rule(c, a, b)

    if alpha is None or beta is None or gamma is None:
        return None
    else:
        return alpha, beta, gamma


def find_arm_angles(x, y, attack_angle):
    c_x = x - HAND.length * cos(attack_angle)
    c_y = y - HAND.length * sin(attack_angle)

    c_length = sqrt(c_x ** 2 + c_y ** 2)
    phi = atan2(c_y, c_x)

    solution = solve_triangle(UPPERARM.length, FOREARM.length, c_length)
    if solution is None:
        return None

    # alpha -> (opposite to UPPERARM)
    # beta -> shoulder (opposite to FOREARM)
    # gamma -> elbow (opposite to c side)
    _alpha, beta, gamma = solution

    shoulder_angle = phi + beta
    elbow_angle = gamma - pi / 2
    wrist_ver_angle = invert_angle(attack_angle - shoulder_angle - elbow_angle)

    if UPPERARM.in_range(shoulder_angle) \
            and FOREARM.in_range(elbow_angle) \
            and HAND.in_range(wrist_ver_angle):
        return shoulder_angle, elbow_angle, wrist_ver_angle

    shoulder_angle = phi - beta
    elbow_angle = pi - (gamma - pi / 2)
    wrist_ver_angle = invert_angle(attack_angle - shoulder_angle - elbow_angle)

    if UPPERARM.in_range(shoulder_angle) \
            and FOREARM.in_range(elbow_angle) \
            and HAND.in_range(wrist_ver_angle):
        return shoulder_angle, elbow_angle, wrist_ver_angle

    return None


def find_arm_angles_without_attack_angle(x, y):
    # just try every possible angle, one will probably work
    for a in range(0, 360):
        a = radians(a)
        solution = find_arm_angles(x, y, a)

        if solution is not None:
            return solution

    return None


def calculate_ik(pos, attack_angle = None):
    result = find_base_angle(pos)
    if result is None:
        return None

    inverted, r, base_angle = result
    if inverted and attack_angle is not None:
        attack_angle = pi - attack_angle

    if attack_angle is not None:
        found_angles = find_arm_angles(
            r, pos.z - BASE.length, attack_angle)
    else:
        found_angles = find_arm_angles_without_attack_angle(
            r, pos.z - BASE.length)

    if found_angles is None:
        return None

    shoulder_angle, elbow_angle, wrist_ver_angle = found_angles
    return base_angle, shoulder_angle, elbow_angle, wrist_ver_angle


def braccio_ik(pos, attack_angle = None):
    # convert to radians
    a = None if attack_angle is None else radians(attack_angle)

    # do calculations
    solution = calculate_ik(pos, attack_angle=a)
    if solution is None:
        return None

    # convert back to degrees
    base, shoulder, elbow, wrist_ver = solution
    return IkAngles(
        base=int(degrees(base)),
        shoulder=int(degrees(shoulder)),
        elbow=int(degrees(elbow)),
        wrist_ver=int(degrees(wrist_ver))
    )
