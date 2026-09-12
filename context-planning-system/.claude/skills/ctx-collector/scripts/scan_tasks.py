#!/usr/bin/env python3
"""
Task Scanner for Context Planning System

Scans Speckit-format task files across multiple project repositories and
aggregates them into a unified backlog.yaml file for planning and tracking.

Usage:
    python3 scan_tasks.py [--output PATH] [--verbose]

Output:
    state/backlog.yaml (or custom path via --output)

Exit Codes:
    0: Success
    1: No projects found
    2: File I/O error
    3: Invalid task format
"""

import re
import sys
import os
import json
import datetime
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Iterator

# Default paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CTX_DIR = SKILL_DIR.parent.parent  # .../context
PROJECTS_DIR = CTX_DIR / "projects"
STATE_DIR = CTX_DIR / "state"

# Task parsing patterns
TASK_ID_PATTERN = re.compile(r"\bT(\d+)\b")
PRIORITY_PATTERN = re.compile(r"\b(P[123])\b")
PRIORITY_BRACKET_PATTERN = re.compile(r"\[P\]")  # Speckit format: [P] means P1
CHECKBOX_PATTERN = re.compile(r"^\s*-\s*\[(?P<mark>[ Xx])\]\s*(?P<title>.+)$")

class TaskScanner:
    """Scans and aggregates tasks from project repositories."""

    def __init__(self, projects_dir: Path, verbose: bool = False):
        self.projects_dir = projects_dir
        self.verbose = verbose
        self.stats = {
            "files_scanned": 0,
            "tasks_found": 0,
            "tasks_open": 0,
            "tasks_done": 0,
            "errors": []
        }

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}", file=sys.stderr)

    def iter_task_files(self) -> Iterator[Tuple[str, str, Path]]:
        """
        Discover task files in projects directory.

        Yields:
            (org, repo, file_path) tuples for each tasks.md file
        """
        if not self.projects_dir.exists():
            self.log(f"Projects directory not found: {self.projects_dir}", "ERROR")
            return

        for org_dir in self.projects_dir.iterdir():
            if not org_dir.is_dir() or org_dir.name.startswith("."):
                continue

            org = org_dir.name

            for repo_dir in org_dir.iterdir():
                if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                    continue

                repo = repo_dir.name

                # Support both formats: specs/ (context-planning) and .specify/ (Speckit)
                task_dirs = []
                specs_dir = repo_dir / "specs"
                specify_dir = repo_dir / ".specify"

                if specs_dir.exists():
                    task_dirs.append(specs_dir)
                if specify_dir.exists():
                    task_dirs.append(specify_dir)

                if not task_dirs:
                    self.log(f"No specs or .specify directory for {org}/{repo}", "DEBUG")
                    continue

                # Walk all task directories recursively
                for task_dir in task_dirs:
                    for root, dirs, files in os.walk(task_dir):
                        # Skip hidden directories except .specify
                        dirs[:] = [d for d in dirs if not d.startswith(".") or d == ".specify"]

                        for filename in files:
                            if filename.lower() == "tasks.md":
                                file_path = Path(root) / filename
                                yield org, repo, file_path

    @staticmethod
    def extract_priority(text: str) -> str:
        """
        Extract priority marker from text.
        Supports both P1/P2/P3 and [P] (Speckit format, where [P] = P1).

        Args:
            text: Text to search (task line or heading)

        Returns:
            Priority string (P1, P2, P3) or default P2
        """
        # Check for [P] first (Speckit format)
        if PRIORITY_BRACKET_PATTERN.search(text):
            return "P1"

        # Check for P1/P2/P3
        match = PRIORITY_PATTERN.search(text)
        return match.group(1) if match else "P2"

    @staticmethod
    def extract_task_id(text: str) -> Optional[str]:
        """
        Extract task ID from text.

        Args:
            text: Text to search for T### pattern

        Returns:
            Task ID (e.g., "T101") or None
        """
        match = TASK_ID_PATTERN.search(text)
        return f"T{match.group(1)}" if match else None

    @staticmethod
    def build_scope(headings: List[str]) -> Dict[str, str]:
        """
        Build scope context from heading stack.

        Args:
            headings: Stack of current heading levels

        Returns:
            Dict with section/subsection keys
        """
        if not headings:
            return {}
        if len(headings) == 1:
            return {"section": headings[-1]}
        return {
            "section": headings[-2],
            "subsection": headings[-1]
        }

    def parse_task_file(
        self,
        org: str,
        repo: str,
        file_path: Path
    ) -> List[Dict]:
        """
        Parse a single task file and extract tasks.

        Args:
            org: Organization/owner name
            repo: Repository name
            file_path: Path to tasks.md file

        Returns:
            List of task dictionaries
        """
        tasks = []

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            self.log(f"Encoding error in {file_path}", "ERROR")
            self.stats["errors"].append(f"Encoding error: {file_path}")
            return tasks
        except Exception as e:
            self.log(f"Failed to read {file_path}: {e}", "ERROR")
            self.stats["errors"].append(f"Read error: {file_path}: {e}")
            return tasks

        self.stats["files_scanned"] += 1
        headings = []

        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.rstrip("\n")

            # Track heading hierarchy
            if line_stripped.startswith("#"):
                level = len(line_stripped) - len(line_stripped.lstrip("#"))
                title = line_stripped[level:].strip()
                # Update heading stack up to current level
                headings = headings[:level-1] + [title]
                continue

            # Parse checkbox tasks
            match = CHECKBOX_PATTERN.match(line_stripped)
            if not match:
                continue

            # Extract task details
            status = "done" if match.group("mark").strip().lower() == "x" else "open"
            title = match.group("title").strip()
            task_id = self.extract_task_id(title)

            # Priority from task line or nearest heading
            priority = self.extract_priority(title)
            if priority == "P2":  # Default, check headings
                priority = self.extract_priority(" ".join(headings))

            # Generate unique identifier
            uid_source = f"{org}/{repo}#{task_id or file_path}:{line_num}:{title}"
            if task_id:
                uid = f"{org}/{repo}#{task_id}"
            else:
                hash_suffix = hashlib.md5(uid_source.encode()).hexdigest()[:8]
                uid = f"{org}/{repo}#{hash_suffix}"

            # Build task object
            task = {
                "uid": uid,
                "project": f"{org}/{repo}",
                "file": str(file_path.relative_to(CTX_DIR)),
                "line": line_num,
                "id": task_id,
                "title": title,
                "priority": priority,
                "status": status,
                "scope": self.build_scope(headings)
            }

            tasks.append(task)
            self.stats["tasks_found"] += 1
            if status == "open":
                self.stats["tasks_open"] += 1
            else:
                self.stats["tasks_done"] += 1

        return tasks

    def scan_all(self) -> List[Dict]:
        """
        Scan all task files and aggregate results.

        Returns:
            List of all discovered tasks
        """
        all_tasks = []

        for org, repo, file_path in self.iter_task_files():
            self.log(f"Scanning {org}/{repo}: {file_path.name}")
            tasks = self.parse_task_file(org, repo, file_path)
            all_tasks.extend(tasks)

        return all_tasks

    def write_backlog(
        self,
        tasks: List[Dict],
        output_path: Path
    ) -> None:
        """
        Write aggregated tasks to backlog file.

        Args:
            tasks: List of task dictionaries
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        backlog = {
            "generated_at": datetime.datetime.now().astimezone().isoformat(),
            "items": tasks
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                try:
                    import yaml
                    yaml.safe_dump(
                        backlog,
                        f,
                        allow_unicode=True,
                        sort_keys=False,
                        default_flow_style=False
                    )
                    self.log(f"Wrote backlog to {output_path} (YAML format)")
                except ImportError:
                    # Fallback to JSON if YAML library not available
                    json.dump(backlog, f, ensure_ascii=False, indent=2)
                    self.log(
                        f"Wrote backlog to {output_path} (JSON format - install PyYAML for YAML)",
                        "WARN"
                    )
        except Exception as e:
            self.log(f"Failed to write {output_path}: {e}", "ERROR")
            raise

    def print_summary(self) -> None:
        """Print scan summary statistics."""
        print("\n=== Scan Summary ===")
        print(f"Files scanned: {self.stats['files_scanned']}")
        print(f"Tasks found: {self.stats['tasks_found']}")
        print(f"  Open: {self.stats['tasks_open']}")
        print(f"  Done: {self.stats['tasks_done']}")

        if self.stats["errors"]:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"  - {error}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scan Speckit task files and generate backlog"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=STATE_DIR / "backlog.yaml",
        help="Output file path (default: state/backlog.yaml)"
    )
    parser.add_argument(
        "--projects",
        type=Path,
        default=PROJECTS_DIR,
        help="Projects directory path (default: projects/)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Initialize scanner
    scanner = TaskScanner(args.projects, verbose=args.verbose)

    # Check if projects directory exists
    if not args.projects.exists():
        print(f"Error: Projects directory not found: {args.projects}", file=sys.stderr)
        return 1

    # Scan all task files
    scanner.log("Starting task scan...")
    tasks = scanner.scan_all()

    if scanner.stats["files_scanned"] == 0:
        print("Warning: No task files found in projects directory", file=sys.stderr)
        return 1

    # Write backlog
    try:
        scanner.write_backlog(tasks, args.output)
    except Exception as e:
        print(f"Error: Failed to write backlog: {e}", file=sys.stderr)
        return 2

    # Print summary
    scanner.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
