#!/usr/bin/env python3
"""Verify workshop structure, checkpoints, documentation, and agent assets."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Stage:
    name: str
    passed: int
    required: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    intentional_red: bool = False


STAGES = (
    Stage("Foundations-start", 5),
    Stage("Repository-Orientation-start", 5, forbidden=("REPOSITORY_MAP.md",)),
    Stage(
        "Planning-Tests-start",
        5,
        required=("REPOSITORY_MAP.md",),
        forbidden=("FEATURE_PLAN.md", "tests/test_owner_filter.py"),
    ),
    Stage(
        "Implementation-start",
        5,
        required=("REPOSITORY_MAP.md", "FEATURE_PLAN.md", "tests/test_owner_filter.py"),
        intentional_red=True,
    ),
    Stage(
        "Debugging-Extension-start",
        11,
        required=("REPOSITORY_MAP.md", "FEATURE_PLAN.md", "tests/test_owner_filter.py"),
        forbidden=("tests/test_debug_owner_choices.py", "tests/test_filter_context.py"),
    ),
    Stage(
        "Review-Refactor-start",
        16,
        required=(
            "REPOSITORY_MAP.md",
            "FEATURE_PLAN.md",
            "tests/test_owner_filter.py",
            "tests/test_debug_owner_choices.py",
            "tests/test_filter_context.py",
        ),
        forbidden=("REVIEW_NOTES.md", "REFACTOR_NOTES.md", "tests/test_note_filter_context.py"),
    ),
    Stage(
        "Handoff-start",
        20,
        required=(
            "REPOSITORY_MAP.md",
            "FEATURE_PLAN.md",
            "REVIEW_NOTES.md",
            "REFACTOR_NOTES.md",
            "tests/test_owner_filter.py",
            "tests/test_debug_owner_choices.py",
            "tests/test_filter_context.py",
            "tests/test_note_filter_context.py",
        ),
        forbidden=("TEAM_HANDOFF.md", "CAPSTONE_EVIDENCE.md"),
    ),
)

SKILLS = (
    "orient-repository-with-codex",
    "turn-story-into-tested-plan",
    "design-intentional-red-tests",
    "implement-focused-slice",
    "debug-from-evidence",
    "review-generated-code",
    "refactor-with-guardrails",
    "verify-workshop-checkpoint",
    "prepare-developer-handoff",
)

CUSTOM_AGENTS = (
    "checkpoint_auditor",
    "security_reviewer",
)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def result_text(result: subprocess.CompletedProcess[str]) -> str:
    return f"{result.stdout}\n{result.stderr}".strip()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_structure(errors: list[str]) -> None:
    actual_stages = sorted(path.name for path in ROOT.glob("*-start") if path.is_dir())
    expected_stages = sorted(stage.name for stage in STAGES)
    require(actual_stages == expected_stages, f"stage set differs: {actual_stages}", errors)

    for stage in STAGES:
        stage_path = ROOT / stage.name
        require((stage_path / "pyproject.toml").is_file(), f"{stage.name}: missing pyproject.toml", errors)
        require((stage_path / "app").is_dir(), f"{stage.name}: missing app/", errors)
        require((stage_path / "tests").is_dir(), f"{stage.name}: missing tests/", errors)
        for relative in stage.required:
            require((stage_path / relative).exists(), f"{stage.name}: missing {relative}", errors)
        for relative in stage.forbidden:
            require(not (stage_path / relative).exists(), f"{stage.name}: unexpected {relative}", errors)
        require(not (stage_path / ".git").exists(), f"{stage.name}: nested .git repository found", errors)

    manifests = [(ROOT / stage.name / "pyproject.toml").read_bytes() for stage in STAGES]
    require(len(set(manifests)) == 1, "stage pyproject.toml files have drifted", errors)
    seeds = [(ROOT / stage.name / "data/seed_tasks.json").read_bytes() for stage in STAGES]
    require(len(set(seeds)) == 1, "stage seed_tasks.json files have drifted", errors)

    root_requirements = sorted(path.name for path in ROOT.glob("requirements*.txt"))
    require(root_requirements == ["requirements.txt"], f"expected one requirements.txt; found {root_requirements}", errors)
    require((ROOT / "AGENTS.md").is_file(), "missing root AGENTS.md", errors)
    require((ROOT / "STUDENT_SETUP.md").is_file(), "missing student pre-work setup guide", errors)
    require((ROOT / ".agents/evals/scenario-matrix.md").is_file(), "missing agent scenario matrix", errors)
    require((ROOT / ".agents/evals/cases.json").is_file(), "missing agent evaluation cases", errors)
    require((ROOT / ".codex/config.toml").is_file(), "missing project Codex config", errors)

    try:
        codex_config = tomllib.loads((ROOT / ".codex/config.toml").read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        errors.append(f"project Codex config is invalid: {exc}")
        codex_config = {}
    agent_config = codex_config.get("agents", {})
    require(agent_config.get("enabled") is True, "project Codex config must enable agents", errors)
    require(
        agent_config.get("max_concurrent_threads_per_session", 0) >= 2,
        "project Codex config must allow at least two specialist threads",
        errors,
    )

    agent_dir = ROOT / ".codex/agents"
    actual_agent_files = sorted(path.stem for path in agent_dir.glob("*.toml"))
    require(
        actual_agent_files == sorted(CUSTOM_AGENTS),
        f"custom agent set differs: {actual_agent_files}",
        errors,
    )
    for agent_name in CUSTOM_AGENTS:
        agent_file = agent_dir / f"{agent_name}.toml"
        try:
            agent_data = tomllib.loads(agent_file.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError) as exc:
            errors.append(f"{agent_name}: invalid custom agent file: {exc}")
            continue
        require(agent_data.get("name") == agent_name, f"{agent_name}: name mismatch", errors)
        require(bool(agent_data.get("description")), f"{agent_name}: missing description", errors)
        instructions = agent_data.get("developer_instructions", "")
        require(bool(instructions), f"{agent_name}: missing developer_instructions", errors)
        require("Do not edit files" in instructions, f"{agent_name}: must prohibit edits", errors)
        require("active stage" in instructions, f"{agent_name}: must enforce active-stage scope", errors)

    scenario_matrix = (ROOT / ".agents/evals/scenario-matrix.md").read_text(encoding="utf-8")
    try:
        eval_cases = json.loads((ROOT / ".agents/evals/cases.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"agent evaluation cases are invalid: {exc}")
        eval_cases = []
    case_skills = {case.get("skill") for case in eval_cases if isinstance(case, dict)}
    case_agents = {case.get("agent") for case in eval_cases if isinstance(case, dict)}
    require(len(eval_cases) >= 12, "agent evaluation suite must contain at least twelve cases", errors)
    for skill in SKILLS:
        skill_path = ROOT / ".agents/skills" / skill
        skill_file = skill_path / "SKILL.md"
        metadata_file = skill_path / "agents/openai.yaml"
        require(skill_file.is_file(), f"{skill}: missing SKILL.md", errors)
        require(metadata_file.is_file(), f"{skill}: missing agents/openai.yaml", errors)
        if skill_file.is_file():
            content = skill_file.read_text(encoding="utf-8")
            require(f"name: {skill}" in content, f"{skill}: frontmatter name mismatch", errors)
            require("description:" in content, f"{skill}: missing description", errors)
            require("TODO" not in content, f"{skill}: unresolved TODO", errors)
            require(len(content.splitlines()) <= 500, f"{skill}: SKILL.md exceeds 500 lines", errors)
            referenced_assets = re.findall(r"`((?:references|scripts)/[^` ]+)`", content)
            for relative in referenced_assets:
                require((skill_path / relative).is_file(), f"{skill}: missing referenced {relative}", errors)
        if metadata_file.is_file():
            metadata = metadata_file.read_text(encoding="utf-8")
            require(f"${skill}" in metadata, f"{skill}: default prompt must name ${skill}", errors)
        require(f"${skill}" in scenario_matrix, f"{skill}: missing evaluation scenario", errors)
        require(skill in case_skills, f"{skill}: missing concrete evaluation case", errors)
    for agent_name in CUSTOM_AGENTS:
        require(agent_name in scenario_matrix, f"{agent_name}: missing evaluation scenario", errors)
        require(agent_name in case_agents, f"{agent_name}: missing concrete evaluation case", errors)

    if (ROOT / ".git").is_dir():
        tracked = run(["git", "ls-files"], ROOT)
        tracked_paths = result_text(tracked).splitlines()
        forbidden_tracked = [
            path
            for path in tracked_paths
            if re.search(r"(^|/)(\.venv|\.git|__pycache__|\.pytest_cache|\.ruff_cache|instance)(/|$)", path)
            or re.search(r"\.(pyc|sqlite|sqlite3)$", path)
            or Path(path).name == ".env"
        ]
        require(not forbidden_tracked, f"forbidden tracked paths: {forbidden_tracked}", errors)


def check_readme(errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in ("Quick start", "Course map", "Evidence ladder", "Troubleshooting", "Final self-assessment"):
        require(heading.casefold() in readme.casefold(), f"README missing {heading!r}", errors)
    for lab in range(1, 11):
        count = len(re.findall(rf"^## Lab {lab}\b", readme, flags=re.MULTILINE))
        require(count == 1, f"README must contain exactly one Lab {lab} heading; found {count}", errors)
    for stage in STAGES:
        require(stage.name in readme, f"README does not name {stage.name}", errors)
    for agent_name in CUSTOM_AGENTS:
        require(agent_name in readme, f"README does not name {agent_name}", errors)
    require("requirements.txt" in readme, "README does not use requirements.txt", errors)
    require("STUDENT_SETUP.md" in readme, "README does not link the student setup guide", errors)
    require("runbook.md" not in readme, "README still refers to runbook.md", errors)
    require("runbook.pdf" not in readme, "README still refers to runbook.pdf", errors)
    require(not (ROOT / "runbook.md").exists(), "obsolete runbook.md still exists", errors)
    require(not (ROOT / "runbook.pdf").exists(), "obsolete runbook.pdf still exists", errors)


def check_green_stage(stage: Stage, errors: list[str]) -> None:
    stage_path = ROOT / stage.name
    pytest = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], stage_path)
    output = result_text(pytest)
    exact_pass = re.search(rf"(?m)^{stage.passed} passed in ", output)
    unexpected_outcome = re.search(r"\b(skipped|xfailed|xpassed|deselected)\b", output)
    if pytest.returncode != 0 or not exact_pass or unexpected_outcome:
        errors.append(f"{stage.name}: expected {stage.passed} passing tests\n{output}")


def check_intentional_red(stage: Stage, errors: list[str]) -> None:
    stage_path = ROOT / stage.name
    legacy = run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_tasks.py"],
        stage_path,
    )
    legacy_output = result_text(legacy)
    if legacy.returncode != 0 or not re.search(r"(?m)^5 passed in ", legacy_output):
        errors.append(f"{stage.name}: legacy baseline is not five green tests\n{legacy_output}")

    focused = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/test_owner_filter.py",
        ],
        stage_path,
    )
    focused_output = result_text(focused)
    expected = (
        focused.returncode != 0
        and re.search(r"(?m)^2 failed in ", focused_output)
        and focused_output.count("unexpected keyword argument 'owner'") >= 2
    )
    if not expected:
        errors.append(f"{stage.name}: expected two owner-argument failures\n{focused_output}")


def check_runtime(errors: list[str]) -> None:
    require(sys.version_info[:2] == (3, 12), f"verification requires Python 3.12, got {sys.version.split()[0]}", errors)
    for stage in STAGES:
        if stage.intentional_red:
            check_intentional_red(stage, errors)
        else:
            check_green_stage(stage, errors)
        lint = run([sys.executable, "-m", "ruff", "check", ".", "--no-cache"], ROOT / stage.name)
        if lint.returncode != 0:
            errors.append(f"{stage.name}: Ruff failed\n{result_text(lint)}")


def check_release(errors: list[str]) -> None:
    require((ROOT / ".git").is_dir(), "release verification requires a Git repository", errors)
    if not (ROOT / ".git").is_dir():
        return

    status = run(["git", "status", "--porcelain", "--untracked-files=normal"], ROOT)
    require(not result_text(status), "release worktree is not clean", errors)

    tag = run(["git", "rev-parse", "--verify", "refs/tags/workshop-start"], ROOT)
    require(tag.returncode == 0, "release is missing workshop-start tag", errors)
    head = run(["git", "rev-parse", "HEAD"], ROOT)
    if tag.returncode == 0 and head.returncode == 0:
        require(
            result_text(tag) == result_text(head),
            "workshop-start tag does not point to the release commit",
            errors,
        )

    tracked_result = run(["git", "ls-files"], ROOT)
    tracked = set(result_text(tracked_result).splitlines())
    critical = {
        "README.md",
        "STUDENT_SETUP.md",
        "AGENTS.md",
        "requirements.txt",
        ".github/workflows/workshop-verify.yml",
        ".codex/config.toml",
        ".agents/evals/scenario-matrix.md",
        ".agents/evals/cases.json",
        "scripts/bootstrap.ps1",
        "scripts/bootstrap.sh",
        "scripts/preflight.ps1",
        "scripts/preflight.sh",
        "scripts/reset-stage.ps1",
        "scripts/reset-stage.sh",
        "scripts/verify_workshop.py",
        "Implementation-start/FEATURE_PLAN.md",
    }
    for agent_name in CUSTOM_AGENTS:
        critical.add(f".codex/agents/{agent_name}.toml")
    for skill in SKILLS:
        critical.add(f".agents/skills/{skill}/SKILL.md")
        critical.add(f".agents/skills/{skill}/agents/openai.yaml")
        skill_root = ROOT / ".agents/skills" / skill
        for support_file in skill_root.rglob("*"):
            if support_file.is_file() and "__pycache__" not in support_file.parts:
                critical.add(support_file.relative_to(ROOT).as_posix())
    missing = sorted(critical - tracked)
    require(not missing, f"critical release paths are not tracked: {missing}", errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-only", action="store_true")
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    check_structure(errors)
    check_readme(errors)
    if not args.structure_only:
        check_runtime(errors)
    if args.release:
        check_release(errors)

    if errors:
        print("Workshop verification FAILED")
        for error in errors:
            print(f"\n- {error}")
        return 1

    mode = "release" if args.release else ("structure" if args.structure_only else "full")
    print(f"Workshop verification passed ({mode}).")
    print("Agents: checkpoint_auditor / security_reviewer")
    if not args.structure_only:
        print("Checkpoints: 5 / 5 / 5 / (5 pass + 2 expected fail) / 11 / 16 / 20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
