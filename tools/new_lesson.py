"""Scaffold a new lesson folder (and its answer-key folder).

    python tools/new_lesson.py m00 l13-my-topic "My topic title"

Then fill in the files, add the lesson id to module.json ("lessons",
"lessonDirs", "lessonTitles"), and run: python tools/verify.py m00.l13
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 1
    module_id, folder, title = argv[1], argv[2], argv[3]
    cur = json.loads((ROOT / "content" / "curriculum.json").read_text(encoding="utf-8"))
    entry = next(m for m in cur["modules"] if m["id"] == module_id)
    lesson_id = f"{module_id}.{folder.split('-')[0]}"
    base = ROOT / "content" / "modules" / entry["dir"] / folder
    if base.exists():
        print(f"{base} already exists")
        return 1
    for sub in ("examples", "challenge", "bug"):
        (base / sub).mkdir(parents=True)
    meta = {
        "id": lesson_id, "title": title, "minutes": 75,
        "objectives": ["TODO objective 1", "TODO objective 2"],
        "skills": {"python": 3},
        "whereYouSawThis": {"course": "TODO", "topic": "TODO"},
        "examples": [{"id": f"ex{i}", "title": f"Example {i}", "file": f"examples/ex{i}.py", "expectedOutput": ""} for i in (1, 2, 3)],
        "predict": [{"id": "p1", "code": "print(1)", "choices": ["1", "2"], "answer": 0, "why": "TODO"}],
        "visualizations": [{"id": "v1", "component": "tracer", "props": {"code": "x = 1\n"}, "notice": "TODO",
                            "predictFirst": {"question": "TODO", "reveal": "TODO"}}],
        "challenge": {"task": "TODO", "starter": "challenge/starter.py", "tests": "challenge/test_challenge.py"},
        "bug": {"file": "bug/buggy.py", "tests": "bug/test_bug.py", "bugType": "TODO", "report": "TODO"},
        "explainBack": {"prompt": "TODO", "rubric": ["TODO", "TODO"], "minWords": 40},
        "hints": {"challenge": ["nudge", "approach", "pseudocode"], "bug": ["nudge"]},
    }
    (base / "lesson.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (base / "lesson.md").write_text(
        f"## {title}\n\nTODO prose.\n\n{{{{example:ex1}}}}\n\n{{{{example:ex2}}}}\n\n{{{{example:ex3}}}}\n\n"
        "{{predict:p1}}\n\n{{viz:v1}}\n\n## Challenge\n\n{{challenge}}\n\n## Find the bug\n\n{{bug}}\n\n"
        "## Explain it back\n\n{{explain}}\n", encoding="utf-8")
    for i in (1, 2, 3):
        (base / "examples" / f"ex{i}.py").write_text("print('TODO')\n", encoding="utf-8")
    (base / "challenge" / "starter.py").write_text("def todo():\n    pass\n", encoding="utf-8")
    (base / "challenge" / "test_challenge.py").write_text("from solution import todo\n\n\ndef test_todo():\n    \"\"\"TODO\"\"\"\n    assert todo() == 1\n", encoding="utf-8")
    (base / "bug" / "buggy.py").write_text("def todo():\n    return 0\n", encoding="utf-8")
    (base / "bug" / "test_bug.py").write_text("from solution import todo\n\n\ndef test_todo():\n    \"\"\"TODO\"\"\"\n    assert todo() == 1\n", encoding="utf-8")
    key = ROOT / "verification" / lesson_id
    if (ROOT / "verification").exists():
        key.mkdir(parents=True, exist_ok=True)
        for name in ("challenge.py", "wrong_1.py", "wrong_2.py", "bug_fixed.py"):
            (key / name).write_text("# TODO\n", encoding="utf-8")
    print(f"Created {base}\nAnswer key: {key}\nNow add {lesson_id} to module.json and run tools/verify.py {lesson_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
