from shardgather.renderers import (
    render_plain, render_table, render_csv)


collected = {
    'live': [{'a': 1}],
}


def test_render_plain():
    result = render_plain(collected)
    expected = (
        "Total: 1\n"
        "----------------------------------------------------------------\n"
        "{'live': [{'a': 1}]}"
    )
    assert expected == result


def test_render_table():
    result = render_table(collected)
    expected = (
        '+---------+---+\n'
        '| db_name | a |\n'
        '+---------+---+\n'
        '|   live  | 1 |\n'
        '+---------+---+'
    )
    assert expected == result


def test_render_csv():
    result = render_csv(collected)
    expected = (
        'db_name,a\r\n'
        'live,1\r\n'
    )
    assert expected == result
