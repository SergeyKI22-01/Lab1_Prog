import tempfile
import os
import unittest

from lab3_model import (
    FileManager,
    Nedvizhimost,
    ParseError,
    PropertyModel,
    PropertyParser,
    StorageError,
)

class TestPropertyParserValidInput(unittest.TestCase):
    """PropertyParser корректно разбирает допустимые строки."""

    def test_standard_line(self):
        prop = PropertyParser.parse('"Иванов Иван" 01.01.2020 5000000')
        self.assertEqual(prop.owner, "Иванов Иван")
        self.assertEqual(prop.date, "01.01.2020")
        self.assertEqual(prop.cost, 5000000)

    def test_owner_with_spaces(self):
        prop = PropertyParser.parse('"Пупкин Василий Петрович" 15.06.2023 1200000')
        self.assertEqual(prop.owner, "Пупкин Василий Петрович")

    def test_zero_cost_is_allowed(self):
        prop = PropertyParser.parse('"Тест Тест" 01.01.2000 0')
        self.assertEqual(prop.cost, 0)

    def test_leading_and_trailing_whitespace_stripped(self):
        prop = PropertyParser.parse('   "Сидоров Сидор" 10.10.2010 999   ')
        self.assertEqual(prop.owner, "Сидоров Сидор")
        self.assertEqual(prop.cost, 999)

    def test_returns_nedvizhimost_instance(self):
        prop = PropertyParser.parse('"А Б" 01.01.2001 1')
        self.assertIsInstance(prop, Nedvizhimost)

class TestPropertyParserInvalidInput(unittest.TestCase):
    """PropertyParser бросает ParseError для некорректных строк."""

    def test_empty_string_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse("   ")

    def test_missing_opening_quote_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('Иванов Иван" 01.01.2020 1000')

    def test_missing_closing_quote_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов Иван 01.01.2020 1000')

    def test_empty_owner_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"" 01.01.2020 1000')

    def test_missing_cost_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов" 01.01.2020')

    def test_missing_date_and_cost_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов"')

    def test_non_integer_cost_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов" 01.01.2020 abc')

    def test_float_cost_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов" 01.01.2020 1234.56')

    def test_negative_cost_raises(self):
        with self.assertRaises(ParseError):
            PropertyParser.parse('"Иванов" 01.01.2020 -500')

    def test_error_message_contains_line_content(self):
        bad_line = '"Иванов" 01.01.2020 NOT_A_NUMBER'
        with self.assertRaises(ParseError) as ctx:
            PropertyParser.parse(bad_line)
        self.assertIn("NOT_A_NUMBER", str(ctx.exception))

def _make_prop(owner="Тест", date="01.01.2000", cost=100):
    return Nedvizhimost(owner=owner, date=date, cost=cost)

class TestPropertyModelAdd(unittest.TestCase):
    """PropertyModel.add() корректно добавляет объекты."""

    def setUp(self):
        self.model = PropertyModel()

    def test_empty_on_creation(self):
        self.assertEqual(self.model.count(), 0)

    def test_add_single(self):
        self.model.add(_make_prop())
        self.assertEqual(self.model.count(), 1)

    def test_add_multiple(self):
        for i in range(5):
            self.model.add(_make_prop(owner=f"Владелец {i}"))
        self.assertEqual(self.model.count(), 5)

    def test_properties_returns_copy(self):
        self.model.add(_make_prop())
        copy = self.model.properties
        copy.clear()
        self.assertEqual(self.model.count(), 1)

    def test_added_property_preserved(self):
        prop = _make_prop(owner="Уникальный", cost=9999)
        self.model.add(prop)
        self.assertEqual(self.model.properties[0].owner, "Уникальный")
        self.assertEqual(self.model.properties[0].cost, 9999)

class TestPropertyModelRemove(unittest.TestCase):
    """PropertyModel.remove_at() корректно удаляет объекты."""

    def setUp(self):
        self.model = PropertyModel()
        for i in range(3):
            self.model.add(_make_prop(owner=f"Владелец {i}"))

    def test_remove_first(self):
        self.model.remove_at(0)
        self.assertEqual(self.model.count(), 2)
        self.assertEqual(self.model.properties[0].owner, "Владелец 1")

    def test_remove_last(self):
        self.model.remove_at(2)
        self.assertEqual(self.model.count(), 2)
        self.assertEqual(self.model.properties[-1].owner, "Владелец 1")

    def test_remove_middle(self):
        self.model.remove_at(1)
        self.assertEqual(self.model.count(), 2)
        self.assertEqual(self.model.properties[0].owner, "Владелец 0")
        self.assertEqual(self.model.properties[1].owner, "Владелец 2")

    def test_remove_negative_index_raises(self):
        with self.assertRaises(IndexError):
            self.model.remove_at(-1)

    def test_remove_out_of_bounds_raises(self):
        with self.assertRaises(IndexError):
            self.model.remove_at(3)

    def test_remove_from_empty_raises(self):
        empty = PropertyModel()
        with self.assertRaises(IndexError):
            empty.remove_at(0)

class TestPropertyModelClear(unittest.TestCase):
    """PropertyModel.clear() сбрасывает список."""

    def test_clear_removes_all(self):
        model = PropertyModel()
        for _ in range(4):
            model.add(_make_prop())
        model.clear()
        self.assertEqual(model.count(), 0)

    def test_clear_on_empty_is_safe(self):
        model = PropertyModel()
        model.clear()
        self.assertEqual(model.count(), 0)

class TestPropertyModelLoadFromLines(unittest.TestCase):
    """PropertyModel.load_from_lines() корректно загружает строки."""

    def setUp(self):
        self.model = PropertyModel()

    def test_all_valid_lines(self):
        lines = [
            (1, '"Иванов И.И." 01.01.2020 1000000'),
            (2, '"Петров П.П." 02.02.2021 2000000'),
        ]
        errors = self.model.load_from_lines(lines)
        self.assertEqual(self.model.count(), 2)
        self.assertEqual(errors, [])

    def test_invalid_line_is_skipped(self):
        lines = [
            (1, '"Иванов И.И." 01.01.2020 1000000'),
            (2, "эта строка некорректна"),
            (3, '"Петров П.П." 02.02.2021 2000000'),
        ]
        errors = self.model.load_from_lines(lines)
        self.assertEqual(self.model.count(), 2)
        self.assertEqual(len(errors), 1)

    def test_error_message_contains_line_number(self):
        lines = [(7, "НЕКОРРЕКТНАЯ СТРОКА")]
        errors = self.model.load_from_lines(lines)
        self.assertIn("7", errors[0])

    def test_all_invalid_lines_yields_empty_model(self):
        lines = [
            (1, "нет кавычек 01.01.2000 100"),
            (2, '"Нет стоимости" 01.01.2000'),
            (3, '"" 01.01.2000 500'),
        ]
        errors = self.model.load_from_lines(lines)
        self.assertEqual(self.model.count(), 0)
        self.assertEqual(len(errors), 3)

    def test_load_replaces_previous_data(self):
        first_load = [(1, '"Первый" 01.01.2000 111')]
        self.model.load_from_lines(first_load)

        second_load = [
            (1, '"Второй" 02.02.2002 222'),
            (2, '"Третий" 03.03.2003 333'),
        ]
        self.model.load_from_lines(second_load)

        self.assertEqual(self.model.count(), 2)
        self.assertEqual(self.model.properties[0].owner, "Второй")

    def test_empty_input_yields_empty_model(self):
        errors = self.model.load_from_lines([])
        self.assertEqual(self.model.count(), 0)
        self.assertEqual(errors, [])

class TestFileManagerReadLines(unittest.TestCase):
    """FileManager.read_lines() корректно читает файл."""

    def _write_temp(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_reads_non_empty_lines(self):
        path = self._write_temp(
            '"Иванов" 01.01.2020 100\n"Петров" 02.02.2021 200\n'
        )
        lines = FileManager.read_lines(path)
        self.assertEqual(len(lines), 2)
        os.remove(path)

    def test_skips_blank_lines(self):
        path = self._write_temp('"Иванов" 01.01.2020 100\n\n\n"Петров" 02.02.2021 200\n')
        lines = FileManager.read_lines(path)
        self.assertEqual(len(lines), 2)
        os.remove(path)

    def test_returns_correct_line_numbers(self):
        path = self._write_temp('"А" 01.01.2000 1\n\n"Б" 02.02.2001 2\n')
        lines = FileManager.read_lines(path)
        numbers = [n for n, _ in lines]
        self.assertEqual(numbers, [1, 3])
        os.remove(path)

    def test_missing_file_raises_storage_error(self):
        with self.assertRaises(StorageError):
            FileManager.read_lines("/nonexistent/path/file.txt")

    def test_empty_file_returns_empty_list(self):
        path = self._write_temp("")
        lines = FileManager.read_lines(path)
        self.assertEqual(lines, [])
        os.remove(path)

class TestFileManagerSaveProperties(unittest.TestCase):
    """FileManager.save_properties() корректно записывает файл."""

    def test_saved_file_can_be_reloaded(self):
        props = [
            Nedvizhimost("Иванов", "01.01.2020", 100),
            Nedvizhimost("Петров", "02.02.2021", 200),
        ]
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)

        FileManager.save_properties(path, props)
        lines = FileManager.read_lines(path)
        os.remove(path)

        model = PropertyModel()
        errors = model.load_from_lines(lines)

        self.assertEqual(errors, [])
        self.assertEqual(model.count(), 2)
        self.assertEqual(model.properties[0].owner, "Иванов")
        self.assertEqual(model.properties[1].cost, 200)

    def test_save_to_invalid_path_raises_storage_error(self):
        props = [Nedvizhimost("Тест", "01.01.2000", 1)]
        with self.assertRaises(StorageError):
            FileManager.save_properties("/nonexistent_dir/file.txt", props)

    def test_empty_list_creates_empty_file(self):
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        FileManager.save_properties(path, [])
        lines = FileManager.read_lines(path)
        os.remove(path)
        self.assertEqual(lines, [])

class TestRoundTrip(unittest.TestCase):
    """Сохранение и повторная загрузка данных не изменяют содержимое."""

    def test_save_and_reload_preserves_all_fields(self):
        original = [
            Nedvizhimost("Владелец Первый", "01.01.2000", 111111),
            Nedvizhimost("Владелец Второй Третий", "31.12.2023", 9999999),
        ]

        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)

        FileManager.save_properties(path, original)
        lines = FileManager.read_lines(path)
        os.remove(path)

        model = PropertyModel()
        model.load_from_lines(lines)

        reloaded = model.properties
        self.assertEqual(len(reloaded), len(original))
        for orig, rel in zip(original, reloaded):
            self.assertEqual(orig.owner, rel.owner)
            self.assertEqual(orig.date, rel.date)
            self.assertEqual(orig.cost, rel.cost)

if __name__ == "__main__":
    unittest.main(verbosity=2)