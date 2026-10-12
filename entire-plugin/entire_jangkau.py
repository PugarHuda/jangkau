"""entire jangkau: an Entire CLI plugin that checks whether an agent checkpoint made a site less accessible.

    entire jangkau <checkpoint-id | commit> [--repo PATH] [--json]

It resolves an Entire-Checkpoint trailer to its commit, finds the HTML pages that commit touched (directly, or
through a stylesheet next to them), audits each page before and after the commit with Jangkau's axe-core audit
in a real browser, and prints the difference per WCAG rule. Exit code 1 when a page got worse, so it can gate a
checkpoint the same way `entire graph checkpoint` reviews one. No model key is needed: it only audits."""
import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent  # the jangkau repo this plugin ships in
PAGES = (".html", ".htm")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def resolve(repo: Path, ref: str) -> tuple:
    """A checkpoint id (from an Entire-Checkpoint trailer) or any commit-ish -> (commit, checkpoint or None)."""
    hit = git(repo, "log", "--all", "--format=%H", f"--grep=^Entire-Checkpoint: {ref}$").split()
    if hit:
        return hit[0], ref
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip(), None


def touched_pages(repo: Path, commit: str) -> list:
    """Pages the commit changed, plus pages in a folder whose stylesheet it changed."""
    changed = git(repo, "diff", "--name-only", "--diff-filter=AMR", f"{commit}^", commit).split("\n")
    pages = {p for p in changed if p.lower().endswith(PAGES)}
    css_dirs = {str(Path(p).parent).replace("\\", "/") for p in changed if p.lower().endswith(".css")}
    for d in css_dirs:  # a stylesheet change can break every page that links it; check the pages beside it
        root = str(Path(d).parent).replace("\\", "/") if Path(d).name in ("css", "styles", "assets") else d
        listed = git(repo, "ls-tree", "-r", "--name-only", commit, "--", "." if root == "." else root).split("\n")
        pages |= {p for p in listed if p.lower().endswith(PAGES) and p.count("/") <= root.count("/") + 1}
    return sorted(p for p in pages if p)


def export(repo: Path, commit: str, paths: list, dest: Path) -> bool:
    """Write `paths`' folders at `commit` into dest (assets included). False when none existed yet."""
    dirs = sorted({str(Path(p).parent).replace("\\", "/") for p in paths})
    present = [d for d in dirs if git(repo, "ls-tree", commit, "--", d if d != "." else ".").strip()]
    if not present:
        return False
    data = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit, "--", *present],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        t.extractall(dest, filter="data")
    return True


def main():
    ap = argparse.ArgumentParser(prog="entire jangkau", description=__doc__.split("\n\n")[0])
    ap.add_argument("ref", help="Entire checkpoint id, or a commit")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    a = ap.parse_args()
    repo = Path(git(a.repo, "rev-parse", "--show-toplevel").strip())
    commit, checkpoint = resolve(repo, a.ref)
    pages = touched_pages(repo, commit)
    result = {"checkpoint": checkpoint, "commit": commit[:12], "pages": []}
    if pages:
        os.environ.setdefault("NEATLOGS_API_KEY", "")  # audit only: nothing to trace, no keys needed
        sys.path.insert(0, str(HOME))
        import contextlib
        with contextlib.redirect_stdout(sys.stderr):
            import jangkau
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
            tmp = Path(tmp)
            had = {"before": export(repo, f"{commit}^", pages, tmp / "before"),
                   "after": export(repo, commit, pages, tmp / "after")}
            page = jangkau.new_page(pw)
            for p in pages:
                row = {"page": p}
                for side in ("before", "after"):
                    f = tmp / side / p
                    if had[side] and f.is_file():
                        r = jangkau.audit(page, f, tmp / f"{side}.png")
                        row[side] = {"nodes": r["nodes"], "by_rule": r["by_rule"]}
                if "before" not in row:  # a page the commit added has nothing to regress from
                    row["new"], row["worse"], row["better"] = True, {}, {}
                    result["pages"].append(row)
                    continue
                b, af = row.get("before", {}).get("by_rule", {}), row.get("after", {}).get("by_rule", {})
                row["worse"] = {k: [b.get(k, 0), v] for k, v in af.items() if v > b.get(k, 0)}
                row["better"] = {k: [v, af.get(k, 0)] for k, v in b.items() if af.get(k, 0) < v}
                result["pages"].append(row)
    regressed = [r["page"] for r in result["pages"] if r["worse"]]
    result["verdict"] = "regressed" if regressed else "ok"

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        head = f"checkpoint {checkpoint} -> commit {commit[:12]}" if checkpoint else f"commit {commit[:12]}"
        print(f"{head}: {len(pages)} page(s) touched")
        for r in result["pages"]:
            n = lambda side: r[side]["nodes"] if side in r else "-"
            print(f"  {r['page']}: " + (f"new page, {n('after')} failing elements" if r.get("new") else
                                        f"{n('before')} -> {n('after')} failing elements"))
            for k, (x, y) in r["worse"].items():
                print(f"    worse  {k}: {x} -> {y}")
            for k, (x, y) in r["better"].items():
                print(f"    better {k}: {x} -> {y}")
        print("verdict: " + (f"REGRESSED ({', '.join(regressed)})" if regressed else "no accessibility regression"))
    sys.exit(1 if regressed else 0)


if __name__ == "__main__":
    main()
