#!/usr/bin/env python

from collections import namedtuple

class Region(namedtuple('Region', 'a b xpos')):
    """Represents an area of the buffer. Empty regions, where a == b are valid. 
    """
    __slots__ = ()
    def __new__(cls, a, b, xpos=-1):
        return super(Region, cls).__new__(cls, a, b, xpos)
        
    def __nonzero__(self):
        return not self.empty()
    __bool__ = __nonzero__
    
    def begin(self):
        "begin() int Returns the minimum of a and b."
        return min(self.a, self.b)

    def end(self):
        "end() int Returns the maximum of a and b."
        return max(self.a, self.b)

    def size(self):
        "size() int Returns the number of characters spanned by the region. Always >= 0."
        return abs(self.b - self.a)

    def empty(self):
        "empty() bool Returns true iff begin() == end()."
        return self.a == self.b

    def cover(self, region):
        "cover(region) Region	Returns a Region spanning both this and the given regions."
        a = region.begin() if region.begin() <= self.begin() else self.begin()
        b = region.end() if region.end() >= self.end() else self.end()
        return Region(a, b)

    def intersection(self, region):
        "intersection(region) Region	Returns the set intersection of the two regions."
        a = b = 0
        if self.begin() <= region.begin() <= self.end():
            a = region.begin()
        elif region.a <= self.begin() <= region.end():
            a = self.begin()
        if self.begin() <= region.end() <= self.end():
            b = region.end()
        elif region.begin() <= self.end() <= region.end():
            b = self.end()
        return Region(a, b)

    def intersects(self, region):
        "intersects(region) bool Returns True iff this == region or both include one or more positions in common."
        return bool(self.intersection(region))

    def contains(self, region_or_point):
        "contains(region) bool Returns True iff the given region is a subset."
        "contains(point) Returns True iff begin() <= point <= end()."
        if isinstance(region_or_point, Region):
            return self.begin() <= region_or_point.begin() <= region_or_point.end() <= self.end()
        print(self.begin(), self.end())
        return self.begin() <= region_or_point <= self.end()
