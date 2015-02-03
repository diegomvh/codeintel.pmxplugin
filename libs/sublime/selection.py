#!/usr/bin/env python

from bisect import bisect
import functools

class Selection(object):
    __slots__ = ('_regions', )
    """Maintains a set of Regions, ensuring that none overlap. The regions are kept in sorted order. 
    """
    def __init__(self):
        super(Selection, self).__init__()
        self._regions = []

    # ------------- Magics
    def __str__(self):
        return "<%s>" % ",".join(map(str, self._regions))
        
    def __getitem__(self, index):
        return self._regions[index]

    def clear(self):
        """clear()	None	Removes all regions.
        """
        self._regions = []

    def _add(self, regions, region):
        if regions:
            while regions and regions[-1].intersects(region):
                r = regions.pop()
                region = r.cover(region)
        regions.append(region)
        return regions
        
    def add(self, region):
        """add(region)	None	Adds the given region. It will be merged with any intersecting regions already contained within the set.
        """
        index = bisect(self._regions, region)
        self._regions.insert(index, region)
        self._regions = functools.reduce(self._add, self._regions, [])
        
    def add_all(self, region_set):
        """add_all(region_set)	None	Adds all regions in the given set.
        """
        for region in region_set:
            index = bisect(self._regions, region)
            self._regions.insert(index, region)
        self._regions = functools.reduce(self._add, self._regions, [])

    def _subtract(self, regions, region):
        if regions:
            while regions and regions[-1].intersects(region):
                r = regions.pop()
                region = r.cover(region)
        regions.append(region)
        return regions
        
    def subtract(self, region):
        """subtract(region)	None	Subtracts the region from all regions in the set.
        """
        # TODO Terminar
        index = bisect(self._regions, region)
        self._regions.insert(index, region)
        self._regions = functools.reduce(self._subtract, self._regions, [])
        
    def contains(self, region):
        """contains(region)	bool	Returns true iff the given region is a subset.
        """
        return any(lambda r: r.contains(region), self._regions)

if __name__ == '__main__':
    s = Selection()
    s.add(region.Region(1,10))
    s.add(region.Region(10,110))
    s.add(region.Region(11,100))
    s.add(region.Region(300,101))
    
    print(s)