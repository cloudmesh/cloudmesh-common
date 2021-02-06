import json
import textwrap

import oyaml as yaml
from cloudmesh.common.FlatDict import flatten
from cloudmesh.common.util import convert_from_unicode
from tabulate import tabulate as tabulate_printer


# noinspection PyPep8
class Printer:
    """
    formats supported dict, yaml, json

    set table.format=table
    cms flavor list
    +-----------+---------+-------+--------+
    | Name      |   VCPUS |   RAM |   Disk |
    |-----------+---------+-------+--------|
    | m1.tiny   |       1 |   512 |      1 |
    | m1.small  |       1 |  2048 |     20 |
    | m1.medium |       2 |  4096 |     40 |
    | m1.large  |       4 |  8192 |     40 |
    | m1.xlarge |       8 | 16384 |     40 |
    +-----------+---------+-------+--------+

    set table.format=grid
    cms flavor list
    ╒═══════════╤═════════╤═══════╤════════╕
    │ Name      │   VCPUS │   RAM │   Disk │
    ╞═══════════╪═════════╪═══════╪════════╡
    │ m1.tiny   │       1 │   512 │      1 │
    ├───────────┼─────────┼───────┼────────┤
    │ m1.small  │       1 │  2048 │     20 │
    ├───────────┼─────────┼───────┼────────┤
    │ m1.medium │       2 │  4096 │     40 │
    ├───────────┼─────────┼───────┼────────┤
    │ m1.large  │       4 │  8192 │     40 │
    ├───────────┼─────────┼───────┼────────┤
    │ m1.xlarge │       8 │ 16384 │     40 │
    ╘═══════════╧═════════╧═══════╧════════╛

    """

    @staticmethod
    def default():
        return "psql"

    @staticmethod
    def select(results, order=None, width=None):
        """
        selects field in the order as defined in order
        If order is non, all fileds will be taken

        :param results: a flat dict
        :param order: the order of the fields
        :param width:
        :return: a list of dicts
        """
        if order is None:
            columns = len(results[0])
        else:
            columns = len(order)

        if type(width) == int:
            _width = [width] * columns
        elif type(width) == list:
            _width = width
        else:
            _width = [40] * columns

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
                    if _width[i]:
                        try:
                            field = result[key]
                            if type(field) == list:
                                field = ", ".join(field)
                            entry.append("\n".join(
                                textwrap.wrap(str(field), _width[i])))
                        except:
                            entry.append("")
                    else:
                        entry.append(result[key])
                    i = i + 1
                _results.append(entry)
        return _results

    @staticmethod
    def write(results,
              order=None,
              header=None,
              output='table',
              width=None,
              humanize=False,
              max_width=None,
              sep='.'):

        width = width or max_width  # maxwidth is deprecated

        if header:
            header = list(header)
        elif order:
            header = list(order)

        if output == 'table':
            output = Printer.default()

        #
        # Make sure that we have a list of dicts
        #
        if type(results) == dict:
            _results = Printer._to_tabulate(results)
        else:
            _results = list(results)

        if output == "json":
            return json.dumps(_results,
                              # sort_keys=sort_keys,
                              indent=4)
        elif output == "yaml":
            return yaml.dump(convert_from_unicode(_results),
                             default_flow_style=False)
        elif output == "dict":
            return _results
        elif output == 'csv':
            flat = flatten(_results, sep=sep)

            return Printer.csv(flat,
                               order=order,
                               header=header,
                               humanize=humanize,
                               sort_keys=True)

        _results = Printer.select(_results,
                                  order=order,
                                  width=width)

        if output in ['flat', 'html']:

            if order is not None:

                flat = []
                for element in results:
                    _element = {}
                    for attribute in element:
                        if attribute in order:
                            _element[attribute] = element[attribute]
                    flat.append(_element)

                _results = flat

        if output in ['flat']:
            return (_results)

        if header:
            return tabulate_printer(_results, tablefmt=output, headers=header)
        else:
            return tabulate_printer(_results, tablefmt=output)

    @staticmethod
    def _to_tabulate(d):
        """

        :param d: dict of dicts
        :return: list of dicts with the key as name
        """
        results = []
        for key in d:
            results.append(d[key])

        return results

    @staticmethod
    def flatwrite(table,
                  order=None,
                  header=None,
                  output="table",
                  sort_keys=True,
                  show_none="",
                  humanize=None,
                  sep=".",
                  max_width=48,  # deprecated use width
                  width=48,
                  ):
        """
        writes the information given in the table
        :param table: the table of values
        :param order: the order of the columns
        :param header: the header for the columns
        :param output: the format (default is table, values are raw, csv, json, yaml, dict
        :param sort_keys: if true the table is sorted
        :param show_none: passed along to the list or dict printer
        :param sep: uses sep as the separator for csv printer
        :param width: maximum width for a cell
        :type width: int
        :param max_width: deprecated use width
        :type max_width: int
        :return:
        """
        width = width or max_width  # max_width is deprecated. thi is used for those still using it

        flat = flatten(table, sep=sep)

        return Printer.write(flat,
                             order=order,
                             header=header,
                             output=output,
                             width=width
                             )
        """
        return Printer.write(flat,
                             sort_keys=sort_keys,
                             order=order,
                             header=header,
                             output=output,
                             humanize=humanize,
                             width=width
                             )
        """

    @classmethod
    def attribute(cls, d,
                  header=None,
                  order=None,
                  sort_keys=True,
                  humanize=None,
                  output="table",
                  width=70):
        """
        prints a attribute/key value table

        :param d: A a dict with dicts of the same type.
                  Each key will be a column
        :param order: The order in which the columns are printed.
                       The order is specified by the key names of the dict.
        :param header:  The Header of each of the columns
        :type header:   A list of string
        :param sort_keys:   Key(s) of the dict to be used for sorting.
                             This specify the column(s) in the table for sorting.
        :type sort_keys:    string or a tuple of string (for sorting with multiple columns)
        :param output: the output format table, csv, dict, json
        """

        if header is None:
            header = ["Attribute", "Value"]
        x = []
        if order is not None:
            sorted_list = order
        else:
            sorted_list = list(d)
        if sort_keys:
            sorted_list = sorted(d)

        for key in sorted_list:
            if type(d[key]) == dict:
                values = d[key]
                x.append([key, "+"])
                for e in values:
                    x.append(["  - {}: {}".format(e, values[e])])
            elif type(d[key]) == list:
                values = list(d[key])
                x.append([key, "+"])
                for e in values:
                    x.append(["  -", e])
            else:
                x.append([key, str(d[key]) or ""])

        if output == 'table':
            output = Printer.default()

        return tabulate_printer(x, tablefmt=output, headers=header)

    @classmethod
    def csv(cls, d,
            order=None,
            header=None,
            humanize=None,
            sort_keys=True):
        """
        prints a table in csv format

        :param d: A a dict with dicts of the same type.
        :type d: dict
        :param order: The order in which the columns are printed.
                      The order is specified by the key names of the dict.
        :type order:
        :param header: The Header of each of the columns
        :type header: list or tuple of field names
        :param sort_keys: TODO - not yet implemented
        :type sort_keys: bool
        :return: a string representing the table in csv format
        """

        if order is None:
            first_element = list(d)[0]

        def _keys():
            return list(first_element.keys())

        # noinspection PyBroadException
        def _get(element, key):
            try:
                tmp = str(d[element][key])
            except:
                tmp = ' '
            return tmp

        if d is None or d == {}:
            return None

        if order is None:
            order = _keys()

        if header is None and order is not None:
            header = order
        elif header is None:
            header = _keys()

        table = ""
        content = []
        for attribute in order:
            content.append(attribute)

        table = table + ",".join([str(e) for e in content]) + "\n"

        for job in d:
            content = []
            for attribute in order:
                try:
                    # if attribute in humanize:
                    #    value = parser.parse(d[job][attribute])
                    #    content.append(naturaltime(value))
                    #    pass
                    # else:
                    content.append(job[attribute])

                except Exception as e:
                    content.append(e)
            table = table + ",".join([str(e) for e in content]) + "\n"
        return table
