"""Generates schemas/*.schema.json (single source of truth, kept in repo)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "schemas"
OUT.mkdir(exist_ok=True)

S = {}

S["brief"] = {
    "type": "object",
    "required": ["run_id", "sentence", "listing_id", "deliverable", "languages", "video", "created_at"],
    "properties": {
        "run_id": {"type": "string"},
        "sentence": {"type": "string"},
        "listing_id": {"type": "string", "pattern": "^[0-9]{10,}$"},
        "deliverable": {"type": "array", "minItems": 5, "items": {"type": "string"}},
        "languages": {"type": "array", "items": {"enum": ["zh", "en", "ja", "ko"]}},
        "video": {"type": "object", "required": ["sizes", "duration_s"],
                  "properties": {"sizes": {"type": "array", "items": {"enum": ["9:16", "16:9"]}},
                                 "duration_s": {"type": "integer", "minimum": 30, "maximum": 45}}},
        "created_at": {"type": "string"},
    },
}

S["facts"] = {
    "type": "object",
    "required": ["listing_id", "generated_at", "facts", "sources"],
    "properties": {
        "listing_id": {"type": "string"},
        "generated_at": {"type": "string"},
        "facts": {"type": "object", "additionalProperties": {
            "type": "object",
            "required": ["value", "source_id", "status"],
            "properties": {"value": {}, "source_id": {"type": "string"},
                           "status": {"enum": ["verified", "unverified", "conflict", "pending_owner"]},
                           "note": {"type": "string"}},
        }},
        "sources": {"type": "array", "items": {"type": "object",
                    "required": ["id", "kind", "url", "retrieved_at"],
                    "properties": {"id": {"type": "string"}, "kind": {"type": "string"},
                                   "url": {"type": "string"}, "retrieved_at": {"type": "string"},
                                   "sha256": {"type": "string"}, "note": {"type": "string"}}}},
    },
}

S["comps"] = {
    "type": "object",
    "required": ["status", "captured_at", "count", "comps", "gaps"],
    "properties": {
        "status": {"enum": ["ok", "partial", "blocked_robots", "blocked_antibot"]},
        "captured_at": {"type": "string"},
        "count": {"type": "integer"},
        "comps": {"type": "array", "items": {"type": "object",
                  "required": ["comp_id", "suburb", "room_type", "guests", "rating", "price_aud", "price_date", "source_url"],
                  "properties": {"comp_id": {"type": "string"}, "suburb": {"type": "string"},
                                 "room_type": {"type": "string"}, "guests": {"type": "integer"},
                                 "rating": {"type": "number"}, "price_aud": {"type": "number"},
                                 "price_date": {"type": "string"}, "source_url": {"type": "string"},
                                 "amenities": {"type": "array", "items": {"type": "string"}}}}},
        "gaps": {"type": "array", "items": {"type": "string"}},
    },
}

S["media_manifest"] = {
    "type": "object",
    "required": ["items"],
    "properties": {"items": {"type": "array", "items": {"type": "object",
        "required": ["path", "sha256", "bytes", "width", "height", "role", "origin", "license"],
        "properties": {"path": {"type": "string"}, "sha256": {"type": "string"},
                       "bytes": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"},
                       "role": {"enum": ["placeholder", "owner-supplied"]},
                       "origin": {"type": "string"}, "license": {"type": "string"},
                       "note": {"type": "string"}}}}},
}

S["licenses"] = {
    "type": "object",
    "required": ["generated_at", "assets"],
    "properties": {"generated_at": {"type": "string"}, "assets": {"type": "array", "items": {"type": "object",
        "required": ["path", "license", "attribution", "source"],
        "properties": {"path": {"type": "string"}, "license": {"type": "string"},
                       "attribution": {"type": "string"}, "source": {"type": "string"},
                       "role": {"type": "string"}}}}},
}

S["pricing"] = {
    "type": "object",
    "required": ["status", "currency", "generated_at", "recommendations", "evidence", "gaps"],
    "properties": {
        "status": {"enum": ["ok", "degraded", "insufficient_market_data"]},
        "currency": {"type": "string"},
        "generated_at": {"type": "string"},
        "recommendations": {"type": "object", "required": ["weekday", "weekend", "peak", "min_nights"]},
        "scenarios": {"type": "array"},
        "evidence": {"type": "array", "items": {"type": "object",
                     "required": ["claim", "source_id", "strength"],
                     "properties": {"claim": {"type": "string"}, "source_id": {"type": "string"},
                                    "strength": {"enum": ["verified", "assumption"]}}}},
        "gaps": {"type": "array", "items": {"type": "string"}},
    },
}

S["copy"] = {
    "type": "object",
    "required": ["lang", "title", "sections", "generated_at"],
    "properties": {
        "lang": {"enum": ["zh", "en", "ja", "ko"]},
        "title": {"type": "string"},
        "title_len": {"type": "integer"},
        "sections": {"type": "array", "items": {"type": "object",
            "required": ["id", "heading", "paragraphs"],
            "properties": {"id": {"type": "string"}, "heading": {"type": "string"},
                           "paragraphs": {"type": "array", "items": {"type": "object",
                               "required": ["text", "sources"],
                               "properties": {"text": {"type": "string"},
                                              "sources": {"type": "array", "items": {"type": "string"}}}}}}}},
        "generated_at": {"type": "string"},
    },
}

S["guide"] = {
    "type": "object",
    "required": ["lang", "pdf", "sections", "placeholders", "generated_at"],
    "properties": {"lang": {"enum": ["zh", "en"]}, "pdf": {"type": "string"},
                   "sections": {"type": "array"}, "placeholders": {"type": "array", "items": {"type": "string"}},
                   "generated_at": {"type": "string"}},
}

S["site"] = {
    "type": "object",
    "required": ["root", "pages", "form", "no_payment", "generated_at"],
    "properties": {"root": {"type": "string"}, "pages": {"type": "array", "items": {"type": "string"}},
                   "form": {"type": "object"}, "no_payment": {"const": True}, "generated_at": {"type": "string"}},
}

S["qc"] = {
    "type": "object",
    "required": ["passed", "checks"],
    "properties": {"passed": {"type": "boolean"}, "checks": {"type": "array"}},
}

S["kb"] = {
    "type": "object",
    "required": ["generated_at", "articles", "faq_count"],
    "properties": {"generated_at": {"type": "string"}, "faq_count": {"type": "integer", "minimum": 20},
                   "articles": {"type": "array", "items": {"type": "object",
                       "required": ["id", "title", "path"],
                       "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "path": {"type": "string"}}}}},
}

S["handoff"] = {
    "type": "object",
    "required": ["station", "run_id", "inputs", "outputs", "tools", "duration_s", "exit_code"],
    "properties": {"station": {"type": "string"}, "run_id": {"type": "string"},
                   "started_at": {"type": "string"}, "ended_at": {"type": "string"},
                   "duration_s": {"type": "number"}, "exit_code": {"type": "integer"},
                   "inputs": {"type": "array", "items": {"type": "object",
                              "required": ["path", "sha256"],
                              "properties": {"path": {"type": "string"}, "sha256": {"type": "string"}}}},
                   "outputs": {"type": "array", "items": {"type": "object",
                               "required": ["path", "sha256"],
                               "properties": {"path": {"type": "string"}, "sha256": {"type": "string"},
                                              "schema": {"type": ["string", "null"]}}}},
                   "tools": {"type": "array"}, "metrics": {"type": "object"},
                   "notes": {"type": "array"}, "error": {"type": ["string", "null"]}},
}

S["scorecard"] = {
    "type": "object",
    "required": ["station", "scores", "total", "notes"],
    "properties": {"station": {"type": "string"},
                   "scores": {"type": "object", "required": ["commercial", "handoff", "benchmark", "craft"]},
                   "total": {"type": "number"}, "notes": {"type": "array"}},
}

for name, schema in S.items():
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["title"] = name
    (OUT / f"{name}.schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(S)} schemas to {OUT}")
