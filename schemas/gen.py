"""生成 JSON Schema（draft 2020-12）。python schemas/gen.py"""
import json, pathlib
D = pathlib.Path(__file__).parent
S = "https://json-schema.org/draft/2020-12/schema"
src = {"type": "string", "minLength": 1}
sha = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
schemas = {
 "brief": {"type":"object","required":["sentence","client","duration_s","languages","aspects","platforms","deliverables"],
   "properties":{"sentence":src,"client":{"type":"object","required":["name_en"],"properties":{"name_en":src,"name_zh_spoken":{"type":"string"},"city":{"type":"string"}}},
   "duration_s":{"type":"number","minimum":5,"maximum":180},"languages":{"type":"array","items":{"enum":["zh","en"]},"minItems":1},
   "aspects":{"type":"array","items":{"enum":["9:16","1:1","16:9"]},"minItems":1},"platforms":{"type":"array","items":src},"deliverables":{"type":"array","items":src}}},
 "facts": {"type":"object","required":["sources","facts"],"properties":{
   "sources":{"type":"array","items":{"type":"object","required":["source_id","url","retrieved"],"properties":{"source_id":src,"url":src,"retrieved":src,"sha256":{"type":"string"}}}},
   "facts":{"type":"array","items":{"type":"object","required":["field","value","source_id","status"],"properties":{"field":src,"value":{},"source_id":src,"status":{"enum":["verified","unverified","conflict","pending"]},"note":{"type":"string"}}}}}},
 "media_manifest": {"type":"object","required":["media"],"properties":{"media":{"type":"array","items":{"type":"object",
   "required":["media_id","path","sha256","origin","license","kind","width","height"],"properties":{"media_id":src,"path":src,"sha256":sha,"note":{"type":"string"},
   "origin":{"enum":["customer-supplied","placeholder","generated"]},"license":src,"permission":{"enum":["granted","pending","n/a"]},
   "kind":{"enum":["image","video","audio","font"]},"width":{"type":"integer"},"height":{"type":"integer"},"duration_s":{"type":["number","null"]},"fps":{"type":["number","null"]},"source_id":{"type":"string"}}}}}},
 "menu": {"type":"object","required":["items","status"],"properties":{"status":src,"items":{"type":"array","items":{"type":"object",
   "required":["name_zh","name_en","price_aud_inc_gst","source_id","status"],"properties":{"name_zh":src,"name_en":src,"price_aud_inc_gst":{"type":"number"},"source_id":src,"status":{"const":"verified"}}}}}},
 "script": {"type":"object","required":["duration_s","shots"],"properties":{"duration_s":{"type":"number"},"shots":{"type":"array","minItems":6,"maxItems":8,"items":{"type":"object",
   "required":["shot_id","start","end","visual","media_id","sub_zh","sub_en","refs"],"properties":{"shot_id":src,"start":{"type":"number"},"end":{"type":"number"},"visual":src,"media_id":src,
   "customer_shot_slot":{"type":"string"},"sub_zh":src,"sub_en":src,"refs":{"type":"array","items":{"type":"string","pattern":"^(facts|menu):"}}}}}}},
 "handoff": {"type":"object","required":["station","inputs","outputs","tools","elapsed_s","exit_code"],"properties":{"station":src,
   "inputs":{"type":"array","items":{"type":"object","required":["path","sha256"],"properties":{"path":src,"sha256":sha}}},
   "outputs":{"type":"array","items":{"type":"object","required":["path","sha256"],"properties":{"path":src,"sha256":sha,"schema":{"type":["string","null"]}}}},
   "tools":{"type":"array","items":{"type":"object","required":["name","version"]}},"elapsed_s":{"type":"number"},"exit_code":{"type":"integer"}}},
}
for k, v in schemas.items():
    v = {"$schema": S, "$id": f"craft-skills/{k}.schema.json", "title": k, **v}
    (D / f"{k}.schema.json").write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n")
print("ok", len(schemas))
