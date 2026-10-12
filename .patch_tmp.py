p = 'jangkau.py'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep('''MAX_ATTEMPTS = 3''', '''MAX_ATTEMPTS = 3        # attempts per rule while stuck
MAX_ATTEMPTS_PROGRESS = 8  # hard cap: every accepted partial fix earns one more attempt''')

rep('''@span(kind="TOOL", name="apply_edits")
def apply_edits(source: str, edits: list) -> str:
    """Apply find/replace edits; each `find` must match exactly once."""
    for i, e in enumerate(edits):
        find, repl = e.get("find", ""), e.get("replace", "")
        n = source.count(find) if find else 0
        if n != 1:
            raise ValueError(f"edit {i}: `find` matched {n} times (must be exactly 1): {find[:80]!r}")
        source = source.replace(find, repl, 1)
    return source''', '''@span(kind="TOOL", name="apply_edits")
def apply_valid_edits(source: str, edits: list) -> tuple:
    """Apply each find/replace whose `find` matches exactly once; collect the rest as errors.
    One mistyped `find` in a batch of 20 alt-text edits no longer throws away the other 19:
    the re-audit judges what was applied, and the skipped edits go back to the model."""
    errors = []
    for i, e in enumerate(edits):
        find, repl = e.get("find", ""), e.get("replace", "")
        n = source.count(find) if find else 0
        if n != 1:
            errors.append(f"edit {i}: `find` matched {n} times (must be exactly 1): {find[:80]!r}")
            continue
        source = source.replace(find, repl, 1)
    return source, errors


def apply_edits(source: str, edits: list) -> str:
    """Strict variant: every `find` must match exactly once."""
    source, errors = apply_valid_edits(source, edits)
    if errors:
        raise ValueError(errors[0])
    return source''')

rep('''    rid, start_nodes, feedback = rule["id"], len(rule["nodes"]), ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        source = html.read_text(encoding="utf-8")''', '''    rid, start_nodes, feedback = rule["id"], len(rule["nodes"]), ""
    budget, stuck, attempt = MAX_ATTEMPTS, 0, 0
    while attempt < budget:
        attempt += 1
        source = html.read_text(encoding="utf-8")''')

rep('''            resp = llm().chat.completions.create(
                model=ESCALATE_MODEL if attempt == MAX_ATTEMPTS else MODEL, temperature=0,''', '''            # escalate only when the cheap model is stuck: two failed or rejected attempts in a row
            resp = llm().chat.completions.create(
                model=ESCALATE_MODEL if stuck >= 2 else MODEL, temperature=0,''')

rep('''            plan = parse_json(resp.choices[0].message.content or "")
            html.write_text(apply_edits(source, plan.get("edits", [])), encoding="utf-8", newline="\n")
        except Exception as e:  # bad JSON, non-unique find, API hiccup -> retry with feedback
            feedback = f"it failed with {type(e).__name__}: {e}. Try again."''', '''            plan = parse_json(resp.choices[0].message.content or "")
            patched, skipped = apply_valid_edits(source, plan.get("edits", []))
            if patched == source:
                raise ValueError("no edit applied. " + "; ".join(skipped[:5]))
            html.write_text(patched, encoding="utf-8", newline="\n")
        except Exception as e:  # bad JSON, no usable edit, API hiccup -> retry with feedback
            stuck += 1
            feedback = f"it failed with {type(e).__name__}: {e}. Try again."''')

rep('''            html.write_text(source, encoding="utf-8", newline="\n")  # recovery: roll back the bad edit
            continue''', '''            html.write_text(source, encoding="utf-8", newline="\n")  # recovery: roll back the bad edit
            stuck += 1
            continue''')

rep('''        neatlogs.log("attempt {attempt} accepted", attempt=attempt, rule=rid, nodes_left=left,
                     visual_diff=round(vd, 4))''', '''        neatlogs.log("attempt {attempt} accepted", attempt=attempt, rule=rid, nodes_left=left,
                     visual_diff=round(vd, 4), skipped_edits=len(skipped))''')

rep('''        rule = next(v for v in after["violations"] if v["id"] == rid)
        feedback = f"it was accepted, but {left} nodes still fail (listed above). Fix those too."
    left = before["by_rule"].get(rid, 0)
    return {"rule": rid, "status": "partial" if left < start_nodes else "gave-up",
            "attempts": MAX_ATTEMPTS, "last_feedback": feedback}''', '''        rule = next(v for v in after["violations"] if v["id"] == rid)
        stuck, budget = 0, min(budget + 1, MAX_ATTEMPTS_PROGRESS)  # progress earns another attempt
        feedback = f"it was accepted, but {left} nodes still fail (listed above). Fix those too."
        if skipped:
            feedback += (" These edits were skipped because their `find` was not an exact, unique copy "
                         "of the current file: " + "; ".join(skipped[:5]))
    left = before["by_rule"].get(rid, 0)
    return {"rule": rid, "status": "partial" if left < start_nodes else "gave-up",
            "attempts": attempt, "last_feedback": feedback}''')

# --wait for pages that animate into their final state
rep('''def audit(page, html_path: Path, shot: Path) -> dict:
    page.goto(html_path.resolve().as_uri())''', '''def audit(page, html_path: Path, shot: Path) -> dict:
    page.goto(html_path.resolve().as_uri())
    if SETTLE_MS:
        page.wait_for_timeout(SETTLE_MS)''')
rep('''LANDMARKS = "main,nav,header,footer,aside,section,[role]"''', '''LANDMARKS = "main,nav,header,footer,aside,section,[role]"
SETTLE_MS = 0  # --wait: let intro animations finish before auditing''')
rep('''    a = ap.parse_args()
    if re.match''', '''    ap.add_argument("--wait", type=int, default=0, metavar="MS",
                    help="wait this long after load before each audit (pages that animate into place)")
    a = ap.parse_args()
    SETTLE_MS = a.wait
    if re.match''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
