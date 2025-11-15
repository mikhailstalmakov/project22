"""
Модуль для визуализации графа зависимостей.
Генерирует представление на языке D2 и сохраняет в SVG.
"""
import subprocess
import os
import tempfile


class Visualizer:
    """Класс для визуализации графа зависимостей."""
    
    def __init__(self, graph, output_file="graph.svg"):
        """
        Инициализация.
        
        Args:
            graph: Словарь графа зависимостей
            output_file: Имя выходного файла SVG
        """
        self.graph = graph
        self.output_file = output_file
    
    def generate_d2_code(self):
        """
        Сгенерировать код на языке D2 для графа.
        
        Returns:
            Строка с кодом D2
        """
        lines = []
        lines.append("// Dependency graph visualization")
        lines.append("")
        
        # Собираем все пакеты
        all_packages = set()
        for package, deps in self.graph.items():
            all_packages.add(package)
            all_packages.update(deps)
        
        # Определяем связи (D2 автоматически создает узлы)
        for package, deps in self.graph.items():
            for dep in deps:
                pkg_escaped = self._escape_d2_identifier(package)
                dep_escaped = self._escape_d2_identifier(dep)
                lines.append(f'{pkg_escaped} -> {dep_escaped}')
        
        return '\n'.join(lines)
    
    def _escape_d2_identifier(self, identifier):
        """
        Экранировать идентификатор для D2.
        
        Args:
            identifier: Имя пакета
            
        Returns:
            Экранированное имя
        """
        # Если содержит специальные символы, заключаем в кавычки
        if any(c in identifier for c in ['-', '.', ' ', ':', '/', '\\']):
            return f'"{identifier}"'
        return identifier
    
    def save_d2_file(self, d2_code, filename="graph.d2"):
        """
        Сохранить код D2 в файл.
        
        Args:
            d2_code: Код на языке D2
            filename: Имя файла
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(d2_code)
        return filename
    
    def generate_svg(self, d2_file=None):
        """
        Сгенерировать SVG из D2 файла.
        
        Args:
            d2_file: Путь к файлу D2 (если None, создается временный)
            
        Returns:
            Путь к созданному SVG файлу
        """
        # Генерируем D2 код
        d2_code = self.generate_d2_code()
        
        # Сохраняем во временный файл, если не указан
        if d2_file is None:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False, encoding='utf-8') as f:
                f.write(d2_code)
                d2_file = f.name
        
        try:
            # Проверяем наличие d2
            try:
                subprocess.run(['d2', '--version'], 
                             capture_output=True, 
                             check=True, 
                             timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print("Warning: D2 compiler not found. Install it from https://d2lang.com/")
                print("D2 code saved to:", d2_file)
                print("\nTo generate SVG, run:")
                print(f"  d2 {d2_file} {self.output_file}")
                return None
            
            # Компилируем D2 в SVG
            result = subprocess.run(
                ['d2', d2_file, self.output_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Error generating SVG: {result.stderr}")
                print("D2 code saved to:", d2_file)
                return None
            
            print(f"SVG file generated: {self.output_file}")
            return self.output_file
        
        except Exception as e:
            print(f"Error during SVG generation: {e}")
            print("D2 code saved to:", d2_file)
            return None
    
    def visualize(self):
        """
        Выполнить полную визуализацию: сгенерировать D2 код и SVG.
        
        Returns:
            Путь к созданному SVG файлу или None
        """
        d2_code = self.generate_d2_code()
        d2_file = self.output_file.replace('.svg', '.d2')
        self.save_d2_file(d2_code, d2_file)
        
        print("\nD2 code:")
        print("=" * 50)
        print(d2_code)
        print("=" * 50)
        
        return self.generate_svg(d2_file)

