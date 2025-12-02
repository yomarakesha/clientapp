"""
Точка входа приложения видеонаблюдения
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import logger


def main():
    """Главная функция запуска приложения"""
    logger.info("=" * 80)
    logger.info("Запуск приложения видеонаблюдения")
    logger.info("=" * 80)
    
    try:
        # Создаем приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Клиент видеонаблюдения")
        app.setOrganizationName("VideoClient")
        
        # Создаем и показываем главное окно
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Главное окно отображено")
        
        # Запускаем event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
