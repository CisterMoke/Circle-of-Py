import numpy as np
from math import copysign, pi
from tools import CardState


MU_VEL = 0.1
MU_OMEGA = 0.05
MU_STAT = 1.5
MU_DYN = 0.2
MIN_OMEGA = 0.1


def split_force(force, inertia, contact, origin=(0, 0)):
    f = np.array(force)
    r = np.array(contact) - origin
    torque = np.cross(f, r) / inertia
    n, mag = _normalize(r)
    trans = n.dot(f)

    return tuple(n * trans), float(torque)


def get_rotational_velocity(omega, point, origin=(0, 0)):
    r = np.array(point) - origin
    r = np.append(r, [0], 0)
    w = np.array([0, 0, omega * pi / 180])
    return tuple(np.cross(w, r)[0:2])


def get_fric_force(delta_v, f_norm, mu_stat=MU_STAT, mu_dyn=MU_DYN):
    v = np.array(delta_v)
    dir_v, mag_v = _normalize(v)
    if mag_v < mu_stat:
        return tuple(v * f_norm)
    else:
        f_dyn = max(mag_v * mu_dyn * f_norm, 0.5)
        return tuple(dir_v * f_dyn)


def get_rot_fric_force(omega, mu_rot):
    f_rot = max(abs(omega*mu_rot), 0.2)
    return copysign(f_rot, omega)


def get_delta_v(point, center1, vel1, omega1, center2, vel2, omega2):
    """ Return the delta_v from the POV of object 1 """
    v1 = np.array(vel1)
    v2 = np.array(vel2)
    rot1 = get_rotational_velocity(omega1, point, center1)
    rot2 = get_rotational_velocity(omega2, point, center2)
    return tuple(v2 + rot2 - v1 - rot1)


def bigger_norm(v1, v2):
    return np.linalg.norm(v1) > np.linalg.norm(v2)


def add(vects):
    return tuple(np.sum(vects, 0))


def mul(v, s):
    return tuple(np.array(v) * s)


def _normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v, 0
    return v / norm, norm


def normalize(v):
    a = np.array(v)
    a, n = _normalize(a)
    return tuple(a)


def interact(card1: dict, card2: dict):
    res1, res2 = {"hash": card1["hash"], "forces": []}, {"hash": card2["hash"], "forces": []}
    if card2["hash"] == card1["hash"]:
        return res1, res2, [], []
    area, contacts = card1["hitbox"].overlap(card2["hitbox"], alpha=card1["angle"], beta=card2["angle"])
    if area == 0:
        return res1, res2, [], []
    f_norm = area / (card1["area"] * len(contacts))
    args = [card1["center"], card1["velocity"], -card1["omega"],
            card2["center"], card2["velocity"], -card2["omega"]]
    delta_vs = [get_delta_v(p, *args) for p in contacts]
    fric_forces = [get_fric_force(dv, f_norm) for dv in delta_vs]
    for force, contact in zip(fric_forces, contacts):
        if not card1["state"] == CardState.GRABBED:
            res1["forces"].append(split_force(force, card1["inertia"], contact, card1["center"]))
        if not card2["state"] == CardState.GRABBED:
            res2["forces"].append(split_force(mul(force, -1), card2["inertia"], contact, card2["center"]))
    return res1, res2, contacts, fric_forces
