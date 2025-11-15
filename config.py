import xml.etree.ElementTree as ET
import os


class Config:
    """Класс для работы с конфигурацией из XML файла."""
    
    def __init__(self, config_file):
        """
        Инициализация конфигурации из XML файла.
        
        Args:
            config_file: Путь к XML файлу конфигурации
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если параметры некорректны
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        
        self.package_name = self._get_text(root, 'package_name')
        self.repo_url = self._get_text(root, 'repo_url')
        self.test_mode = self._get_bool(root, 'test_mode')
        self.output_file = self._get_text(root, 'output_file')
        # filter_substring может быть пустым (означает "без фильтрации")
        self.filter_substring = self._get_text_optional(root, 'filter_substring')
    
    def _get_text(self, root, tag):
        """
        Получить текстовое значение элемента.
        
        Args:
            root: Корневой элемент XML
            tag: Имя тега
            
        Returns:
            Текстовое значение
            
        Raises:
            ValueError: Если элемент отсутствует или пуст
        """
        element = root.find(tag)
        if element is None or element.text is None:
            raise ValueError(f"Missing or empty parameter: {tag}")
        return element.text.strip()
    
    def _get_text_optional(self, root, tag):
        """
        Получить текстовое значение элемента (опциональный параметр).
        Если элемент отсутствует или пуст, возвращает пустую строку.
        
        Args:
            root: Корневой элемент XML
            tag: Имя тега
            
        Returns:
            Текстовое значение или пустая строка
        """
        element = root.find(tag)
        if element is None or element.text is None:
            return ""
        return element.text.strip()
    
    def _get_bool(self, root, tag):
        """
        Получить булево значение элемента.
        
        Args:
            root: Корневой элемент XML
            tag: Имя тега
            
        Returns:
            Булево значение
            
        Raises:
            ValueError: Если значение некорректно
        """
        text = self._get_text(root, tag)
        if text.lower() in ('true', '1', 'yes'):
            return True
        elif text.lower() in ('false', '0', 'no'):
            return False
        else:
            raise ValueError(f"Invalid boolean value for {tag}: {text}. Expected 'true' or 'false'")
    
    def print_params(self):
        """Вывести все параметры конфигурации в формате ключ-значение."""
        print("Configuration parameters:")
        print(f"  package_name: {self.package_name}")
        print(f"  repo_url: {self.repo_url}")
        print(f"  test_mode: {self.test_mode}")
        print(f"  output_file: {self.output_file}")
        print(f"  filter_substring: {self.filter_substring}")
