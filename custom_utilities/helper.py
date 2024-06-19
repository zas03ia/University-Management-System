from datetime import time

def time_overlap(start1, end1, start2, end2):
    if start1==None or start2==None:
        return False
    return max(start1, start2) < min(end1, end2)
