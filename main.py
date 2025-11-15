#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов.
Реализует все 5 этапов разработки.
"""
import sys
import os
from config import Config
from dependency_fetcher import DependencyFetcher
from graph_builder import GraphBuilder
from visualizer import Visualizer




def main():
    """Главная функция приложения."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file> [--reverse <package>]")
        print("  --reverse <package>: Show reverse dependencies for a package")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Парсинг опциональных аргументов
    show_reverse = False
    reverse_package = None
    if len(sys.argv) > 2 and sys.argv[2] == '--reverse':
        if len(sys.argv) < 4:
            print("Error: --reverse requires package name")
            sys.exit(1)
        show_reverse = True
        reverse_package = sys.argv[3]
    
    try:
        # Этап 1: Загрузка конфигурации
        config = Config(config_file)
        config.print_params()
        print()
        
        # Создаем fetcher для получения зависимостей
        fetcher = DependencyFetcher(config.repo_url, config.test_mode)
        
        # Этап 2: Получение прямых зависимостей
        print("=" * 60)
        print("Stage 2: Direct Dependencies")
        print("=" * 60)
        try:
            direct_deps = fetcher.get_direct_dependencies(config.package_name)
            print(f"Direct dependencies of '{config.package_name}':")
            if direct_deps:
                for dep in direct_deps:
                    print(f"  - {dep}")
            else:
                print("  (no dependencies)")
        except Exception as e:
            print(f"Error getting direct dependencies: {e}")
            sys.exit(1)
        print()
        
        # Этап 3: Построение графа зависимостей
        print("=" * 60)
        print("Stage 3: Dependency Graph Construction")
        print("=" * 60)
        graph_builder = GraphBuilder(fetcher, config.filter_substring)
        graph = graph_builder.build_graph(config.package_name)
        
        print(f"Dependency graph for '{config.package_name}':")
        print(f"Total packages in graph: {len(graph)}")
        print()
        
        # Выводим граф
        for package, deps in sorted(graph.items()):
            if deps:
                print(f"{package} -> {', '.join(deps)}")
            else:
                print(f"{package} -> (no dependencies)")
        
        # Проверка на циклы
        cycles = graph_builder.get_cycles()
        if cycles:
            print()
            print("Warning: Circular dependencies detected:")
            for cycle in cycles:
                print(f"  Cycle: {' -> '.join(cycle)} -> ...")
        else:
            print()
            print("No circular dependencies detected.")
        print()
        
        # Этап 4: Обратные зависимости (если запрошено)
        if show_reverse:
            print("=" * 60)
            print("Stage 4: Reverse Dependencies")
            print("=" * 60)
            reverse_deps = graph_builder.get_reverse_dependencies(reverse_package)
            print(f"Packages that depend on '{reverse_package}':")
            if reverse_deps:
                for dep in sorted(reverse_deps):
                    print(f"  - {dep}")
            else:
                print("  (no packages depend on this package)")
            print()
        
        # Этап 5: Визуализация
        print("=" * 60)
        print("Stage 5: Visualization")
        print("=" * 60)
        visualizer = Visualizer(graph, config.output_file)
        svg_file = visualizer.visualize()
        
        if svg_file:
            print(f"\nVisualization complete! SVG saved to: {svg_file}")
        else:
            print("\nD2 code generated. Install D2 compiler to generate SVG:")
            print("  https://d2lang.com/")
            print(f"Then run: d2 {config.output_file.replace('.svg', '.d2')} {config.output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

