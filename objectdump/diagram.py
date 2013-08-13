def make_dot(data, filename):
    """
    Make a .dot file based on the {obj: {field: set(objs)}} data structure
    """
    import os
    filename = os.path.abspath(os.path.expanduser(filename))
    lines = [
        'digraph G {',
    ]
    for obj, fields in dict(data).items():
        for field, foreign_objs in dict(fields).items():
            for foreign_obj in list(foreign_objs):
                params = {'obj': obj, 'field': field, 'foreign_obj': foreign_obj}
                lines.append('"{obj}" -> "{foreign_obj}"[label="{field}"];'.format(**params))
    lines.append('}')
    with open(filename, 'w') as f:
        f.write("\n".join(lines))
