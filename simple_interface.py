"""
ConsciousAI v5.0 - Simple Intuitive Interface
Простой интуитивный интерфейс - управление одним словом

Команды:
- создай - Создать проект
- маркетинг - Запустить маркетинг
- анализ - Глубокий анализ
- инсайт - Генерировать инсайты
- память - Посмотреть память
- рефлексия - Рефлексия AI
- партнёр - Режим партнёра
- помощь - Справка
"""

import sys
from typing import Optional, Dict, Any
from datetime import datetime


class SimpleInterface:
    """
    Простой интерфейс с командами одним словом

    Философия: Меньше слов, больше действия!
    """

    # Цвета для терминала (ANSI)
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }

    def __init__(self):
        self.current_mode = "dialogue"  # dialogue, command, partner, reflection
        self.session_start = datetime.now()

    def print_colored(self, text: str, color: str = "reset", bold: bool = False):
        """Печать цветного текста"""
        prefix = self.COLORS.get("bold", "") if bold else ""
        color_code = self.COLORS.get(color, "")
        reset = self.COLORS.get("reset", "")
        print(f"{prefix}{color_code}{text}{reset}")

    def show_banner(self):
        """Показать приветственный баннер"""
        self.print_colored("\n" + "=" * 60, "cyan", bold=True)
        self.print_colored("  🧠 ConsciousAI v5.0 - Мета-Сознательный AI", "cyan", bold=True)
        self.print_colored("=" * 60, "cyan", bold=True)
        print()
        self.print_colored("  Простой интерфейс - управление одним словом!", "blue")
        self.print_colored("  Введите 'помощь' для списка команд", "blue")
        print()

    def show_help(self):
        """Показать справку по командам"""
        self.print_colored("\n📚 Команды (одно слово!):", "yellow", bold=True)
        print()

        commands = [
            ("создай", "Создать проект (бот, сайт, игра)", "green"),
            ("маркетинг", "Запустить маркетинговую кампанию 24/7", "green"),
            ("анализ", "Глубокий анализ темы или кода", "blue"),
            ("инсайт", "Генерировать инсайты и идеи", "magenta"),
            ("память", "Посмотреть смысловую память", "cyan"),
            ("рефлексия", "AI анализирует своё мышление", "yellow"),
            ("партнёр", "Режим партнёра (совместное мышление)", "magenta"),
            ("статистика", "Статистика работы AI", "cyan"),
            ("помощь", "Эта справка", "blue"),
            ("выход", "Завершить работу", "red")
        ]

        for cmd, description, color in commands:
            self.print_colored(f"  • {cmd:15} - {description}", color)

        print()
        self.print_colored("💡 Совет: Можно писать команды и по-английски!", "blue")
        print()

    def parse_command(self, user_input: str) -> tuple[str, str]:
        """
        Распознать команду

        Returns:
            (command, args)
        """
        parts = user_input.strip().split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        # Поддержка английских команд
        command_map = {
            "create": "создай",
            "marketing": "маркетинг",
            "analysis": "анализ",
            "analyze": "анализ",
            "insight": "инсайт",
            "memory": "память",
            "reflection": "рефлексия",
            "reflect": "рефлексия",
            "partner": "партнёр",
            "stats": "статистика",
            "help": "помощь",
            "exit": "выход",
            "quit": "выход"
        }

        command = command_map.get(command, command)

        return command, args

    def handle_create(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'создай'"""
        self.print_colored("\n🚀 Создание проекта", "green", bold=True)
        print()

        # Если нет аргументов - спросить
        if not args:
            self.print_colored("Что создаём?", "blue")
            print("  1. Telegram бот")
            print("  2. Веб-сайт")
            print("  3. Discord бот")
            print("  4. REST API")
            print("  5. Игра")
            print("  6. CLI приложение")
            print()

            choice = input("Выбери номер (или опиши своими словами): ").strip()

            # Преобразовать выбор
            choice_map = {
                "1": "telegram бот",
                "2": "веб-сайт",
                "3": "discord бот",
                "4": "rest api",
                "5": "игра",
                "6": "cli приложение"
            }
            args = choice_map.get(choice, choice)

        self.print_colored(f"\n✨ Создаю: {args}", "green")
        print()

        return {
            "action": "create_project",
            "project_type": args,
            "status": "initiated"
        }

    def handle_marketing(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'маркетинг'"""
        self.print_colored("\n📢 Маркетинговая автоматизация 24/7", "green", bold=True)
        print()

        # Если нет аргументов - спросить минимум
        if not args:
            product_name = input("Название продукта: ").strip()
            target_audience = input("Целевая аудитория (кратко): ").strip()

            args = f"{product_name} для {target_audience}"

        self.print_colored(f"\n🎯 Запускаю кампанию: {args}", "green")
        print()

        return {
            "action": "launch_marketing",
            "description": args,
            "status": "initiated"
        }

    def handle_analysis(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'анализ'"""
        self.print_colored("\n🔍 Глубокий анализ", "blue", bold=True)
        print()

        if not args:
            args = input("Что анализируем? ").strip()

        self.print_colored(f"\n🧐 Анализирую: {args}", "blue")
        print()

        return {
            "action": "deep_analysis",
            "topic": args,
            "status": "initiated"
        }

    def handle_insight(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'инсайт'"""
        self.print_colored("\n💡 Генерация инсайтов", "magenta", bold=True)
        print()

        if not args:
            args = input("Тема для инсайтов: ").strip()

        self.print_colored(f"\n✨ Генерирую инсайты о: {args}", "magenta")
        print()

        return {
            "action": "generate_insights",
            "topic": args,
            "status": "initiated"
        }

    def handle_memory(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'память'"""
        self.print_colored("\n🧠 Смысловая память", "cyan", bold=True)
        print()

        options = {
            "всё": "show_all",
            "важное": "show_important",
            "недавнее": "show_recent",
            "поиск": "search",
            "статистика": "stats"
        }

        if not args:
            self.print_colored("Что показать?", "cyan")
            for key in options.keys():
                print(f"  • {key}")
            print()
            args = input("Выбери: ").strip().lower()

        action = options.get(args, "show_all")

        return {
            "action": "memory_view",
            "view_type": action,
            "status": "initiated"
        }

    def handle_reflection(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'рефлексия'"""
        self.print_colored("\n🤔 Рефлексия AI", "yellow", bold=True)
        print()

        self.print_colored("AI думает о своём мышлении...", "yellow")
        print()

        if not args:
            args = "последние решения"

        return {
            "action": "reflection",
            "focus": args,
            "status": "initiated"
        }

    def handle_partner(self, args: str) -> Dict[str, Any]:
        """Обработать команду 'партнёр'"""
        self.print_colored("\n🤝 Режим партнёра - совместное мышление", "magenta", bold=True)
        print()

        self.print_colored("Доступные режимы:", "magenta")
        modes = {
            "мозговой штурм": "brainstorming",
            "критик": "devils_advocate",
            "совместное творчество": "co_creation",
            "наставник": "mentoring"
        }

        for mode_name in modes.keys():
            print(f"  • {mode_name}")
        print()

        if not args:
            args = input("Выбери режим: ").strip().lower()

        mode = modes.get(args, "co_creation")

        self.print_colored(f"\n✨ Режим: {args}", "magenta")
        print()

        return {
            "action": "partner_mode",
            "mode": mode,
            "status": "initiated"
        }

    def handle_stats(self) -> Dict[str, Any]:
        """Обработать команду 'статистика'"""
        self.print_colored("\n📊 Статистика работы AI", "cyan", bold=True)
        print()

        # Время работы сессии
        uptime = datetime.now() - self.session_start
        hours = uptime.total_seconds() / 3600

        self.print_colored(f"⏱️  Время сессии: {hours:.1f} часов", "cyan")
        self.print_colored(f"🎯 Текущий режим: {self.current_mode}", "blue")
        print()

        return {
            "action": "show_stats",
            "uptime_hours": hours,
            "mode": self.current_mode,
            "status": "completed"
        }

    def run_command(self, command: str, args: str) -> Optional[Dict[str, Any]]:
        """
        Выполнить команду

        Returns:
            Результат команды или None для выхода
        """
        if command in ["выход", "quit", "exit"]:
            self.print_colored("\n👋 До встречи!", "green", bold=True)
            print()
            return None

        elif command in ["помощь", "help"]:
            self.show_help()
            return {"action": "help", "status": "completed"}

        elif command == "создай":
            return self.handle_create(args)

        elif command == "маркетинг":
            return self.handle_marketing(args)

        elif command == "анализ":
            return self.handle_analysis(args)

        elif command == "инсайт":
            return self.handle_insight(args)

        elif command == "память":
            return self.handle_memory(args)

        elif command == "рефлексия":
            return self.handle_reflection(args)

        elif command == "партнёр":
            return self.handle_partner(args)

        elif command == "статистика":
            return self.handle_stats()

        else:
            # Неизвестная команда - возможно, это обычный диалог
            return {
                "action": "dialogue",
                "message": f"{command} {args}".strip(),
                "status": "initiated"
            }

    def interactive_loop(self):
        """Интерактивный цикл"""
        self.show_banner()

        while True:
            try:
                # Промпт
                self.print_colored("AI> ", "green", bold=True)
                user_input = input().strip()

                if not user_input:
                    continue

                # Распознать команду
                command, args = self.parse_command(user_input)

                # Выполнить
                result = self.run_command(command, args)

                if result is None:
                    break

                # Показать результат (заглушка - реальный AI обработает)
                if result.get("status") == "initiated":
                    self.print_colored("✅ Команда принята! AI обрабатывает...", "green")
                    print()

            except KeyboardInterrupt:
                self.print_colored("\n\n👋 Прервано пользователем. До встречи!", "yellow")
                break
            except Exception as e:
                self.print_colored(f"\n❌ Ошибка: {e}", "red")
                print()


class QuickCommands:
    """
    Быстрые команды - ещё проще!

    Использование:
        from simple_interface import quick
        quick.create("telegram бот")
        quick.marketing("мой продукт")
    """

    def __init__(self):
        self.interface = SimpleInterface()

    def create(self, what: str):
        """Быстро создать проект"""
        return self.interface.handle_create(what)

    def marketing(self, description: str):
        """Быстро запустить маркетинг"""
        return self.interface.handle_marketing(description)

    def analyze(self, topic: str):
        """Быстро проанализировать"""
        return self.interface.handle_analysis(topic)

    def insight(self, topic: str):
        """Быстро сгенерировать инсайты"""
        return self.interface.handle_insight(topic)

    def memory(self, view: str = "всё"):
        """Быстро посмотреть память"""
        return self.interface.handle_memory(view)

    def reflect(self, focus: str = ""):
        """Быстро запустить рефлексию"""
        return self.interface.handle_reflection(focus)

    def partner(self, mode: str = "мозговой штурм"):
        """Быстро войти в режим партнёра"""
        return self.interface.handle_partner(mode)


# Глобальный экземпляр для быстрых команд
quick = QuickCommands()


# Пример использования
if __name__ == "__main__":
    print("🎯 Simple Interface - Простой интуитивный интерфейс\n")

    # Вариант 1: Интерактивный режим
    print("Запускаю интерактивный режим...\n")
    interface = SimpleInterface()

    # Показать примеры команд (не запускать цикл в тесте)
    print("Примеры команд:")
    print("  • создай telegram бот")
    print("  • маркетинг")
    print("  • анализ мой код")
    print("  • инсайт AI память")
    print("  • память важное")
    print("  • рефлексия")
    print("  • партнёр мозговой штурм")
    print("  • помощь")
    print()

    # Пример обработки команд
    test_commands = [
        "создай веб-сайт",
        "инсайт улучшение памяти",
        "статистика"
    ]

    for cmd in test_commands:
        print(f"\nКоманда: {cmd}")
        command, args = interface.parse_command(cmd)
        result = interface.run_command(command, args)
        print(f"Результат: {result}")

    print("\n✅ Интерфейс работает!")
    print("\nДля полноценной работы запустите:")
    print("  python simple_interface.py")
    print("  (и используйте интерактивный режим)")
