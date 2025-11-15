"""
🤖 Agent Framework - Автономный агент для выполнения сложных задач
Автор: ConsciousAI v3.0
Дата: 2025-11-15

Возможности:
- Автоматическое планирование задач
- Разбивка на подзадачи
- Выполнение через инструменты (tools)
- Self-correction (проверка и исправление ошибок)
- Прогресс-трекинг
- Адаптивное обучение
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import traceback


class TaskStatus(Enum):
    """Статусы задачи"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Приоритеты задач"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    OPTIONAL = 1


@dataclass
class Task:
    """Задача для выполнения"""
    task_id: str
    description: str
    action: str  # Тип действия: 'create_file', 'run_code', 'web_search', etc.
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)  # ID задач, от которых зависит
    parent_task_id: Optional[str] = None
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data


@dataclass
class ExecutionPlan:
    """План выполнения задачи"""
    goal: str
    tasks: List[Task] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def get_executable_tasks(self) -> List[Task]:
        """Получить задачи, готовые к выполнению (без невыполненных зависимостей)"""
        executable = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # Проверить зависимости
            deps_satisfied = all(
                any(t.task_id == dep_id and t.status == TaskStatus.COMPLETED
                    for t in self.tasks)
                for dep_id in task.dependencies
            )

            if deps_satisfied:
                executable.append(task)

        return executable

    def get_progress(self) -> Dict[str, Any]:
        """Получить прогресс выполнения"""
        total = len(self.tasks)
        if total == 0:
            return {"percent": 0, "completed": 0, "total": 0}

        completed = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.tasks if t.status == TaskStatus.FAILED])
        in_progress = len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS])

        return {
            "percent": (completed / total) * 100,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "total": total
        }


class TaskPlanner:
    """Планировщик задач"""

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider

    async def create_plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """Создать план выполнения для цели"""
        plan = ExecutionPlan(goal=goal, metadata=context or {})

        # Если есть LLM - использовать его для планирования
        if self.llm_provider:
            tasks = await self._llm_based_planning(goal, context)
        else:
            tasks = self._rule_based_planning(goal, context)

        for task in tasks:
            plan.add_task(task)

        return plan

    async def _llm_based_planning(self, goal: str, context: Optional[Dict[str, Any]]) -> List[Task]:
        """Планирование с помощью LLM"""
        prompt = f"""Ты - планировщик задач. Разбей цель на конкретные выполнимые шаги.

Цель: {goal}

Контекст: {json.dumps(context or {}, ensure_ascii=False, indent=2)}

Создай список задач в формате JSON:
[
  {{
    "task_id": "task_001",
    "description": "Описание шага",
    "action": "тип действия (create_file, run_code, web_search, etc)",
    "params": {{"параметры": "значения"}},
    "priority": "MEDIUM",
    "dependencies": []
  }},
  ...
]

Требования:
- Задачи должны быть конкретными и выполнимыми
- Указывай зависимости между задачами
- Сортируй по логическому порядку выполнения
"""

        try:
            response = await self.llm_provider.generate(prompt)
            tasks_data = json.loads(response)

            tasks = []
            for task_data in tasks_data:
                task = Task(
                    task_id=task_data['task_id'],
                    description=task_data['description'],
                    action=task_data['action'],
                    params=task_data.get('params', {}),
                    priority=TaskPriority[task_data.get('priority', 'MEDIUM')],
                    dependencies=task_data.get('dependencies', [])
                )
                tasks.append(task)

            return tasks

        except Exception as e:
            print(f"⚠️ LLM planning failed: {e}, falling back to rule-based")
            return self._rule_based_planning(goal, context)

    def _rule_based_planning(self, goal: str, context: Optional[Dict[str, Any]]) -> List[Task]:
        """Планирование на основе правил (fallback)"""
        tasks = []

        # Анализ цели
        goal_lower = goal.lower()

        # Проект веб-сайта
        if any(keyword in goal_lower for keyword in ['сайт', 'website', 'веб']):
            tasks = [
                Task("task_001", "Создать структуру проекта", "create_directory",
                     {"path": "./website_project"}, priority=TaskPriority.HIGH),
                Task("task_002", "Создать HTML файл", "create_file",
                     {"path": "./website_project/index.html", "content": "<!DOCTYPE html>..."},
                     dependencies=["task_001"]),
                Task("task_003", "Создать CSS стили", "create_file",
                     {"path": "./website_project/styles.css"},
                     dependencies=["task_001"]),
                Task("task_004", "Создать JavaScript", "create_file",
                     {"path": "./website_project/script.js"},
                     dependencies=["task_001"]),
            ]

        # Проект игры
        elif any(keyword in goal_lower for keyword in ['игр', 'game']):
            tasks = [
                Task("task_001", "Создать проект игры", "create_directory",
                     {"path": "./game_project"}, priority=TaskPriority.HIGH),
                Task("task_002", "Создать игровой движок", "create_file",
                     {"path": "./game_project/game.py"},
                     dependencies=["task_001"]),
                Task("task_003", "Создать ресурсы", "create_directory",
                     {"path": "./game_project/assets"},
                     dependencies=["task_001"]),
            ]

        # Бот
        elif any(keyword in goal_lower for keyword in ['бот', 'bot']):
            tasks = [
                Task("task_001", "Создать проект бота", "create_directory",
                     {"path": "./bot_project"}, priority=TaskPriority.HIGH),
                Task("task_002", "Создать основной файл бота", "create_file",
                     {"path": "./bot_project/bot.py"},
                     dependencies=["task_001"]),
                Task("task_003", "Создать конфигурацию", "create_file",
                     {"path": "./bot_project/config.json"},
                     dependencies=["task_001"]),
            ]

        # Общий случай
        else:
            tasks = [
                Task("task_001", f"Проанализировать требования: {goal}", "analyze",
                     {"goal": goal}, priority=TaskPriority.CRITICAL),
                Task("task_002", "Создать базовую структуру", "create_structure",
                     {}, dependencies=["task_001"]),
                Task("task_003", "Реализовать основной функционал", "implement",
                     {}, dependencies=["task_002"]),
                Task("task_004", "Тестирование", "test",
                     {}, dependencies=["task_003"]),
            ]

        return tasks

    async def refine_plan(self, plan: ExecutionPlan, feedback: str) -> ExecutionPlan:
        """Уточнить план на основе обратной связи"""
        # Можно использовать LLM для адаптации плана
        return plan


class ToolRegistry:
    """Реестр инструментов (tools)"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, action: str, handler: Callable):
        """Зарегистрировать инструмент"""
        self.tools[action] = handler

    def get(self, action: str) -> Optional[Callable]:
        """Получить инструмент"""
        return self.tools.get(action)

    def list_tools(self) -> List[str]:
        """Список доступных инструментов"""
        return list(self.tools.keys())


class SelfCorrectionSystem:
    """Система самопроверки и исправления ошибок"""

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider

    async def verify_result(self, task: Task) -> Tuple[bool, Optional[str]]:
        """Проверить результат выполнения задачи"""
        # Базовые проверки
        if task.status == TaskStatus.FAILED:
            return False, task.error

        if task.result is None and task.action not in ['delete', 'cleanup']:
            return False, "No result produced"

        # Специфичные проверки для разных типов задач
        if task.action == 'create_file':
            # Проверить, что файл создан
            import os
            if 'path' in task.params:
                if not os.path.exists(task.params['path']):
                    return False, f"File {task.params['path']} was not created"

        elif task.action == 'run_code':
            # Проверить код на ошибки
            if task.result and 'error' in str(task.result).lower():
                return False, "Code execution produced errors"

        # LLM-based verification
        if self.llm_provider:
            is_valid = await self._llm_verify(task)
            if not is_valid:
                return False, "LLM verification failed"

        return True, None

    async def _llm_verify(self, task: Task) -> bool:
        """Проверка через LLM"""
        prompt = f"""Проверь, корректно ли выполнена задача:

Задача: {task.description}
Действие: {task.action}
Результат: {task.result}

Ответь 'YES' если всё корректно, или 'NO' если есть проблемы."""

        try:
            response = await self.llm_provider.generate(prompt)
            return 'YES' in response.upper()
        except:
            return True  # По умолчанию считаем валидным

    async def suggest_fix(self, task: Task) -> Optional[Task]:
        """Предложить исправление для неудавшейся задачи"""
        if not self.llm_provider:
            return None

        prompt = f"""Задача провалилась. Предложи исправленную версию.

Оригинальная задача:
{json.dumps(task.to_dict(), ensure_ascii=False, indent=2)}

Ошибка: {task.error}

Создай исправленную задачу в формате JSON."""

        try:
            response = await self.llm_provider.generate(prompt)
            fixed_data = json.loads(response)

            fixed_task = Task(
                task_id=f"{task.task_id}_retry_{task.retry_count + 1}",
                description=fixed_data['description'],
                action=fixed_data['action'],
                params=fixed_data.get('params', {}),
                parent_task_id=task.task_id
            )
            return fixed_task

        except Exception as e:
            print(f"⚠️ Could not suggest fix: {e}")
            return None


class AutonomousAgent:
    """Автономный агент"""

    def __init__(self, tool_registry: ToolRegistry,
                 task_planner: Optional[TaskPlanner] = None,
                 self_correction: Optional[SelfCorrectionSystem] = None):
        self.tool_registry = tool_registry
        self.task_planner = task_planner or TaskPlanner()
        self.self_correction = self_correction or SelfCorrectionSystem()
        self.current_plan: Optional[ExecutionPlan] = None
        self.execution_log: List[Dict[str, Any]] = []

    async def execute_goal(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполнить цель автономно"""
        print(f"🎯 Цель: {goal}")

        # 1. Создать план
        print("📋 Создаю план...")
        self.current_plan = await self.task_planner.create_plan(goal, context)
        print(f"   Создано задач: {len(self.current_plan.tasks)}")

        # 2. Выполнить задачи
        while True:
            executable = self.current_plan.get_executable_tasks()

            if not executable:
                # Проверить, остались ли невыполненные задачи
                pending = self.current_plan.get_pending_tasks()
                if pending:
                    print(f"⚠️ Заблокированные задачи: {len(pending)}")
                    # Попробовать разблокировать
                    for task in pending:
                        task.status = TaskStatus.PENDING
                        task.dependencies = []  # Убрать зависимости
                    continue
                else:
                    break

            # Выполнить доступные задачи
            for task in executable:
                await self._execute_task(task)

            # Показать прогресс
            progress = self.current_plan.get_progress()
            print(f"   Прогресс: {progress['percent']:.1f}% ({progress['completed']}/{progress['total']})")

        # 3. Итоговый отчёт
        return self._generate_report()

    async def _execute_task(self, task: Task):
        """Выполнить одну задачу"""
        print(f"\n🔧 Выполняю: {task.description}")
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().timestamp()

        try:
            # Получить инструмент
            tool = self.tool_registry.get(task.action)
            if not tool:
                raise ValueError(f"Unknown action: {task.action}")

            # Выполнить
            result = await tool(**task.params) if asyncio.iscoroutinefunction(tool) else tool(**task.params)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().timestamp()

            print(f"   ✅ Выполнено!")

            # Проверка результата
            is_valid, error_msg = await self.self_correction.verify_result(task)
            if not is_valid:
                print(f"   ⚠️ Проверка не пройдена: {error_msg}")
                task.status = TaskStatus.FAILED
                task.error = error_msg

                # Попробовать исправить
                if task.retry_count < task.max_retries:
                    fixed_task = await self.self_correction.suggest_fix(task)
                    if fixed_task:
                        self.current_plan.add_task(fixed_task)
                        print(f"   🔄 Создана задача для повтора")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().timestamp()
            print(f"   ❌ Ошибка: {e}")

            # Лог ошибки
            self.execution_log.append({
                "task_id": task.task_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            })

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                print(f"   🔄 Повтор {task.retry_count}/{task.max_retries}")

    def _generate_report(self) -> Dict[str, Any]:
        """Сгенерировать отчёт о выполнении"""
        if not self.current_plan:
            return {}

        progress = self.current_plan.get_progress()
        completed_tasks = [t for t in self.current_plan.tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in self.current_plan.tasks if t.status == TaskStatus.FAILED]

        return {
            "goal": self.current_plan.goal,
            "progress": progress,
            "completed_tasks": [t.to_dict() for t in completed_tasks],
            "failed_tasks": [t.to_dict() for t in failed_tasks],
            "execution_log": self.execution_log,
            "total_time": sum(
                (t.completed_at or t.started_at or 0) - t.started_at
                for t in self.current_plan.tasks
                if t.started_at
            )
        }

    def get_current_progress(self) -> Optional[Dict[str, Any]]:
        """Получить текущий прогресс"""
        if not self.current_plan:
            return None
        return self.current_plan.get_progress()


# === ДЕМО ===
if __name__ == "__main__":
    print("🤖 Демо: Autonomous Agent")
    print("=" * 60)

    # Создать реестр инструментов
    registry = ToolRegistry()

    # Зарегистрировать базовые инструменты
    def create_directory(path: str):
        import os
        os.makedirs(path, exist_ok=True)
        return f"Created: {path}"

    def create_file(path: str, content: str = ""):
        with open(path, 'w') as f:
            f.write(content)
        return f"Created file: {path}"

    def analyze(goal: str):
        return f"Analyzed goal: {goal}"

    registry.register("create_directory", create_directory)
    registry.register("create_file", create_file)
    registry.register("analyze", analyze)
    registry.register("create_structure", lambda: "Structure created")
    registry.register("implement", lambda: "Implementation done")
    registry.register("test", lambda: "Tests passed")

    # Создать агента
    planner = TaskPlanner()
    correction = SelfCorrectionSystem()
    agent = AutonomousAgent(registry, planner, correction)

    # Выполнить цель
    async def demo():
        report = await agent.execute_goal(
            "Создать простой веб-сайт для стартапа",
            context={"theme": "eco-products", "pages": ["home", "about", "contact"]}
        )

        print("\n" + "=" * 60)
        print("📊 ОТЧЁТ:")
        print(json.dumps(report, ensure_ascii=False, indent=2))

    asyncio.run(demo())
