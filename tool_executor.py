"""
🛠️ Tool Executor - Инструменты для выполнения действий
Автор: ConsciousAI v3.0
Дата: 2025-11-15

Возможности:
- Работа с файловой системой
- Git операции
- Shell команды
- Веб-поиск и scraping
- API вызовы
- Выполнение кода
- Установка зависимостей
"""

import os
import subprocess
import shutil
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import urllib.request
import urllib.parse


class FileTools:
    """Инструменты для работы с файлами"""

    @staticmethod
    def create_file(path: str, content: str = "", encoding: str = "utf-8") -> Dict[str, Any]:
        """Создать файл"""
        try:
            # Создать директорию если не существует
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "path": path,
                "size": len(content),
                "message": f"File created: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def read_file(path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Прочитать файл"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                "success": True,
                "path": path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def append_to_file(path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Дописать в файл"""
        try:
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "path": path,
                "message": f"Content appended to {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def delete_file(path: str) -> Dict[str, Any]:
        """Удалить файл"""
        try:
            os.remove(path)
            return {
                "success": True,
                "path": path,
                "message": f"File deleted: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def create_directory(path: str) -> Dict[str, Any]:
        """Создать директорию"""
        try:
            os.makedirs(path, exist_ok=True)
            return {
                "success": True,
                "path": path,
                "message": f"Directory created: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def list_directory(path: str = ".") -> Dict[str, Any]:
        """Список файлов в директории"""
        try:
            items = os.listdir(path)
            files = [f for f in items if os.path.isfile(os.path.join(path, f))]
            dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]

            return {
                "success": True,
                "path": path,
                "files": files,
                "directories": dirs,
                "total": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def copy_file(src: str, dst: str) -> Dict[str, Any]:
        """Скопировать файл"""
        try:
            shutil.copy2(src, dst)
            return {
                "success": True,
                "source": src,
                "destination": dst,
                "message": f"File copied: {src} -> {dst}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def move_file(src: str, dst: str) -> Dict[str, Any]:
        """Переместить файл"""
        try:
            shutil.move(src, dst)
            return {
                "success": True,
                "source": src,
                "destination": dst,
                "message": f"File moved: {src} -> {dst}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class GitTools:
    """Инструменты для работы с Git"""

    @staticmethod
    def _run_git_command(args: List[str], cwd: str = ".") -> Dict[str, Any]:
        """Выполнить git команду"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def git_init(path: str = ".") -> Dict[str, Any]:
        """Инициализировать git репозиторий"""
        return GitTools._run_git_command(["init"], cwd=path)

    @staticmethod
    def git_clone(repo_url: str, destination: str) -> Dict[str, Any]:
        """Клонировать репозиторий"""
        return GitTools._run_git_command(["clone", repo_url, destination])

    @staticmethod
    def git_add(files: str = ".", cwd: str = ".") -> Dict[str, Any]:
        """Добавить файлы в staging"""
        return GitTools._run_git_command(["add", files], cwd=cwd)

    @staticmethod
    def git_commit(message: str, cwd: str = ".") -> Dict[str, Any]:
        """Создать коммит"""
        return GitTools._run_git_command(["commit", "-m", message], cwd=cwd)

    @staticmethod
    def git_push(remote: str = "origin", branch: str = "main", cwd: str = ".") -> Dict[str, Any]:
        """Запушить изменения"""
        return GitTools._run_git_command(["push", remote, branch], cwd=cwd)

    @staticmethod
    def git_pull(remote: str = "origin", branch: str = "main", cwd: str = ".") -> Dict[str, Any]:
        """Подтянуть изменения"""
        return GitTools._run_git_command(["pull", remote, branch], cwd=cwd)

    @staticmethod
    def git_status(cwd: str = ".") -> Dict[str, Any]:
        """Получить статус репозитория"""
        return GitTools._run_git_command(["status"], cwd=cwd)

    @staticmethod
    def git_log(n: int = 10, cwd: str = ".") -> Dict[str, Any]:
        """Получить лог коммитов"""
        return GitTools._run_git_command(["log", f"-{n}", "--oneline"], cwd=cwd)


class ShellTools:
    """Инструменты для выполнения shell команд"""

    DANGEROUS_COMMANDS = ['rm -rf /', 'dd', 'mkfs', 'format', ':(){:|:&};:']

    @staticmethod
    def run_command(command: str, cwd: str = ".", timeout: int = 60,
                   safe_mode: bool = True) -> Dict[str, Any]:
        """Выполнить shell команду"""
        # Проверка на опасные команды
        if safe_mode:
            for dangerous in ShellTools.DANGEROUS_COMMANDS:
                if dangerous in command:
                    return {
                        "success": False,
                        "error": f"Dangerous command blocked: {dangerous}"
                    }

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def install_package(package: str, package_manager: str = "pip") -> Dict[str, Any]:
        """Установить пакет"""
        commands = {
            "pip": f"pip install {package}",
            "npm": f"npm install {package}",
            "apt": f"sudo apt-get install -y {package}",
            "brew": f"brew install {package}"
        }

        command = commands.get(package_manager)
        if not command:
            return {
                "success": False,
                "error": f"Unknown package manager: {package_manager}"
            }

        return ShellTools.run_command(command)

    @staticmethod
    def run_python_script(script_path: str, args: str = "") -> Dict[str, Any]:
        """Запустить Python скрипт"""
        command = f"python {script_path} {args}"
        return ShellTools.run_command(command)

    @staticmethod
    def run_node_script(script_path: str, args: str = "") -> Dict[str, Any]:
        """Запустить Node.js скрипт"""
        command = f"node {script_path} {args}"
        return ShellTools.run_command(command)


class WebTools:
    """Инструменты для работы с веб"""

    @staticmethod
    def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
        """Поиск в интернете (простая имитация через DuckDuckGo)"""
        try:
            # Простой поиск через DuckDuckGo HTML
            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')

            # Простой парсинг (для продакшена лучше использовать BeautifulSoup)
            results = []
            import re
            links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"', html)

            for link in links[:num_results]:
                results.append({
                    "url": link,
                    "title": f"Result for: {query}"
                })

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def fetch_url(url: str, timeout: int = 10) -> Dict[str, Any]:
        """Получить содержимое URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8')

            return {
                "success": True,
                "url": url,
                "content": content,
                "size": len(content)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class CodeTools:
    """Инструменты для работы с кодом"""

    @staticmethod
    def run_python_code(code: str, timeout: int = 10) -> Dict[str, Any]:
        """Выполнить Python код"""
        try:
            # Создать временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Выполнить
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Удалить временный файл
            os.remove(temp_path)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def validate_python_syntax(code: str) -> Dict[str, Any]:
        """Проверить синтаксис Python кода"""
        try:
            compile(code, '<string>', 'exec')
            return {
                "success": True,
                "valid": True,
                "message": "Syntax is valid"
            }
        except SyntaxError as e:
            return {
                "success": True,
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "offset": e.offset
            }

    @staticmethod
    def format_python_code(code: str) -> Dict[str, Any]:
        """Форматировать Python код (используя autopep8 если доступен)"""
        try:
            import autopep8
            formatted = autopep8.fix_code(code)
            return {
                "success": True,
                "formatted_code": formatted
            }
        except ImportError:
            return {
                "success": False,
                "error": "autopep8 not installed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class APITools:
    """Инструменты для работы с API"""

    @staticmethod
    async def call_api(url: str, method: str = "GET", headers: Optional[Dict] = None,
                      data: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Вызов API"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                kwargs = {
                    "timeout": aiohttp.ClientTimeout(total=timeout)
                }

                if headers:
                    kwargs["headers"] = headers

                if data:
                    kwargs["json"] = data

                async with session.request(method, url, **kwargs) as response:
                    content = await response.text()

                    try:
                        json_data = json.loads(content)
                    except:
                        json_data = None

                    return {
                        "success": response.status < 400,
                        "status": response.status,
                        "content": content,
                        "json": json_data,
                        "headers": dict(response.headers)
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ProjectTools:
    """Инструменты для создания проектов"""

    @staticmethod
    def create_python_project(name: str, path: str = ".") -> Dict[str, Any]:
        """Создать структуру Python проекта"""
        try:
            project_path = os.path.join(path, name)
            os.makedirs(project_path, exist_ok=True)

            # Структура
            structure = {
                f"{name}/__init__.py": "",
                f"{name}/main.py": "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n",
                "tests/__init__.py": "",
                "tests/test_main.py": "import pytest\n\ndef test_example():\n    assert True\n",
                "requirements.txt": "pytest\n",
                "README.md": f"# {name}\n\nProject description here.\n",
                ".gitignore": "__pycache__/\n*.pyc\n.pytest_cache/\n",
            }

            for file_path, content in structure.items():
                full_path = os.path.join(project_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)

            return {
                "success": True,
                "project_path": project_path,
                "files_created": len(structure),
                "message": f"Python project '{name}' created"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def create_web_project(name: str, path: str = ".") -> Dict[str, Any]:
        """Создать структуру веб-проекта"""
        try:
            project_path = os.path.join(path, name)
            os.makedirs(project_path, exist_ok=True)

            # HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Welcome to {name}</h1>
    <script src="script.js"></script>
</body>
</html>"""

            # CSS
            css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    padding: 20px;
}

h1 {
    color: #333;
}"""

            # JS
            js_content = """console.log('Project loaded!');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM ready!');
});"""

            structure = {
                "index.html": html_content,
                "styles.css": css_content,
                "script.js": js_content,
                "README.md": f"# {name}\n\nWeb project\n",
            }

            for file_path, content in structure.items():
                full_path = os.path.join(project_path, file_path)
                with open(full_path, 'w') as f:
                    f.write(content)

            return {
                "success": True,
                "project_path": project_path,
                "files_created": len(structure),
                "message": f"Web project '{name}' created"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ToolExecutor:
    """Главный исполнитель инструментов"""

    def __init__(self):
        self.file_tools = FileTools()
        self.git_tools = GitTools()
        self.shell_tools = ShellTools()
        self.web_tools = WebTools()
        self.code_tools = CodeTools()
        self.api_tools = APITools()
        self.project_tools = ProjectTools()

    def get_all_tools(self) -> Dict[str, Any]:
        """Получить все доступные инструменты"""
        return {
            "file": {
                "create_file": self.file_tools.create_file,
                "read_file": self.file_tools.read_file,
                "append_to_file": self.file_tools.append_to_file,
                "delete_file": self.file_tools.delete_file,
                "create_directory": self.file_tools.create_directory,
                "list_directory": self.file_tools.list_directory,
                "copy_file": self.file_tools.copy_file,
                "move_file": self.file_tools.move_file,
            },
            "git": {
                "git_init": self.git_tools.git_init,
                "git_clone": self.git_tools.git_clone,
                "git_add": self.git_tools.git_add,
                "git_commit": self.git_tools.git_commit,
                "git_push": self.git_tools.git_push,
                "git_pull": self.git_tools.git_pull,
                "git_status": self.git_tools.git_status,
                "git_log": self.git_tools.git_log,
            },
            "shell": {
                "run_command": self.shell_tools.run_command,
                "install_package": self.shell_tools.install_package,
                "run_python_script": self.shell_tools.run_python_script,
                "run_node_script": self.shell_tools.run_node_script,
            },
            "web": {
                "search_web": self.web_tools.search_web,
                "fetch_url": self.web_tools.fetch_url,
            },
            "code": {
                "run_python_code": self.code_tools.run_python_code,
                "validate_python_syntax": self.code_tools.validate_python_syntax,
                "format_python_code": self.code_tools.format_python_code,
            },
            "api": {
                "call_api": self.api_tools.call_api,
            },
            "project": {
                "create_python_project": self.project_tools.create_python_project,
                "create_web_project": self.project_tools.create_web_project,
            }
        }


# === ДЕМО ===
if __name__ == "__main__":
    print("🛠️ Демо: Tool Executor")
    print("=" * 60)

    executor = ToolExecutor()

    # Тест файловых операций
    print("\n📁 Тест: Файловые операции")
    result = executor.file_tools.create_directory("./test_tools_demo")
    print(f"   {result}")

    result = executor.file_tools.create_file("./test_tools_demo/hello.txt", "Hello, World!")
    print(f"   {result}")

    result = executor.file_tools.read_file("./test_tools_demo/hello.txt")
    print(f"   Content: {result.get('content', 'N/A')}")

    # Тест создания проекта
    print("\n🌐 Тест: Создание веб-проекта")
    result = executor.project_tools.create_web_project("my_website", path="./test_tools_demo")
    print(f"   {result}")

    # Тест shell команды
    print("\n⚙️ Тест: Shell команда")
    result = executor.shell_tools.run_command("echo 'Hello from shell!'")
    print(f"   Output: {result.get('stdout', 'N/A').strip()}")

    # Тест Python кода
    print("\n🐍 Тест: Выполнение Python кода")
    code = "print('Hello from Python!')\nprint(2 + 2)"
    result = executor.code_tools.run_python_code(code)
    print(f"   Output: {result.get('stdout', 'N/A').strip()}")

    print("\n✅ Демо завершено!")
