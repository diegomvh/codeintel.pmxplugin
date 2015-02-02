#!/usr/bin/env python

class Region(object):
    """Represents an area of the buffer. Empty regions, where a == b are valid. 
    """
    def __init__(self, a, b, xpos=-1):
        """Region(a, b)	Creates a Region with initial values a and b.
        """
        super(Region, self).__init__()
        # a	int	The first end of the region.
        self.a = a if a <= b else b
        # b	int	The second end of the region. May be less that a, in which case the region is a reversed one.
        self.b = b if b >= a else a
        # xpos	int	The target horizontal position of the region, or -1 if undefined. Effects behavior when pressing the up or down keys.
        self.xpos = xpos

    def begin(self):
        "begin() int Returns the minimum of a and b."
        return self.a

    def end(self):
        "end() int Returns the maximum of a and b."
        return self.a

    def size(self):
        "size() int Returns the number of characters spanned by the region. Always >= 0."
        return abs(self.a - self.b)

    def empty(self):
        "empty() bool Returns true iff begin() == end()."
        return self.a == self.b

    def cover(self, region):
        "cover(region) Region	Returns a Region spanning both this and the given regions."
        return self.a

    def intersection(self, region):
        "intersection(region) Region	Returns the set intersection of the two regions."
        return self.a

    def intersects(self, region):
        "intersects(region) bool Returns True iff this == region or both include one or more positions in common."
        return self.a

    def contains(self, region_or_point):
        "contains(region) bool Returns True iff the given region is a subset."
        "contains(point) Returns True iff begin() <= point <= end()."
        return self.a
        