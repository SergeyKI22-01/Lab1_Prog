import logging
from dataclasses import dataclass
from typing import List, Tuple

logger = logging.getLogger(__name__)

class ParseError(Exception):
    """Raised when a property line cannot be parsed."""

class StorageError(Exception):
    """Raised on file I/O failures."""

@dataclass
class Nedvizhimost:
    """Represents a single real-estate property record."""

    owner: str
    date: str
    cost: int

class PropertyParser:
    """Converts raw text lines into Nedvizhimost objects."""

    @staticmethod
    def parse(line: str) -> Nedvizhimost:
        """Parses one text line into a Nedvizhimost.

        Expected format: '"Owner Name" DD.MM.YYYY 1234567'

        Args:
            line: A single non-empty string.

        Returns:
            A Nedvizhimost instance.

        Raises:
            ParseError: If the line does not conform to the expected format.
        """
        line = line.strip()
        if not line:
            raise ParseError("Пустая строка.")

        start = line.find('"')
        if start == -1:
            raise ParseError(f"Отсутствует открывающая кавычка: {line!r}")

        end = line.find('"', start + 1)
        if end == -1:
            raise ParseError(f"Отсутствует закрывающая кавычка: {line!r}")

        owner = line[start + 1 : end].strip()
        if not owner:
            raise ParseError(f"Имя владельца не может быть пустым: {line!r}")

        rest = line[end + 1 :].split()
        if len(rest) < 2:
            raise ParseError(f"Отсутствует дата или стоимость: {line!r}")

        date = rest[0]

        try:
            cost = int(rest[1])
        except ValueError:
            raise ParseError(
                f"Стоимость должна быть целым числом, получено {rest[1]!r}: {line!r}"
            )

        if cost < 0:
            raise ParseError(
                f"Стоимость не может быть отрицательной ({cost}): {line!r}"
            )

        return Nedvizhimost(owner=owner, date=date, cost=cost)

class PropertyModel:
    """Manages the in-memory list of property records.

    This class is intentionally free of any UI dependencies so that it
    can be covered by unit tests without starting a GUI.
    """

    def __init__(self) -> None:
        self._properties: List[Nedvizhimost] = []

    @property
    def properties(self) -> List[Nedvizhimost]:
        """Returns a shallow copy of the property list."""
        return list(self._properties)

    def count(self) -> int:
        """Returns the number of properties currently stored."""
        return len(self._properties)

    def add(self, prop: Nedvizhimost) -> None:
        """Appends a property to the list.

        Args:
            prop: The Nedvizhimost object to add.
        """
        self._properties.append(prop)
        logger.info("Добавлен объект: %s", prop)

    def remove_at(self, index: int) -> None:
        """Removes the property at the given index.

        Args:
            index: Zero-based position in the list.

        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self._properties):
            raise IndexError(
                f"Индекс {index} выходит за пределы списка"
                f" (размер {len(self._properties)})."
            )
        removed = self._properties.pop(index)
        logger.info("Удалён объект: %s", removed)

    def clear(self) -> None:
        """Removes all properties from the list."""
        self._properties.clear()

    # -- Bulk loading ----------------------------------------------------

    def load_from_lines(self, numbered_lines: List[Tuple[int, str]]) -> List[str]:
        """Replaces the current list with records parsed from text lines.

        Invalid lines are skipped; a warning is logged for each one.

        Args:
            numbered_lines: A list of (line_number, line_text) pairs.

        Returns:
            A list of human-readable error messages for skipped lines.
        """
        self.clear()
        errors: List[str] = []

        for line_number, line_text in numbered_lines:
            try:
                prop = PropertyParser.parse(line_text)
                self._properties.append(prop)
            except ParseError as exc:
                message = f"Строка {line_number}: {exc}"
                errors.append(message)
                logger.warning(message)

        logger.info(
            "Загрузка завершена: %d объектов, %d ошибок.",
            len(self._properties),
            len(errors),
        )
        return errors

class FileManager:
    """Handles reading and writing property data files."""

    @staticmethod
    def read_lines(file_path: str) -> List[Tuple[int, str]]:
        """Reads non-empty lines from a UTF-8 text file.

        Args:
            file_path: Absolute or relative path to the file.

        Returns:
            A list of (line_number, stripped_line) tuples, skipping blank lines.

        Raises:
            StorageError: If the file cannot be opened or read.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as fobj:
                return [
                    (num, line.strip())
                    for num, line in enumerate(fobj, 1)
                    if line.strip()
                ]
        except FileNotFoundError:
            raise StorageError(f"Файл не найден: {file_path}")
        except OSError as exc:
            raise StorageError(f"Ошибка чтения файла {file_path}: {exc}")

    @staticmethod
    def save_properties(file_path: str, props: List[Nedvizhimost]) -> None:
        """Writes a list of properties to a UTF-8 text file.

        Args:
            file_path: Destination path.
            props: Properties to serialize.

        Raises:
            StorageError: If the file cannot be written.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as fobj:
                for prop in props:
                    fobj.write(f'"{prop.owner}" {prop.date} {prop.cost}\n')
            logger.info(
                "Файл сохранён: %s (%d объектов)", file_path, len(props)
            )
        except OSError as exc:
            raise StorageError(f"Ошибка записи файла {file_path}: {exc}")