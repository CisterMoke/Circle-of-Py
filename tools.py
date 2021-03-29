from math import pi, cos, sin, radians, degrees
from enum import Enum
import numpy as np


class Line:
    # ax + by + c = 0
    def __init__(self, v1, v2):
        self.a = v2[1] - v1[1]
        self.b = v1[0] - v2[0]
        self.c = np.cross(v2, v1)

    def __call__(self, p):
        return self.a*p[0] + self.b*p[1] + self.c

    def intersection(self, other):
        # See e.g.     https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Using_homogeneous_coordinates
        if not isinstance(other, Line):
            return NotImplemented
        w = self.a*other.b - self.b*other.a
        return np.array(((self.b*other.c - self.c*other.b)/w, (self.c*other.a - self.a*other.c)/w))


def rectangle_vertices(cx, cy, w, h, r):
    angle = radians(r)
    dx = w/2
    dy = h/2
    rot = np.array(((cos(angle), sin(angle)), (-sin(angle), cos(angle))))
    return (
        (cx, cy) + np.array((-dx, -dy)).dot(rot),
        (cx, cy) + np.array((dx, -dy)).dot(rot),
        (cx, cy) + np.array((dx, dy)).dot(rot),
        (cx, cy) + np.array((-dx, dy)).dot(rot)
    )


def intersection_area(r1, r2):
    # r1 and r2 are in (center_x, center_y, width, height, rotation) representation
    # First convert these into a sequence of vertices

    rect1 = rectangle_vertices(*r1)
    rect2 = rectangle_vertices(*r2)

    # Use the vertices of the first rectangle as
    # starting vertices of the intersection polygon.
    intersection = rect1

    # Loop over the edges of the second rectangle
    for p, q in zip(rect2, rect2[1:] + rect2[:1]):
        if len(intersection) == 0:
            break  # No intersection

        line = Line(p, q)

        # Any point p with line(p) <= 0 is on the "inside" (or on the boundary),
        # any point p with line(p) > 0 is on the "outside".

        # Loop over the edges of the intersection polygon,
        # and determine which part is inside and which is outside.
        new_intersection = []
        line_values = [line(t) for t in intersection]
        for s, t, s_value, t_value in zip(
                intersection, intersection[1:] + intersection[:1],
                line_values, line_values[1:] + line_values[:1]):
            if s_value <= 0:
                new_intersection.append(s)
            if s_value * t_value < 0:
                # Points are on opposite sides.
                # Add the intersection of the lines to new_intersection.
                intersection_point = line.intersection(Line(s, t))
                new_intersection.append(intersection_point)

        intersection = new_intersection
    contact_points = [v for v in intersection]
    area = 0
    # Calculate area
    if len(intersection) > 2:
        area = 0.5 * sum(np.cross(p, q) for p, q in
                         zip(intersection, intersection[1:] + intersection[:1]))
    return area, contact_points


def circle_points(num, radius, origin=(0, 0)):
    points = []
    alpha = 0
    beta = 2 * pi / num
    while 2 * pi - alpha > 0.01:
        p = (origin[0] + radius*cos(alpha), origin[1] + radius*sin(alpha), - degrees(alpha))
        points.append(p)
        alpha += beta
    return points


class CardState(Enum):
    REST = 1
    GRABBED = 2
    RELEASED = 3
    MOVING = 4
    MOVED = 5
    FINAL = 6
