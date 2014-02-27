DEFAULT_RENDERER = 'csv'


def render_plain(collected):
    import pprint

    return '\n'.join(
        ["Total: %d" % len(collected),
         "-" * 64,
         pprint.pformat(collected)])


def render_table(collected):
    if not collected:
        return "No output"

    from prettytable import PrettyTable
    pt = PrettyTable()

    for live in collected:
        for entry in collected[live]:
            if not pt.field_names:
                pt.field_names = ['db_name'] + list(entry.keys())
            pt.add_row([live] + entry.values())
    return str(pt)


def render_csv(collected):
    import csv
    from cStringIO import StringIO

    output = StringIO()
    writer = csv.writer(output)
    header = []
    for live in collected:
        for entry in collected[live]:
            if not header:
                header = ['db_name'] + list(entry.keys())
                writer.writerow(header)
            writer.writerow([live] + entry.values())
    output.seek(0)
    return output.read()


RENDERERS = {
    'plain': render_plain,
    'csv': render_csv,
    'table': render_table,
}
