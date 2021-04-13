from utils.geometry import get_line_intersection


def box_size(box):
    left, top, right, down = box

    return right - left, down - top


def box_center(box):
    l, t, r, d = box

    return l + (abs(r - l) / 2), t + (abs(d - t) / 2)


def merge_boxes(box1, box2):
    l1, t1, r1, d1 = box1
    l2, t2, r2, d2 = box2

    left = min(l1, l2)
    top = min(t1, t2)
    right = max(r1, r2)
    down = max(d1, d2)

    return left, top, right, down


def get_border_lines(box):
    left, top, right, down = box

    lines = [((0, 0), (0, 0))] * 4
    lines[0] = ((left, down), (left, top))
    lines[1] = ((left, top), (right, top))
    lines[2] = ((right, top), (right, down))
    lines[3] = ((right, down), (left, down))

    return lines


def is_another_in_between(box1, box2, boxes):
    box1_center = box_center(box1)
    box2_center = box_center(box2)

    line_between_two_boxes = (box1_center, box2_center)

    for box in boxes:
        # ignore if its the same box
        if box == box1 or box == box2:
            continue

        # if its covered, then ignore this
        if is_center_inside(box1, box) or is_center_inside(box2, box) >= 0.7:
            continue

        lines = get_border_lines(box)

        # we check if an edge (bounding-rect) of any symbol intersects with the
        # line between the two symbols we are interested in
        for line in lines:
            if get_line_intersection(line, line_between_two_boxes):
                return True

    return False


def box_overlap_percentage(box1, box2) -> float:
    l1, t1, r1, d1 = box1
    l2, t2, r2, d2 = box2

    w2, h2 = box_size(box2)

    overlap_area = max(0, min(r1, r2) - max(l1, l2)) * max(0, min(d1, d2) - max(t1, t2))
    area2 = w2 * h2

    return overlap_area / area2


def is_center_inside(box, box_to_be_inside_of) -> bool:
    # must be overlapped
    if box_overlap_percentage(box_to_be_inside_of, box) == 0:
        return False

    lines = get_border_lines(box_to_be_inside_of)
    l1, t1, r1, d1 = box
    l2, t2, r2, d2 = box_to_be_inside_of

    l = min(l1, l2)
    t = min(t1, t2)
    r = max(r1, r2)
    d = max(d1, d2)

    c_x, c_y = box_center(box)

    top_bottom_line = ((c_x, t - 1), (c_x, d + 1))
    left_right_line = ((l - 1, c_y), (r + 1, c_y))

    box_from_center_lines = [left_right_line, top_bottom_line] * 2

    # make sure it intersects with all directions
    return all(map(lambda x: get_line_intersection(x[0], x[1]), zip(lines, box_from_center_lines)))
