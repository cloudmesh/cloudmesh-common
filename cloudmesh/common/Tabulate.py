import textwrap
from tabulate import tabulate
from pprint import pprint

class Printer:

    @staticmethod
    def select(results, order=None, width=None):
        if order is None:
            columns = len(results[0])
        else:
            columns = len(order)

        if type(width) == int:
            _width = [width] * columns
        elif type(width) == list:
            _width=width
        else:
            _width= [40] * columns

        if order is None or results is None:
            return results
        _results = []
        for result in results:
            if width is None:
                _results.append([result[key] for key in order])
            else:
                entry = []
                i = 0
                for key in order:
                    print (key, _width[i])
                    if _width[i]:
                        entry.append("\n".join(textwrap.wrap(str(result[key]), _width[i])))
                    else:
                        entry.append(result[key])
                    i = i + 1
                _results.append(entry)
        return _results



    @staticmethod
    def write(results, order=None, header=None, output='psql', width=None):
        if header:
            headers = header
        else:
            headers = order
        return tabulate(
            Printer.select(results, order=order,                        width=width),
                            tablefmt=output, headers=headers
                            )
