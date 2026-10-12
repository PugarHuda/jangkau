"""Merge several Jangkau SARIF files into one run, so code scanning gets a single upload."""
import json
import sys

out, *inputs = sys.argv[1:]
rules, results = {}, []
for path in inputs:
    run = json.load(open(path, encoding="utf-8"))["runs"][0]
    for rule in run["tool"]["driver"]["rules"]:
        rules.setdefault(rule["id"], rule)
    results += run["results"]
doc = {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
       "runs": [{"tool": {"driver": {"name": "Jangkau", "informationUri": "https://github.com/PugarHuda/jangkau",
                                     "rules": list(rules.values())}}, "results": results}]}
json.dump(doc, open(out, "w", encoding="utf-8"), indent=2)
print(f"{out}: {len(results)} results, {len(rules)} rules from {len(inputs)} file(s)")
