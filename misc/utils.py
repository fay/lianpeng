import re

def find_mentions(content):
    regex = re.compile(ur"@(?P<username>(?!_)(?!.*?_$)(?!\d+)([a-zA-Z0-9_]+))(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]


class Choice(object):

    def __init__(self, choices):
        self.choices = choices

    def __getattr__(self, name):
        if name.lower() in self.choices:
            return self.choices.get(name.lower())
        else:
            return super(Choice, self).__getattr__(name)

    def to_choices(self):
        return tuple(zip(self.choices.values(), self.choices.keys()))

    def __iter__(self):
        return self.choices.__iter__()

    def __contains__(self, v):
        return (v in self.choices)

    def __len__(self):
        return len(self.choices)

    def __getitem__(self, v):
        if isinstance(v, basestring):
            return self.choices[v]
        elif isinstance(v, int):
            return self.choices[v]
