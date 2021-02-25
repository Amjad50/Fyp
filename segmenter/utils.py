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


def is_another_in_between(box1, box2, boxes):

    box1_center = box_center(box1)
    box2_center = box_center(box2)

    line_between_two_boxes = (box1_center, box2_center)

    for box in boxes:
        # ignore if its the same box
        if box == box1 or box == box2:
            continue

        left, top, right, down = box

        lines = [((0, 0), (0, 0))] * 4
        lines[0] = ((left, down), (left, top))
        lines[1] = ((left, top), (right, top))
        lines[2] = ((right, top), (right, down))
        lines[3] = ((right, down), (left, down))

        # we check if an edge (bounding-rect) of any symbol intersects with the
        # line between the two symbols we are interested in
        for line in lines:
            if get_line_intersection(line, line_between_two_boxes):
                return True

    return False
