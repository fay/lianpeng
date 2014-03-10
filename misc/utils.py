import re

def find_mentions(content):
    regex = re.compile(ur"@(?P<username>(?!_)(?!.*?_$)(?!\d+)([a-zA-Z0-9_]+))(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]


class Choice(object):

    def __init__(self, *choice_tuples):
        self.choices_dict = {}
        for choice in choice_tuples:
            self.choices_dict[choice[0]] = choice[1]
        self.choices = [(item[1], item[0]) for item in choice_tuples]

    def __getattr__(self, name):
        return self.choices_dict.get(name)

    def __iter__(self):
        return self.choices.__iter__()

    def __contains__(self, v):
        return (v in self.choices_dict)

    def __len__(self):
        return len(self.choices)

    def __getitem__(self, v):
        if isinstance(v, basestring):
            return self.choices_dict[v]
        elif isinstance(v, int):
            return self.choices_dict[v]
