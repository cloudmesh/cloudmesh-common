from tabulate import tabulate

class Printer:

    @staticmethod
    def select(results, order=None):
        if order is None or results is None:
            return results
        _results = []
        for result in results:
            _results.append([result[x] for x in order])

        return _results

    @staticmethod
    def write(results, order=None, header=None, output='psql'):
        if header:
            headers = header
        else:
            headers = order
        return tabulate(Printer.select(results, order=order),
                        headers=headers,
                        tablefmt=output)
