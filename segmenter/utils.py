def box_size(box):
    left, top, right, down = box

    return right - left, down - top


def merge_boxes(box1, box2):
    l1, t1, r1, d1 = box1
    l2, t2, r2, d2 = box2

    left = min(l1, l2)
    top = min(t1, t2)
    right = max(r1, r2)
    down = max(d1, d2)

    return left, top, right, down


def is_another_in_between(box1, box2, boxes):
    l1, t1, r1, d1 = box1
    l2, t2, r2, d2 = box2

    # box1 is the one on top of box2, if its not the case, then flip them
    # TODO: this will not work if they are colliding or not in `top-down` position
    if t1 > t2:
        tmp = box1
        box1 = box2
        box2 = tmp

        l1, t1, r1, d1 = box1
        l2, t2, r2, d2 = box2

    for box in boxes:
        # ignore if its the same box
        if box == box1 or box == box2:
            continue

        left, top, right, down = box

        if d1 <= top <= t2:
            if (left < r1 and right > l1) or (left < r2 and right > l2):
                return True

    return False
