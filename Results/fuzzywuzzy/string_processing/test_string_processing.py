import sys
import pytest

# Ajuste necesario para importar el módulo desde la ruta especificada
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/fuzzywuzzy')

from string_processing import StringProcessor

class TestStringProcessor:

    def test_replace_non_letters_non_numbers_with_whitespace(self):
        # El método regex.sub(" ", a_string) reemplaza cada caracter no alfanumérico individualmente
        input_str = "abc!!!def"
        expected = "abc   def"
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace(input_str) == expected

        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("a-b") == "a b"
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("") == ""
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("123") == "123"

    def test_strip(self):
        assert StringProcessor.strip("  abc  ") == "abc"
        assert StringProcessor.strip("abc") == "abc"
        assert StringProcessor.strip("  ") == ""

    def test_to_lower_case(self):
        assert StringProcessor.to_lower_case("ABC") == "abc"
        assert StringProcessor.to_lower_case("AbC123") == "abc123"
        assert StringProcessor.to_lower_case("") == ""

    def test_to_upper_case(self):
        assert StringProcessor.to_upper_case("abc") == "ABC"
        assert StringProcessor.to_upper_case("aBc123") == "ABC123"
        assert StringProcessor.to_upper_case("") == ""

    def test_type_errors(self):
        # En Python 3, str.lower/upper/strip sobre un entero eleva TypeError
        # porque son métodos descriptores de la clase str.
        with pytest.raises(TypeError):
            StringProcessor.to_lower_case(123)
        
        with pytest.raises(AttributeError):
            StringProcessor.strip(None)

        # La expresión regular en sub espera un string, pasar None lanza un TypeError
        with pytest.raises(TypeError):
            StringProcessor.replace_non_letters_non_numbers_with_whitespace(None)