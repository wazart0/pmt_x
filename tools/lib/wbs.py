import re

class WBS():

    @staticmethod
    # accepted formats, eg.: ['1.', '1', '1.1.', '1.1', ...]
    def check(string, separator = '.'):
        return bool(re.match('''\A([0-9]+\{0}?)+\Z'''.format(separator), string))


    @staticmethod
    def normalize(string, separator = '.'):
        if not WBS.check(string.strip(), separator): return None
        return string.strip()[:-1] if re.match('''\A([0-9]+\{0})+\Z'''.format(separator), string.strip()) else string.strip()


    @staticmethod
    def parent(string, separator = '.'):
        if WBS.normalize(string, separator) is None:
            return None
        return separator.join(WBS.normalize(string, separator).split(separator)[:-1])


def wbsprt(method):
    for i in ['1', '1.', '1.2', '1.2.', '1.2.3', '1.2.3.', '1.x', '1.2,', ' 1.2  ', ' 1.2.  ', '  1  ']:
        print('"' + i + '"', '    "' + str(method(i)) + '"')


### EXAMPLE ###

if __name__ == "__main__":
    wbsprt(WBS.parent)