import pytest
from string_processing import StringProcessor

class TestStringProcessor:
    def test_replace_non_letters_non_numbers_with_whitespace(self):
        # Caso normal: mezcla de caracteres alfanuméricos y símbolos
        input_str = "hello!@#world123"
        expected = "hello    world123"
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace(input_str) == expected

        # Caso borde: cadena vacía
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("") == ""

        # Caso borde: solo caracteres no alfanuméricos
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("!!!") == "   "

        # Caso normal: cadena con espacios existentes
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("a-b") == "a b"

    def test_strip(self):
        # Caso normal: espacios al inicio y final
        assert StringProcessor.strip("  hello  ") == "hello"
        
        # Caso borde: cadena sin espacios
        assert StringProcessor.strip("hello") == "hello"
        
        # Caso borde: cadena vacía
        assert StringProcessor.strip("") == ""

    def test_to_lower_case(self):
        # Caso normal: convertir a minúsculas
        assert StringProcessor.to_lower_case("HELLO") == "hello"
        
        # Caso borde: ya en minúsculas
        assert StringProcessor.to_lower_case("hello") == "hello"
        
        # Caso borde: caracteres especiales/no alfabéticos
        assert StringProcessor.to_lower_case("123!@#") == "123!@#"

    def test_to_upper_case(self):
        # Caso normal: convertir a mayúsculas
        assert StringProcessor.to_upper_case("hello") == "HELLO"
        
        # Caso borde: ya en mayúsculas
        assert StringProcessor.to_upper_case("HELLO") == "HELLO"
        
        # Caso borde: caracteres especiales/no alfabéticos
        assert StringProcessor.to_upper_case("123!@#") == "123!@#"

    def test_type_error_on_non_string_input(self):
        # Las funciones delegadas a string (strip, lower, upper) lanzan AttributeError 
        # si se pasa algo que no sea un string (como None o int)
        with pytest.raises(AttributeError):
            StringProcessor.strip(None)
            
        with pytest.raises(AttributeError):
            StringProcessor.to_lower_case(123)

        # La regex sub espera una cadena
        with pytest.raises(TypeError):
            StringProcessor.replace_non_letters_non_numbers_with_whitespace(None)