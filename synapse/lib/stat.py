import sys
import calendar
import collections

def nearest(n, nearest=1):
    return n - (n % nearest)

class Histogram(collections.OrderedDict):
    def __init__(self, data, bins=None, width=1, minval=None, maxval=None):
        self._data = data

        if bins is None:
            # Calculate range of values
            self._values = list(map(self._getValueForItem, self._data))

            # Set width of each bin
            self._width = width

            if minval is None:
                # minval is the lowest value rounded down to the prev width multiple
                minval = nearest(min(self._values), self._width)

            if maxval is None:
                # maxval is the highest value rounded up to the next width multiple
                maxval = nearest(max(self._values), self._width) + self._width

            # create dictionary keys
            super(Histogram, self).__init__(
                (binid, []) for binid in range(minval, maxval, self._width)
            )
        else:
            # width is the difference between bin ids
            self._width = bins[1] - bins[0]

            # minval is the lowest bin id
            minval = bins[0]

            # maxval is the highest bin id
            maxval = bins[-1]

            # create dictionary keys
            super(Histogram, self).__init__(
                (binid, []) for binid in bins
            )

        for item in data:
            # Get the value of this item
            value = self._getValueForItem(item)

            # Range check to make sure we care about it
            if value < minval or value > maxval:
                continue

            # Figure out the bin id
            binid = self._computeBinForValue(value)

            # Set the value in the bin
            self._setValueInBin(binid, value)

    def _getValueForItem(self, item):
        '''
        Data aware method to get value from item
        '''
        return item

    def _computeBinForValue(self, value):
        '''
        Data aware method to get the bin id for a value
        '''
        return nearest(value, self._width)

    def _setValueInBin(self, binid, value):
        '''
        Data aware method to set the value in the bin
        '''
        self[binid].append(value)

class BinaryHistogram(Histogram):
    def __init__(self, data):
        super(BinaryHistogram, self).__init__(data, bins=[0,1])

    def _computeBinForValue(self, value):
        return value & 1

class SynapseHistogram(Histogram):
    def __init__(self, data):
        self._data = data

    def _getValueForItem(self, item):
        # item = (basetime, [things...])
        return item[0]

    def _setValueInBin(self, binid, value):
        self[binid].extend(value)

class DayByHour(SynapseHistogram):
    '''
    bins: 24
    width: 1 hour

    24 bins, one for each hour of the day
    '''
    def __init__(self, data):
        super().__init__(data, bins=range(24))

    def _computeBinForValue(self, value):
        return time.gmtime(value/1000).tm_hour

class MonthByDay(SynapseHistogram):
    '''
    bins: 31
    width: 1 day

    31 bins, one for each day of the month
    '''
    def __init__(self, data):
        super().__init__(data, bins=range(31))

    def _computeBinForValue(self, value):
        return time.gmtime(value/1000).tm_mday

class WeekByDay(SynapseHistogram):
    '''
    bins: 7
    width: 1 day

    7 bins, one for each day of the week
    '''
    def __init__(self, data):
        super().__init__(data, bins=range(7))

    def _computeBinForValue(self, value):
        return time.gmtime(value/1000).tm_wday

class YearByMonth(SynapseHistogram):
    '''
    bins: 12
    width: 1 month

    12 bins, one for each month of the year
    '''
    def __init__(self, data):
        super().__init__(data, bins=range(12))

    def _computeBinForValue(self, value):
        return time.gmtime(value/1000).tm_mon

class YearByDay(SynapseHistogram):
    '''
    bins: 366
    width: 1 year

    366 bins, one for each month of the year
    '''
    def __init__(self, data, year):
        super().__init__(data, bins=range(366))

    def _computeBinForValue(self, value):
        timestruc = time.gmtime(value/1000)
        yday = timestruc.tm_yday

        if yday > 59 and not calendar.isleap(timestruc.tm_year):
            yday += 1

        return yday

class Linear(SynapseHistogram):
    '''
    bins: n
    width: 1 year

    n bins, one for each year
    '''
    pass

def main(argv):

    try:
        h0 = Histogram(bytes(range(256))*10)
        h1 = Histogram(bytes(range(256))*10, minval=20)
        h2 = Histogram(bytes(range(256))*10, width=10)
        h3 = Histogram(bytes(range(256))*10, bins=range(20,30))
        bh = BinaryHistogram(bytes(range(256)))
    except:
        import traceback
        traceback.print_exc()

    import code
    lookup = globals()
    lookup.update(locals())
    code.interact(local=lookup)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
