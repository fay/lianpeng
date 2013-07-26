import re

def find_mentions(content):
    regex = re.compile(ur"@(?P<username>(?!_)(?!.*?_$)(?!\d+)([a-zA-Z0-9_]+))(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]
