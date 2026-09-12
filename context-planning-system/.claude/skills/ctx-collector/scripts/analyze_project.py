#!/usr/bin/env python3
"""
Project Context Analyzer for Context Planning System

Analyzes project structure, dependencies, and generates comprehensive context summary.
Integrates with existing ctx-* workflow.

Usage:
    python3 analyze_project.py <project_path> [--output PATH]

Example:
    python3 analyze_project.py projects/forgequant/nt-playground
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


class ProjectAnalyzer:
    """Analyzes project structure and generates context summary."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.name = project_path.name
        self.org = project_path.parent.name if project_path.parent.name != "projects" else None

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return structured data."""
        return {
            "name": self.name,
            "organization": self.org,
            "path": str(self.project_path),
            "analyzed_at": datetime.now().isoformat(),
            "overview": self._analyze_overview(),
            "structure": self._analyze_structure(),
            "stack": self._analyze_stack(),
            "entry_points": self._analyze_entry_points(),
            "specs": self._analyze_specs(),
            "tests": self._analyze_tests(),
            "documentation": self._analyze_docs(),
        }

    def _analyze_overview(self) -> Dict[str, Any]:
        """Extract project overview from README and pyproject.toml."""
        result = {}

        # Read README
        readme_files = list(self.project_path.glob("README.md"))
        if readme_files:
            with open(readme_files[0]) as f:
                lines = f.readlines()
                result["title"] = lines[0].strip("# \n") if lines else self.name
                # Extract first paragraph as description
                desc_lines = []
                for line in lines[1:]:
                    if line.strip() and not line.startswith("#"):
                        desc_lines.append(line.strip())
                    elif desc_lines:
                        break
                result["description"] = " ".join(desc_lines)

        # Read pyproject.toml for Python projects
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject) as f:
                content = f.read()
                # Simple extraction (not full TOML parser)
                for line in content.split("\n"):
                    if line.startswith("description"):
                        result["description"] = line.split("=")[1].strip(' "')
                        break

        # Read package.json for Node projects
        package_json = self.project_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                result["description"] = data.get("description", "")

        return result

    def _analyze_structure(self) -> Dict[str, List[str]]:
        """Analyze directory structure."""
        structure = defaultdict(list)

        for item in self.project_path.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_dir():
                structure["directories"].append(item.name)
            else:
                structure["root_files"].append(item.name)

        # Find key directories
        for key_dir in ["src", "app", "lib", "services", "strategies", "tests", "specs", ".specify"]:
            dir_path = self.project_path / key_dir
            if dir_path.exists():
                structure[f"{key_dir}_contents"] = [
                    f.relative_to(dir_path).as_posix()
                    for f in dir_path.rglob("*.py")
                    if not f.name.startswith("_") or f.name == "__init__.py"
                ][:20]  # Limit to 20 files

        return dict(structure)

    def _analyze_stack(self) -> Dict[str, Any]:
        """Detect technology stack."""
        stack = {
            "languages": [],
            "frameworks": [],
            "tools": []
        }

        # Python
        pyproject = self.project_path / "pyproject.toml"
        requirements = self.project_path / "requirements.txt"
        if pyproject.exists() or requirements.exists():
            stack["languages"].append("Python")

            # Extract dependencies from pyproject.toml
            if pyproject.exists():
                with open(pyproject) as f:
                    content = f.read()
                    deps = []
                    in_deps = False
                    for line in content.split("\n"):
                        if "dependencies" in line and "[" in line:
                            in_deps = True
                        elif in_deps:
                            if "]" in line:
                                break
                            if "=" in line or ">" in line or "<" in line:
                                dep = line.strip(' ",[]')
                                if dep:
                                    deps.append(dep.split(">=")[0].split("==")[0])
                    stack["frameworks"] = deps[:15]  # Top 15 deps

        # JavaScript/TypeScript
        package_json = self.project_path / "package.json"
        if package_json.exists():
            stack["languages"].append("JavaScript/TypeScript")
            with open(package_json) as f:
                data = json.load(f)
                deps = list(data.get("dependencies", {}).keys())[:10]
                stack["frameworks"].extend(deps)

        # Rust
        cargo_toml = self.project_path / "Cargo.toml"
        if cargo_toml.exists():
            stack["languages"].append("Rust")

        # Docker
        if (self.project_path / "Dockerfile").exists():
            stack["tools"].append("Docker")
        if (self.project_path / "docker-compose.yml").exists():
            stack["tools"].append("Docker Compose")

        return stack

    def _analyze_entry_points(self) -> List[Dict[str, str]]:
        """Find CLI entry points and main modules."""
        entry_points = []

        # Python CLI
        for cli_file in self.project_path.rglob("cli.py"):
            entry_points.append({
                "type": "Python CLI",
                "file": str(cli_file.relative_to(self.project_path))
            })

        # Main files
        for main_file in self.project_path.rglob("main.py"):
            entry_points.append({
                "type": "Python Main",
                "file": str(main_file.relative_to(self.project_path))
            })

        # __main__.py
        for main_file in self.project_path.rglob("__main__.py"):
            entry_points.append({
                "type": "Python Package Entry",
                "file": str(main_file.relative_to(self.project_path))
            })

        return entry_points

    def _analyze_specs(self) -> Dict[str, Any]:
        """Analyze Speckit specs and tasks."""
        specs = {
            "format": None,
            "files": [],
            "open_tasks_count": 0
        }

        # Check for .specify (Speckit)
        specify_dir = self.project_path / ".specify"
        if specify_dir.exists():
            specs["format"] = "Speckit (.specify)"
            specs["files"] = [
                str(f.relative_to(self.project_path))
                for f in specify_dir.rglob("*.md")
            ]

        # Check for specs/ (context-planning)
        specs_dir = self.project_path / "specs"
        if specs_dir.exists():
            if not specs["format"]:
                specs["format"] = "Context Planning (specs/)"
            specs["files"].extend([
                str(f.relative_to(self.project_path))
                for f in specs_dir.rglob("*.md")
            ])

        return specs

    def _analyze_tests(self) -> Dict[str, Any]:
        """Analyze test structure."""
        tests = {
            "framework": None,
            "test_files": [],
            "count": 0
        }

        tests_dir = self.project_path / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            tests["test_files"] = [
                str(f.relative_to(self.project_path))
                for f in test_files[:10]
            ]
            tests["count"] = len(test_files)

            # Detect framework
            if (self.project_path / "pytest.ini").exists() or "pytest" in str(self.project_path / "pyproject.toml"):
                tests["framework"] = "pytest"

        return tests

    def _analyze_docs(self) -> List[str]:
        """Find documentation files."""
        docs = []

        for pattern in ["*.md", "*.rst"]:
            for doc_file in self.project_path.rglob(pattern):
                # Skip test and spec files
                if "test" not in str(doc_file) and "spec" not in str(doc_file):
                    docs.append(str(doc_file.relative_to(self.project_path)))

        return docs[:20]  # Limit to 20

    def generate_report(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        lines = [
            f"# Project Context: {data['name']}",
            "",
            f"**Generated:** {data['analyzed_at']}",
            f"**Path:** `{data['path']}`",
            ""
        ]

        # Overview
        if data["overview"]:
            lines.extend([
                "## Overview",
                "",
                f"**Description:** {data['overview'].get('description', 'N/A')}",
                ""
            ])

        # Stack
        if data["stack"]:
            lines.extend(["## Technology Stack", ""])
            if data["stack"]["languages"]:
                lines.append(f"**Languages:** {', '.join(data['stack']['languages'])}")
            if data["stack"]["frameworks"]:
                lines.append(f"**Key Dependencies:** {', '.join(data['stack']['frameworks'][:5])}")
            if data["stack"]["tools"]:
                lines.append(f"**Tools:** {', '.join(data['stack']['tools'])}")
            lines.append("")

        # Structure
        if data["structure"]:
            lines.extend(["## Project Structure", ""])
            if "directories" in data["structure"]:
                lines.append("**Key Directories:**")
                for d in sorted(data["structure"]["directories"])[:10]:
                    lines.append(f"- `{d}/`")
            lines.append("")

        # Entry Points
        if data["entry_points"]:
            lines.extend(["## Entry Points", ""])
            for ep in data["entry_points"]:
                lines.append(f"- **{ep['type']}**: `{ep['file']}`")
            lines.append("")

        # Specs
        if data["specs"]["format"]:
            lines.extend([
                "## Specifications",
                "",
                f"**Format:** {data['specs']['format']}",
                f"**Spec Files:** {len(data['specs']['files'])}",
                ""
            ])

        # Tests
        if data["tests"]["count"] > 0:
            lines.extend([
                "## Tests",
                "",
                f"**Framework:** {data['tests']['framework']}",
                f"**Test Files:** {data['tests']['count']}",
                ""
            ])

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_project.py <project_path> [--output PATH]")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_path = Path(sys.argv[idx + 1])

    if not project_path.exists():
        print(f"Error: Project path not found: {project_path}")
        sys.exit(1)

    analyzer = ProjectAnalyzer(project_path)
    data = analyzer.analyze()
    report = analyzer.generate_report(data)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        print(f"✅ Report saved: {output_path}")
    else:
        print(report)

    # Also save JSON for programmatic access
    json_path = output_path.with_suffix(".json") if output_path else None
    if json_path:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ JSON data saved: {json_path}")


if __name__ == "__main__":
    main()
