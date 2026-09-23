import pytest
import sys
import os

# Asegurar que el directorio del archivo objetivo esté en el path
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/stock4')

from tableformat import (
    print_table, TextTableFormatter, CSVTableFormatter, 
    HTMLTableFormatter, create_formatter, TableFormatter
)

class MockRecord:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class InvalidFormatter:
    pass

def test_print_table_exception():
    with pytest.raises(RuntimeError, match='Expected a TableFormatter'):
        print_table([], [], InvalidFormatter())

def test_text_table_formatter(capsys):
    formatter = TextTableFormatter()
    records = [MockRecord('Apple', 10)]
    print_table(records, ['name', 'price'], formatter)
    captured = capsys.readouterr()
    assert '      name      price' in captured.out
    assert '     Apple         10' in captured.out

def test_csv_table_formatter(capsys):
    formatter = CSVTableFormatter()
    records = [MockRecord('Apple', 10)]
    print_table(records, ['name', 'price'], formatter)
    captured = capsys.readouterr()
    assert 'name,price' in captured.out
    assert 'Apple,10' in captured.out

def test_html_table_formatter(capsys):
    formatter = HTMLTableFormatter()
    records = [MockRecord('Apple', 10)]
    print_table(records, ['name', 'price'], formatter)
    captured = capsys.readouterr()
    assert '<tr> <th>name</th> <th>price</th> </tr>' in captured.out
    assert '<tr> <td>Apple</td> <td>10</td> </tr>' in captured.out

def test_create_formatter_text():
    f = create_formatter('text')
    assert isinstance(f, TextTableFormatter)

def test_create_formatter_csv():
    f = create_formatter('csv')
    assert isinstance(f, CSVTableFormatter)

def test_create_formatter_html():
    f = create_formatter('html')
    assert isinstance(f, HTMLTableFormatter)

def test_create_formatter_unknown():
    with pytest.raises(RuntimeError, match='Unknown format unknown'):
        create_formatter('unknown')

def test_create_formatter_with_mixins(capsys):
    f = create_formatter('csv', column_formats=['%s', '%.2f'], upper_headers=True)
    records = [MockRecord('Apple', 10)]
    print_table(records, ['name', 'price'], f)
    captured = capsys.readouterr()
    assert 'NAME,PRICE' in captured.out
    assert 'Apple,10.00' in captured.out

def test_column_format_mixin_logic(capsys):
    f = create_formatter('text', column_formats=['%10s', '%10d'])
    records = [MockRecord('A', 1)]
    print_table(records, ['name', 'price'], f)
    captured = capsys.readouterr()
    assert '         A          1' in captured.out

def test_abstract_class_instantiation():
    with pytest.raises(TypeError):
        TableFormatter()