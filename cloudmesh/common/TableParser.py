from __future__ import print_function
import json


class TableParser(object):
    @classmethod
    def convert(cls, table=None,
                output='dict',
                header=True,
                index=None,
                change=None,
                strip=True,
                lower=True,
                strip_seperator=True,
                seperator="|",
                comment_chars="+#"):
        if change is None:
            change = [(":", "_"), ("(", "_"), (")", ""), ("/", "_")]
        parser = TableParser(
            output=output,
            header=header,
            index=index,
            change=change,
            strip=strip,
            lower=lower,
            strip_seperator=strip_seperator,
            seperator=seperator,
            comment_chars=comment_chars)
        if table is not None:
            if 'dict' in output:
                return parser.to_dict(table)
            elif 'list' in output:
                return parser.to_dict(table)
            else:
                raise ValueError("output type not supported")

    def __init__(self,
                 output='dict',
                 header=True,
                 index=None,
                 change=None,
                 strip=True,
                 lower=True,
                 strip_seperator=True,
                 seperator="|",
                 comment_chars="+#"):
        """

        :param header: if true the first line is a header. Not implemented
        :param index: if true, identifies one of the heade column as index
                      for dict key naming
        :param change: an array of tuples of characters that need to be
                       changed to allow key creation in the dict
        :param strip: if true the the lines start and end with the separator
        :param lower: converts headers to lower case
        :param strip_seperator: removes the spaces before and after the
                                separator
        :param seperator: the separator character, default is |
        :param comment_chars: lines starting with this chars will be ignored
        :return:
        """
        if change is None:
            change = [(":", "_"), ("(", "_"), (")", ""), ("/", "_")]
        self.data = None
        self.output = None
        self.with_header = header
        self.change = change
        self.is_lower = lower
        self.is_strip = strip
        self.index = index
        self.strip_seperator = strip_seperator
        self.seperator = seperator
        self.comment_chars = comment_chars
        self.lines = None

    def clean(self, line):
        """
        :param line: cleans the string
        :return:
        """
        # print ("-" + line + "-")
        if line == '':
            line = 'None'
        if self.is_lower:
            line = line.lower()
        if line == "user ":  # for slurm which has "user" and "user "
            line = "userid"
        for convert in self.change:
            line = line.replace(convert[0], convert[1])
        if self.is_strip:
            line = line.strip()
        return line.strip(' ')

    def extract_lines(self, table):
        lines = table.splitlines()
        self.lines = []
        for line in lines:
            if self.is_strip:
                line = line.strip()
            if line[0] not in self.comment_chars:
                self.lines.append(line)
        return self.lines

    def _get_headers(self):
        """
        assumes comment have been stripped with extract
        :return:
        """

        header = self.lines[0]
        self.lines = self.lines[1:]

        self.headers = \
            [self.clean(h) for h in header.split(self.seperator)]
        if self.is_strip:
            self.headers = self.headers[1:-1]
        return self.headers

    def to_dict(self, table):
        """

        :param table: converts a stream called line to a dict
        :type table: string
        :return: the dict
        """

        self.extract_lines(table)

        self._get_headers()

        i = 0
        self.data = {}
        for line in self.lines:
            element = [h.strip() for h in line.split(self.seperator)]
            if self.is_strip:
                element = element[1:-1]
            entry = {}
            for column in range(0, len(self.headers)):
                entry[self.headers[column]] = element[column]
            if self.index is None:
                self.data[str(i)] = dict(entry)
            else:
                self.data[entry[self.index]] = dict(entry)
            i += 1
        return self.data

    def to_list(self, table):
        """
        :param table: converts a stream called line to a list
        :type table: string
        :return: the list
        """
        self.extract_lines(table)

        self._get_headers()

        i = 0
        self.data = []
        for line in self.lines:
            element = [h.strip() for h in line.split(self.seperator)]
            if self.is_strip:
                element = element[1:-1]

            entry = {}
            for column in range(0, len(self.headers)):
                entry[self.headers[column]] = element[column]
            if self.index is None:
                entry["_id"] = str(i)
            else:
                entry["_id"] = self.index
            self.data.append(entry)
            i += 1
        return self.data

    def json(self):
        return self.data

    def __str__(self):
        return json.dumps(self.data, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    parser = TableParser()
    d = parser.to_list("|a|b|c|\n|1|2|3|\n+|4|5|6|\n|7|8|9|")
    print(d)
    print(parser.json())
    print(parser.headers)
    print(parser)

    parser.to_dict("|a|b|c|\n|1|2|3|\n|4|5|6|")
    print(parser.json())

    print(parser.headers)
    print(parser)
