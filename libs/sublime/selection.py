#!/usr/bin/env python

class Selection(object):
    """Maintains a set of Regions, ensuring that none overlap. The regions are kept in sorted order. 
    """
    def __init__(self):
        super(Selection, self).__init__()
        self.regions = []

    def clear(self):
        """clear()	None	Removes all regions.
        """
        pass

    def add(self, region):
        """add(region)	None	Adds the given region. It will be merged with any intersecting regions already contained within the set.
        """
        pass

    def add_all(self, region_set):
        """add_all(region_set)	None	Adds all regions in the given set.
        """
        pass

    def subtract(self, region):
        """subtract(region)	None	Subtracts the region from all regions in the set.
        """
        pass

    def contains(self, region):
        """contains(region)	bool	Returns true iff the given region is a subset.
        """
        pass
