# got this from 
# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/1968345#1968345
def get_line_intersection(line1, line2):
    """
    Finds an intersection point between two lines, each line in the form
    [(x1, y1), (x2, y2)]. If no intersection is found, `None` is returned
    """
    p0, p1 = line1
    p2, p3 = line2

    p0_x, p0_y = p0
    p1_x, p1_y = p1
    p2_x, p2_y = p2
    p3_x, p3_y = p3

    s1_x = p1_x - p0_x
    s1_y = p1_y - p0_y
    s2_x = p3_x - p2_x
    s2_y = p3_y - p2_y

    s_bottom = -s2_x * s1_y + s1_x * s2_y
    t_bottom = -s2_x * s1_y + s1_x * s2_y

    # parallel I think, TODO: check
    if s_bottom == 0 or t_bottom == 0:
        return None

    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / s_bottom
    t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / t_bottom

    if 0 <= s <= 1 and 0 <= t <= 1:
        i_x = p0_x + (t * s1_x)
        i_y = p0_y + (t * s1_y)
        return i_x, i_y

    return None
