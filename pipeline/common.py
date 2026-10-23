"""接力链公共件：哈希、Schema 校验、handoff/qa/scorecard 落盘、命令执行。"""
import datetime, hashlib, json, os, pathlib, resource, subprocess, sys, time
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


class StationFail(Exception):
    def __init__(self, station, step, why):
        super().__init__(f"[{station}] {step}: {why}")
        self.station, self.step, self.why = station, step, why


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rjson(p):
    return json.loads(pathlib.Path(p).read_text())


def wjson(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return p


def validate(obj_or_path, schema, station, step="schema"):
    obj = rjson(obj_or_path) if isinstance(obj_or_path, (str, pathlib.Path)) else obj_or_path
    v = Draft202012Validator(rjson(SCHEMAS / f"{schema}.schema.json"))
    errs = sorted(v.iter_errors(obj), key=lambda e: e.path)
    if errs:
        raise StationFail(station, step, f"{schema} 校验失败: " + "; ".join(f"{list(e.path)} {e.message}" for e in errs[:5]))
    return obj


def run(cmd, station, step, **kw):
    t = time.time()
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise StationFail(station, step, f"exit {r.returncode}: {(r.stderr or r.stdout)[-600:]}")
    return r


def ver(cmd):
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return (out.stdout or out.stderr).strip().splitlines()[0][:120]
    except Exception as e:
        return f"unknown ({e})"


class Station:
    """with Station(run_dir, '03_grade', inputs=[...]) as st: ... st.out(path, schema)"""

    def __init__(self, run_dir, name, inputs=(), tools=()):
        self.dir = pathlib.Path(run_dir) / name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.name, self.inputs, self.tools = name, list(inputs), list(tools)
        self.outputs, self.checks, self.score = [], [], {}

    def __enter__(self):
        self.t = time.time(); self.t_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds'); self.cpu0 = self._cpu()
        for p in self.inputs:
            if not pathlib.Path(p).exists():
                raise StationFail(self.name, "inputs", f"上一站产出缺失: {p}")
        print(f"==> {self.name}", flush=True)
        return self

    @staticmethod
    def _cpu():
        a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime

    def out(self, p, schema=None):
        self.outputs.append((pathlib.Path(p), schema)); return p

    def check(self, name, ok, value=None, threshold=None, note=""):
        self.checks.append({"check": name, "pass": bool(ok), "value": value, "threshold": threshold, "note": note})
        return ok

    def __exit__(self, et, ev, tb):
        code = 0 if et is None else 2
        rel = lambda p: os.path.relpath(p, self.dir.parent)
        h = {"station": self.name,
             "inputs": [{"path": rel(p), "sha256": sha256(p)} for p in self.inputs if pathlib.Path(p).is_file()],
             "outputs": [{"path": rel(p), "sha256": sha256(p), "schema": s} for p, s in self.outputs if p.is_file()],
             "tools": self.tools, "elapsed_s": round(time.time() - self.t, 2), "exit_code": code, "started_at": self.t_iso, "ended_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "cpu_s": round(self._cpu() - self.cpu0, 2)}
        if et is not None:
            h["error"] = str(ev)
        wjson(self.dir / "handoff.json", h)
        qa_ok = all(c["pass"] for c in self.checks)
        wjson(self.dir / "qa.json", {"station": self.name, "pass": qa_ok and code == 0, "checks": self.checks})
        if self.score:
            wjson(self.dir / "scorecard.json", {"station": self.name, **self.score})
        validate(h, "handoff", self.name, "handoff")
        return False
