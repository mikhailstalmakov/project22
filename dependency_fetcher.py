"""
Модуль для получения зависимостей пакетов Python.
Поддерживает работу с PyPI API и тестовым репозиторием.
"""
import urllib.request
import json
import os


class DependencyFetcher:
    """Класс для получения зависимостей пакетов."""
    
    def __init__(self, repo_url, test_mode=False):
        """
        Инициализация.
        
        Args:
            repo_url: URL репозитория PyPI или путь к тестовому файлу
            test_mode: Режим тестирования (работа с файлом)
        """
        self.repo_url = repo_url
        self.test_mode = test_mode
    
    def get_direct_dependencies(self, package_name):
        """
        Получить прямые зависимости пакета.
        
        Args:
            package_name: Имя пакета
            
        Returns:
            Список имен зависимостей
        """
        if self.test_mode:
            return self._get_dependencies_from_test_file(package_name)
        else:
            return self._get_dependencies_from_pypi(package_name)
    
    def _get_dependencies_from_pypi(self, package_name):
        """Получить зависимости из PyPI API."""
        try:
            # Формируем URL для конкретного пакета
            url = f"https://pypi.org/pypi/{package_name}/json"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            info = data.get('info', {})
            requires_dist = info.get('requires_dist', [])
            
            if requires_dist is None:
                return []
            
            dependencies = []
            for req in requires_dist:
                # Парсинг requires_dist: убираем версии, условия и т.д.
                # Формат может быть: "package", "package>=1.0", "package[extra]"
                dep = req.split()[0].split('(')[0].split('[')[0].strip()
                if dep:
                    dependencies.append(dep)
            
            return dependencies
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise RuntimeError(f"Package '{package_name}' not found on PyPI")
            raise RuntimeError(f"Failed to fetch package info: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch dependencies: {e}")
    
    def _get_dependencies_from_test_file(self, package_name):
        """Получить зависимости из тестового файла."""
        if not os.path.exists(self.repo_url):
            raise FileNotFoundError(f"Test repository file '{self.repo_url}' not found")
        
        try:
            with open(self.repo_url, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг тестового файла
            # Формат: пакеты называются большими латинскими буквами
            # Формат файла: каждая строка содержит зависимости пакета
            # Например: "A: B C D" означает, что A зависит от B, C, D
            
            dependencies = []
            lines = content.strip().split('\n')
            package_found = False
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Формат: PACKAGE: DEP1 DEP2 DEP3
                if ':' in line:
                    parts = line.split(':', 1)
                    current_package = parts[0].strip()
                    deps_str = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Сравниваем без учета регистра
                    if current_package.upper() == package_name.upper():
                        # Нашли нужный пакет
                        package_found = True
                        if deps_str:
                            deps = deps_str.split()
                            dependencies.extend([d.strip() for d in deps if d.strip()])
                        break
            
            # Если пакет не найден, возвращаем пустой список (не ошибка)
            # Это позволяет обрабатывать пакеты без зависимостей
            return dependencies
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to read test repository file: {e}")

