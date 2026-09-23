import sys
import pytest

# Asegurar que el directorio del archivo fuente esté en el sys.path para permitir la importación
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/fuzzywuzzy')

from string_processing import StringProcessor

class TestStringProcessor:

    def test_replace_non_letters_non_numbers_with_whitespace(self):
        # El regex (?ui)\W reemplaza cualquier carácter que no sea word (alfanumérico + underscore)
        input_str = "hello-world_123!?"
        # "-" y "!" y "?" son \W. "_" es \w.
        # "hello" + " " + "world_123" + "  "
        result = StringProcessor.replace_non_letters_non_numbers_with_whitespace(input_str)
        assert result == "hello world_123  "

        # Caso borde: cadena vacía
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("") == ""

        # Caso borde: solo caracteres \W
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace("!!!") == "   "

        # Caso borde: solo caracteres alfanuméricos
        input_str = "abc123ABC"
        assert StringProcessor.replace_non_letters_non_numbers_with_whitespace(input_str) == "abc123ABC"

    def test_strip(self):
        # Caso normal: espacios al inicio y final
        assert StringProcessor.strip("  hello  ") == "hello"
        
        # Caso borde: cadena vacía
        assert StringProcessor.strip("   ") == ""
        
        # Caso borde: sin espacios
        assert StringProcessor.strip("hello") == "hello"

    def test_to_lower_case(self):
        # Caso normal: mezcla de mayúsculas
        assert StringProcessor.to_lower_case("HELLO world") == "hello world"
        
        # Caso borde: ya en minúsculas
        assert StringProcessor.to_lower_case("abc") == "abc"
        
        # Caso borde: cadena vacía
        assert StringProcessor.to_lower_case("") == ""

    def test_to_upper_case(self):
        # Caso normal: mezcla de minúsculas
        assert StringProcessor.to_upper_case("hello WORLD") == "HELLO WORLD"
        
        # Caso borde: ya en mayúsculas
        assert StringProcessor.to_upper_case("ABC") == "ABC"
        
        # Caso borde: cadena vacía
        assert StringProcessor.to_upper_case("") == ""

    def test_invalid_input_types(self):
        # Validación de comportamiento ante tipos incorrectos
        # En Python, llamar str.strip(None) levanta TypeError y no AttributeError
        with pytest.raises(TypeError):
            StringProcessor.strip(None)
            
        with pytest.raises(TypeError):
            StringProcessor.to_lower_case(123)
            
        with pytest.raises(TypeError):
            # re.sub espera un string, enviar None causa TypeError
            StringProcessor.replace_non_letters_non_numbers_with_whitespace(None)