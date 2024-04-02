from math import acos, sin, cos, radians


def distance(lat1, lon1, lat2, lon2):
    return acos(
            (sin(radians(lat1)) * sin(radians(lat2)))
            + (cos(radians(lat1)) * cos(radians(lat2)))
            * (cos(radians(lon2) - radians(lon1)))
        ) * 6_371_000
