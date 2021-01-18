from tools import intersection_area, rectangle_vertices


class Hitbox:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    @property
    def center_x(self):
        return (self.x_max + self.x_min) / 2

    @property
    def center_y(self):
        return (self.y_max + self.y_min) / 2

    @property
    def center(self):
        return self.center_x, self.center_y

    @property
    def width(self):
        return self.x_max - self.x_min

    @property
    def height(self):
        return self.y_max - self.y_min

    @property
    def area(self):
        return self.width * self.height

    def translate(self, disp):
        self.x_min += disp[0]
        self.x_max += disp[0]
        self.y_min += disp[1]
        self.y_max += disp[1]

    def get_rotated(self, theta):
        verts = rectangle_vertices(self.center_x, self.center_y, self.width, self.height, - theta)
        return [v.tuple() for v in verts]

    def overlap(self, h: "Hitbox", alpha=0, beta=0):
        r1 = (self.center_x, self.center_y, self.width, self.height, - alpha)
        r2 = (h.center_x, h.center_y, h.width, h.height, - beta)
        return intersection_area(r1, r2)
