import sys, os, glob, importlib, json, random, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import lib
only = sys.argv[1:] 
mods = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t_*.py")))
for m in mods:
    importlib.import_module(os.path.basename(m)[:-3])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch10")
bad = 0
for tk in sorted(lib.TASKS, key=lambda x: x["code"]):
    if only and tk["code"] not in only: continue
    c = tk["cls"]
    gen, sol, brute = c.gen, c.sol, c.brute
    exec(getattr(c, 'helpers', ''), gen.__globals__)
    # verify
    ok = True
    for seed in range(300):
        r = random.Random(seed)
        inp = gen(r, 0)
        a, b = norm(sol(inp)), norm(brute(inp))
        if a != b:
            print("MISMATCH", tk["code"], tk["name"], "seed", seed); print(inp); print("sol:", a[:200]); print("brute:", b[:200]); ok = False; bad += 1; break
    if not ok: continue
    mx = 0; sizes = []
    for t in range(1, 11):
        r = random.Random(int(tk["code"]) * 1000 + t)
        inp = gen(r, t)
        t0 = time.time(); o = sol(inp); dt = time.time() - t0
        mx = max(mx, dt); sizes.append(len(inp))
    print(tk["code"], tk["name"], "ok maxsol=%.2fs maxin=%d" % (mx, max(sizes)))
    # samples
    ex = []
    for s in tk["samples"]:
        s = s.strip("\n") + "\n"
        a, b = norm(sol(s)), norm(brute(s))
        assert a == b, ("sample mismatch", tk["code"])
        ex.append((s, a))
    d = os.path.join(out, tk["code"]); os.makedirs(d, exist_ok=True)
    md = "# " + tk["name"] + "\n\n" + tk["stmt"] + "\n\n"
    for i, (s, a) in enumerate(ex, 1):
        md += "## Пример %d\n\nВвод:\n```\n%s```\n\nВывод:\n```\n%s\n```\n\n" % (i, s, a)
    open(os.path.join(d, "statement.md"), "w").write(md.rstrip() + "\n")
    helpers = getattr(c, "helpers", "")
    open(os.path.join(d, "gen.py"), "w").write(PRE + "\n" + lib.N_SRC + "\n" + helpers + "\n" + src(gen, "gen") + "\nif __name__ == '__main__':\n    t = int(sys.argv[1])\n    r = random.Random(%s * 1000 + t)\n    sys.stdout.write(gen(r, t))\n" % int(tk["code"]))
    for nm, f in (("sol", sol), ("brute", brute)):
        open(os.path.join(d, nm + ".py"), "w").write(PRE + "\n" + helpers + "\n" + src(f, "solve") + "\nif __name__ == '__main__':\n    print(solve(sys.stdin.read()))\n")
    json.dump(dict(code=tk["code"], name=tk["name"], topic=tk["topic"], time_limit=tk["tl"], memory_mb=256, points=100, tests=10, group="olympiad"), open(os.path.join(d, "meta.json"), "w"), ensure_ascii=False, indent=1)
print("bad:", bad)
