import re

class WBS():

    @staticmethod
    # accepted formats, eg.: ['1.', '1', '1.1. ', ' 1.1', ...]
    def check(string, separator = '.'):
        return bool(re.match('''\A([0-9]+\{0}?)+\Z'''.format(separator), string.strip()))


    @staticmethod
    # accepted formats, eg.: ['1.', '1', '1.1. ', ' 1.1', ...]
    def normalize(wbs, separator = '.'):
        tmp = wbs.strip().split(separator)
        return [int(i) for i in (tmp[:-1] if tmp[-1] == '' else tmp)]


    @staticmethod
    def to_str(wbs_normalized, separator = '.'):
        return separator.join([str(i) for i in wbs_normalized])


    @staticmethod
    def parent(wbs_normalized):
        return wbs_normalized[:-1]


    @staticmethod
    def level(wbs_normalized):
        return len(wbs_normalized)


    @staticmethod
    def lowest_level_number(wbs_normalized):
        return wbs_normalized[-1]


    @staticmethod
    def expand_wbs_range(wbs_start_normalized, wbs_finish_normalized):
        if WBS.parent(wbs_start_normalized) != WBS.parent(wbs_finish_normalized) or WBS.lowest_level_number(wbs_start_normalized) > WBS.lowest_level_number(wbs_finish_normalized):
            return []
        return [WBS.parent(wbs_start_normalized) + [i] for i in list(range(WBS.lowest_level_number(wbs_start_normalized), 1 + WBS.lowest_level_number(wbs_finish_normalized)))]





def wbsprt(method):
    for i in ['1', '1.', '1.2', '1.2.', '1.2.3', '1.2.3.', '1.x', '1.2,', ' 1.2  ', ' 1.2.  ', '  1  ']:
        if WBS.check(i):
            print('"' + i + '"', '    "' + str(WBS.to_str((WBS.normalize(i)))) + '"')
        else:
            print('"' + i + '"', '    is not a WBS')


def expand_check():
    lst = [['1.', '3'],
        ['1.', '1.'],
        ['1.2', '1.4'],
        ['1.2', '1.2'],
        ['1.4.5', '1.4.11'],
        ['1.2.3', '1.3.9'],
        ['1.1', '1'],
        ['1', '1.3'],
        ['1.1.5', '1.1.2']]

    for i in lst:
        if WBS.check(i[0]) and WBS.check(i[1]):
            print('"' + str(i) + '"     "' + str(expand_wbs_range(WBS.normalize(i[0]), WBS.normalize(i[1]))) + '"')
        else:
            print('"' + str(i) + '"    is not a WBS')


### EXAMPLE ###

if __name__ == "__main__":
    wbsprt(WBS.parent)
