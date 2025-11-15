"""
Модуль для построения графа зависимостей.
Реализует алгоритм DFS для получения транзитивных зависимостей.
"""
from dependency_fetcher import DependencyFetcher


class GraphBuilder:
    """Класс для построения графа зависимостей."""
    
    def __init__(self, dependency_fetcher, filter_substring=""):
        """
        Инициализация.
        
        Args:
            dependency_fetcher: Экземпляр DependencyFetcher
            filter_substring: Подстрока для фильтрации пакетов
        """
        self.dependency_fetcher = dependency_fetcher
        self.filter_substring = filter_substring.lower() if filter_substring else ""
        self.graph = {}  # Словарь: пакет -> список зависимостей
        self.visited = set()  # Посещенные пакеты для обнаружения циклов
        self.current_path = set()  # Текущий путь для обнаружения циклов
        self.cycles = []  # Список обнаруженных циклов
    
    def should_filter_package(self, package_name):
        """Проверить, нужно ли фильтровать пакет."""
        if not self.filter_substring:
            return False
        return self.filter_substring in package_name.lower()
    
    def build_graph(self, package_name):
        """
        Построить граф зависимостей для пакета (DFS с рекурсией).
        
        Args:
            package_name: Имя корневого пакета
            
        Returns:
            Словарь графа зависимостей
        """
        self.graph = {}
        self.visited = set()
        self.current_path = set()
        self.cycles = []
        
        self._dfs(package_name)
        
        return self.graph
    
    def _dfs(self, package_name):
        """
        Рекурсивный DFS для построения графа.
        
        Args:
            package_name: Имя текущего пакета
        """
        # Проверка на фильтрацию
        if self.should_filter_package(package_name):
            return
        
        # Обнаружение циклов
        if package_name in self.current_path:
            cycle = list(self.current_path) + [package_name]
            self.cycles.append(cycle)
            return
        
        # Если уже обработали этот пакет, не обрабатываем снова
        if package_name in self.visited:
            return
        
        # Добавляем в текущий путь
        self.current_path.add(package_name)
        
        try:
            # Получаем прямые зависимости
            dependencies = self.dependency_fetcher.get_direct_dependencies(package_name)
            
            # Фильтруем зависимости
            filtered_deps = [dep for dep in dependencies 
                           if not self.should_filter_package(dep)]
            
            # Сохраняем в граф
            self.graph[package_name] = filtered_deps
            
            # Рекурсивно обрабатываем зависимости
            for dep in filtered_deps:
                self._dfs(dep)
        
        except Exception as e:
            # Если не удалось получить зависимости, сохраняем пустой список
            self.graph[package_name] = []
        
        finally:
            # Убираем из текущего пути
            self.current_path.remove(package_name)
            self.visited.add(package_name)
    
    def get_reverse_dependencies(self, package_name):
        """
        Получить обратные зависимости (пакеты, которые зависят от данного).
        
        Args:
            package_name: Имя пакета
            
        Returns:
            Список пакетов, зависящих от данного
        """
        reverse_deps = []
        
        # Проходим по всем пакетам в графе
        for pkg, deps in self.graph.items():
            if package_name in deps:
                reverse_deps.append(pkg)
        
        return reverse_deps
    
    def get_cycles(self):
        """Получить список обнаруженных циклов."""
        return self.cycles

