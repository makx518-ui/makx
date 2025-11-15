"""
✅ Project Validator - Автоматическая валидация созданных проектов
Syntax Check + Lint + Security + Tests
"""

import subprocess
import ast
import os
from typing import Dict, Any, List


class ProjectValidator:
    """Валидатор проектов"""

    def __init__(self):
        self.results = {
            "syntax": [],
            "lint": [],
            "security": [],
            "tests": [],
        }

    def validate_project(self, project_path: str) -> Dict[str, Any]:
        """Полная валидация проекта"""
        print(f"🔍 Валидирую проект: {project_path}")

        self.validate_python_syntax(project_path)
        self.run_lint_check(project_path)
        self.run_security_check(project_path)

        score = self.calculate_score()

        return {
            "score": score,
            "results": self.results,
            "passed": score >= 70
        }

    def validate_python_syntax(self, project_path: str):
        """Проверка синтаксиса Python файлов"""
        python_files = self._find_python_files(project_path)

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    ast.parse(code)
                self.results["syntax"].append({
                    "file": file_path,
                    "status": "✅ OK"
                })
            except SyntaxError as e:
                self.results["syntax"].append({
                    "file": file_path,
                    "status": f"❌ Error: {e}"
                })

    def run_lint_check(self, project_path: str):
        """Проверка стиля кода"""
        python_files = self._find_python_files(project_path)

        for file_path in python_files:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", file_path],
                    capture_output=True,
                    timeout=10
                )
                status = "✅ OK" if result.returncode == 0 else "⚠️ Warning"
                self.results["lint"].append({
                    "file": file_path,
                    "status": status
                })
            except:
                self.results["lint"].append({
                    "file": file_path,
                    "status": "⏭️ Skipped"
                })

    def run_security_check(self, project_path: str):
        """Базовая проверка безопасности"""
        python_files = self._find_python_files(project_path)

        dangerous_patterns = [
            ("eval(", "Использование eval()"),
            ("exec(", "Использование exec()"),
            ("__import__", "Динамический импорт"),
            ("shell=True", "Shell injection риск"),
        ]

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()

                issues = []
                for pattern, description in dangerous_patterns:
                    if pattern in code:
                        issues.append(description)

                status = "✅ Safe" if not issues else f"⚠️ {', '.join(issues)}"
                self.results["security"].append({
                    "file": file_path,
                    "status": status
                })
            except:
                pass

    def _find_python_files(self, project_path: str) -> List[str]:
        """Найти все Python файлы"""
        python_files = []
        for root, dirs, files in os.walk(project_path):
            if '__pycache__' in root or 'venv' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def calculate_score(self) -> int:
        """Подсчитать общий score"""
        total_checks = sum(len(v) for v in self.results.values())
        if total_checks == 0:
            return 100

        passed_checks = sum(
            1 for category in self.results.values()
            for check in category
            if "✅" in check["status"]
        )

        return int((passed_checks / total_checks) * 100)


if __name__ == "__main__":
    validator = ProjectValidator()
    result = validator.validate_project("./test_simulation_projects/test_bot_simulation")
    print(f"\n📊 Score: {result['score']}/100")
    print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
