import pytest
from tableformat import (
    print_table, TableFormatter, TextTableFormatter, CSVTableFormatter,
    HTMLTableFormatter, create_formatter
)

class Record:
    def __init__(self, name, price):
        self.name = name
        self.price = price

@pytest.fixture
def sample_records():
    return [Record('A', 10), Record('B', 20)]

def test_print_table_invalid_formatter():
    with pytest.raises(RuntimeError, match='Expected a TableFormatter'):
        print_table([], [], object())

def test_print_table_execution(capsys, sample_records):
    formatter = TextTableFormatter()
    print_table(sample_records, ['name', 'price'], formatter)
    captured = capsys.readouterr()
    assert 'name' in captured.out
    assert 'price' in captured.out
    assert '10' in captured.out

def test_text_formatter_output(capsys):
    fmt = TextTableFormatter()
    fmt.headings(['A', 'B'])
    fmt.row([1, 2])
    captured = capsys.readouterr()
    assert '         A          B' in captured.out
    assert '1          2' in captured.out

def test_csv_formatter_output(capsys):
    fmt = CSVTableFormatter()
    fmt.headings(['A', 'B'])
    fmt.row([1, 2])
    captured = capsys.readouterr()
    assert 'A,B' in captured.out
    assert '1,2' in captured.out

def test_html_formatter_output(capsys):
    fmt = HTMLTableFormatter()
    fmt.headings(['A'])
    fmt.row([1])
    captured = capsys.readouterr()
    assert '<tr> <th>A</th> </tr>' in captured.out
    assert '<tr> <td>1</td> </tr>' in captured.out

def test_create_formatter_unknown():
    with pytest.raises(RuntimeError, match='Unknown format'):
        create_formatter('unknown')

def test_create_formatter_text():
    fmt = create_formatter('text')
    assert isinstance(fmt, TextTableFormatter)

def test_create_formatter_csv():
    fmt = create_formatter('csv')
    assert isinstance(fmt, CSVTableFormatter)

def test_create_formatter_html():
    fmt = create_formatter('html')
    assert isinstance(fmt, HTMLTableFormatter)

def test_create_formatter_with_options(capsys, sample_records):
    # Tests ColumnFormatMixin and UpperHeadersMixin integration
    fmt = create_formatter(
        'csv', 
        column_formats=['%s', '%.2f'], 
        upper_headers=True
    )
    
    print_table(sample_records, ['name', 'price'], fmt)
    captured = capsys.readouterr()
    
    # Verify UpperHeadersMixin
    assert 'NAME,PRICE' in captured.out
    # Verify ColumnFormatMixin (price formatted to .2f)
    assert 'A,10.00' in captured.out
    assert 'B,20.00' in captured.out

def test_table_formatter_abstract():
    # Verify that TableFormatter cannot be instantiated directly
    with pytest.raises(TypeError):
        TableFormatter()