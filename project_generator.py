"""
🏗️ Project Generator - Генератор проектов под ключ
Автор: ConsciousAI v3.0
Дата: 2025-11-15

Возможности:
- Создание проектов любого типа (веб, игра, бот, API, и т.д.)
- Автогенерация кода
- Управление зависимостями
- Создание тестов
- Документация
- Конфигурация деплоя
- Docker контейнеризация
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class ProjectType(Enum):
    """Типы проектов"""
    WEB_STATIC = "web_static"
    WEB_REACT = "web_react"
    WEB_FLASK = "web_flask"
    WEB_FASTAPI = "web_fastapi"
    TELEGRAM_BOT = "telegram_bot"
    DISCORD_BOT = "discord_bot"
    REST_API = "rest_api"
    GAME_PYGAME = "game_pygame"
    CLI_TOOL = "cli_tool"
    ML_PROJECT = "ml_project"
    DATA_ANALYSIS = "data_analysis"
    MOBILE_FLUTTER = "mobile_flutter"
    DESKTOP_ELECTRON = "desktop_electron"


@dataclass
class ProjectConfig:
    """Конфигурация проекта"""
    name: str
    project_type: ProjectType
    description: str = ""
    features: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    include_tests: bool = True
    include_docs: bool = True
    include_docker: bool = True
    include_ci_cd: bool = True
    target_directory: str = "."


class TemplateGenerator:
    """Генератор шаблонов файлов"""

    @staticmethod
    def generate_python_main(project_name: str, project_type: ProjectType) -> str:
        """Генерация main.py"""
        templates = {
            ProjectType.WEB_FLASK: f'''"""
{project_name} - Flask Web Application
"""
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({{"status": "ok", "service": "{project_name}"}})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
''',

            ProjectType.WEB_FASTAPI: f'''"""
{project_name} - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="{project_name}", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name}"}}

@app.get("/health")
async def health():
    return {{"status": "ok"}}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
''',

            ProjectType.TELEGRAM_BOT: f'''"""
{project_name} - Telegram Bot
"""
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота (из переменных окружения)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TOKEN_HERE')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я {project_name}. Чем могу помочь?'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Доступные команды:\\n'
        '/start - Начать\\n'
        '/help - Помощь'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = f'Вы написали: {{text}}'
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Бот запущен...')
    app.run_polling()

if __name__ == '__main__':
    main()
''',

            ProjectType.CLI_TOOL: f'''"""
{project_name} - CLI Tool
"""
import click
import sys

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """{project_name} - Command Line Tool"""
    pass

@cli.command()
@click.argument('name')
def greet(name):
    """Greet someone"""
    click.echo(f'Hello, {{name}}!')

@cli.command()
@click.option('--count', default=1, help='Number of times')
@click.option('--message', default='Hello', help='Message to display')
def repeat(count, message):
    """Repeat a message"""
    for _ in range(count):
        click.echo(message)

if __name__ == '__main__':
    cli()
''',
        }

        return templates.get(project_type, f'"""\n{project_name}\n"""\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n')

    @staticmethod
    def generate_requirements_txt(project_type: ProjectType, features: List[str]) -> str:
        """Генерация requirements.txt"""
        base_deps = {
            ProjectType.WEB_FLASK: ["flask>=2.3.0", "python-dotenv>=1.0.0"],
            ProjectType.WEB_FASTAPI: ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0", "python-dotenv>=1.0.0"],
            ProjectType.TELEGRAM_BOT: ["python-telegram-bot>=20.0", "python-dotenv>=1.0.0"],
            ProjectType.DISCORD_BOT: ["discord.py>=2.3.0", "python-dotenv>=1.0.0"],
            ProjectType.CLI_TOOL: ["click>=8.1.0", "rich>=13.0.0"],
            ProjectType.ML_PROJECT: ["numpy>=1.24.0", "pandas>=2.0.0", "scikit-learn>=1.3.0", "matplotlib>=3.7.0"],
            ProjectType.DATA_ANALYSIS: ["numpy>=1.24.0", "pandas>=2.0.0", "matplotlib>=3.7.0", "jupyter>=1.0.0"],
        }

        deps = base_deps.get(project_type, ["python-dotenv>=1.0.0"])

        # Добавить тестовые зависимости
        deps.extend(["pytest>=7.4.0", "pytest-cov>=4.1.0"])

        return "\n".join(deps) + "\n"

    @staticmethod
    def generate_dockerfile(project_type: ProjectType, project_name: str) -> str:
        """Генерация Dockerfile"""
        return f'''FROM python:3.11-slim

WORKDIR /app

# Копировать зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копировать код
COPY . .

# Экспонировать порт (если веб-приложение)
EXPOSE 8000

# Запустить приложение
CMD ["python", "main.py"]
'''

    @staticmethod
    def generate_docker_compose(project_name: str) -> str:
        """Генерация docker-compose.yml"""
        return f'''version: '3.8'

services:
  app:
    build: .
    container_name: {project_name}
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    volumes:
      - .:/app
    restart: unless-stopped
'''

    @staticmethod
    def generate_gitignore() -> str:
        """Генерация .gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
docker-compose.override.yml
'''

    @staticmethod
    def generate_readme(config: ProjectConfig) -> str:
        """Генерация README.md"""
        features_section = ""
        if config.features:
            features_section = "\n## Возможности\n\n" + "\n".join([f"- {f}" for f in config.features])

        tech_section = ""
        if config.tech_stack:
            tech_section = "\n## Технологии\n\n" + "\n".join([f"- {t}" for t in config.tech_stack])

        return f'''# {config.name}

{config.description}
{features_section}
{tech_section}

## Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd {config.name}

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\\Scripts\\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

## Использование

```bash
python main.py
```

## Тестирование

```bash
pytest
```

## Docker

```bash
# Собрать образ
docker build -t {config.name} .

# Запустить
docker run -p 8000:8000 {config.name}

# Или использовать docker-compose
docker-compose up
```

## Разработка

Создано с помощью ConsciousAI v3.0 🤖

## Лицензия

MIT
'''

    @staticmethod
    def generate_test_file(project_name: str, project_type: ProjectType) -> str:
        """Генерация файла с тестами"""
        return f'''"""
Тесты для {project_name}
"""
import pytest

def test_example():
    """Пример теста"""
    assert True

def test_main_import():
    """Тест импорта main модуля"""
    try:
        import main
        assert True
    except ImportError:
        pytest.fail("Не удалось импортировать main модуль")

# Добавьте свои тесты здесь
'''

    @staticmethod
    def generate_env_example() -> str:
        """Генерация .env.example"""
        return '''# Environment Variables Template
# Copy this file to .env and fill in your values

# Application
APP_NAME=MyApp
DEBUG=True
PORT=8000

# Database (если используется)
DATABASE_URL=sqlite:///./database.db

# API Keys (если используются)
API_KEY=your_api_key_here

# Telegram Bot (если используется)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Discord Bot (если используется)
DISCORD_BOT_TOKEN=your_bot_token_here
'''


class ProjectGenerator:
    """Главный генератор проектов"""

    def __init__(self):
        self.template_generator = TemplateGenerator()

    async def generate_project(self, config: ProjectConfig) -> Dict[str, Any]:
        """Сгенерировать проект под ключ"""
        project_path = os.path.join(config.target_directory, config.name)

        print(f"🏗️ Создаю проект: {config.name}")
        print(f"   Тип: {config.project_type.value}")
        print(f"   Путь: {project_path}")

        try:
            # 1. Создать структуру директорий
            os.makedirs(project_path, exist_ok=True)

            # 2. Создать основные файлы
            files_created = []

            # main.py
            main_content = self.template_generator.generate_python_main(
                config.name,
                config.project_type
            )
            main_path = os.path.join(project_path, "main.py")
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
            files_created.append("main.py")

            # requirements.txt
            req_content = self.template_generator.generate_requirements_txt(
                config.project_type,
                config.features
            )
            req_path = os.path.join(project_path, "requirements.txt")
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(req_content)
            files_created.append("requirements.txt")

            # .gitignore
            gitignore_path = os.path.join(project_path, ".gitignore")
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(self.template_generator.generate_gitignore())
            files_created.append(".gitignore")

            # .env.example
            env_path = os.path.join(project_path, ".env.example")
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(self.template_generator.generate_env_example())
            files_created.append(".env.example")

            # 3. Создать тесты (если включено)
            if config.include_tests:
                tests_dir = os.path.join(project_path, "tests")
                os.makedirs(tests_dir, exist_ok=True)

                # __init__.py
                init_path = os.path.join(tests_dir, "__init__.py")
                with open(init_path, 'w') as f:
                    f.write("")

                # test_main.py
                test_content = self.template_generator.generate_test_file(
                    config.name,
                    config.project_type
                )
                test_path = os.path.join(tests_dir, "test_main.py")
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(test_content)
                files_created.append("tests/test_main.py")

            # 4. Создать документацию (если включено)
            if config.include_docs:
                readme_content = self.template_generator.generate_readme(config)
                readme_path = os.path.join(project_path, "README.md")
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                files_created.append("README.md")

            # 5. Создать Docker файлы (если включено)
            if config.include_docker:
                dockerfile_content = self.template_generator.generate_dockerfile(
                    config.project_type,
                    config.name
                )
                dockerfile_path = os.path.join(project_path, "Dockerfile")
                with open(dockerfile_path, 'w', encoding='utf-8') as f:
                    f.write(dockerfile_content)
                files_created.append("Dockerfile")

                compose_content = self.template_generator.generate_docker_compose(config.name)
                compose_path = os.path.join(project_path, "docker-compose.yml")
                with open(compose_path, 'w', encoding='utf-8') as f:
                    f.write(compose_content)
                files_created.append("docker-compose.yml")

            # 6. Создать CI/CD конфигурацию (если включено)
            if config.include_ci_cd:
                github_dir = os.path.join(project_path, ".github", "workflows")
                os.makedirs(github_dir, exist_ok=True)

                ci_content = self._generate_github_actions_ci(config.name)
                ci_path = os.path.join(github_dir, "ci.yml")
                with open(ci_path, 'w', encoding='utf-8') as f:
                    f.write(ci_content)
                files_created.append(".github/workflows/ci.yml")

            # 7. Создать дополнительные файлы в зависимости от типа проекта
            if config.project_type in [ProjectType.WEB_FLASK]:
                # Создать templates для Flask
                templates_dir = os.path.join(project_path, "templates")
                os.makedirs(templates_dir, exist_ok=True)

                index_html = self._generate_flask_index_html(config.name)
                index_path = os.path.join(templates_dir, "index.html")
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(index_html)
                files_created.append("templates/index.html")

                # Создать static
                static_dir = os.path.join(project_path, "static")
                os.makedirs(static_dir, exist_ok=True)

            print(f"\n✅ Проект создан успешно!")
            print(f"   Файлов создано: {len(files_created)}")
            for f in files_created:
                print(f"   - {f}")

            return {
                "success": True,
                "project_path": project_path,
                "files_created": files_created,
                "message": f"Project {config.name} created successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_github_actions_ci(self, project_name: str) -> str:
        """Генерация GitHub Actions CI"""
        return f'''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
'''

    def _generate_flask_index_html(self, project_name: str) -> str:
        """Генерация index.html для Flask"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: white;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {project_name}</h1>
        <p>Your application is running!</p>
        <p style="margin-top: 20px; opacity: 0.7;">Built with ConsciousAI v3.0</p>
    </div>
</body>
</html>
'''


# === ДЕМО ===
if __name__ == "__main__":
    print("🏗️ Демо: Project Generator")
    print("=" * 60)

    async def demo():
        generator = ProjectGenerator()

        # Пример 1: FastAPI проект
        config1 = ProjectConfig(
            name="my_api_service",
            project_type=ProjectType.WEB_FASTAPI,
            description="RESTful API сервис для обработки данных",
            features=[
                "REST API endpoints",
                "Автоматическая документация",
                "CORS поддержка",
                "Асинхронная обработка"
            ],
            tech_stack=["Python", "FastAPI", "Uvicorn"],
            include_tests=True,
            include_docs=True,
            include_docker=True,
            include_ci_cd=True,
            target_directory="./demo_projects"
        )

        print("\n📦 Создаю FastAPI проект...")
        result1 = await generator.generate_project(config1)
        print(json.dumps(result1, ensure_ascii=False, indent=2))

        # Пример 2: Telegram Bot
        config2 = ProjectConfig(
            name="my_telegram_bot",
            project_type=ProjectType.TELEGRAM_BOT,
            description="Telegram бот-помощник",
            features=[
                "Обработка команд",
                "Ответы на сообщения",
                "Модульная архитектура"
            ],
            tech_stack=["Python", "python-telegram-bot"],
            target_directory="./demo_projects"
        )

        print("\n🤖 Создаю Telegram Bot проект...")
        result2 = await generator.generate_project(config2)

    asyncio.run(demo())

    print("\n✅ Демо завершено!")
