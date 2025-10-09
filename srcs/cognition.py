import os
from typing import Dict, List, Optional
import warnings
import json
import re
from pathlib import Path
from functools import lru_cache
from datetime import datetime 
from heapq import heappush, heappop
import numpy as np
import pandas as pd
from joblib import load
from sentence_transformers import SentenceTransformer
import anthropic 

from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-2")
MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")
from db import SessionLocal
from crud import (
    insert_output,
    get_episodic,
    get_semantic,
)

db = SessionLocal()

warnings.filterwarnings("ignore", category=DeprecationWarning)
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

LAST_STATE_PATH = Path("last_species_state.json")

EXPECTED_WITH_ORIGIN = [
    "climbs_trees", "group_behavior", "swimming_ability", "flight_ability",
    "toxicity", "avoidance_tendency", "aggression_tendency",
    "risk_level", "origin_speed", "vision_sensitivity", "hearing_sensitivity",
    "state", "distance", "speed"
]

CANDIDATES_SIMPLE = ["snake", "boar", "bear", "rabbit", "dog", "deer", "owl"]

def _row_value(row, key):
    """Return attribute or dict item from ORM/Dict row."""
    if isinstance(row, dict):
        return row.get(key)
    return getattr(row, key, None)

def _row_to_dict(row) -> Dict:
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "__dict__"):
        return {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
    return {}

def _json_dict(value) -> Dict[str, float]:
    if value is None:
        return {}
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if v is None:
                continue
            try:
                result[(k or "").lower()] = float(v)
            except (TypeError, ValueError):
                continue
        return result
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return _json_dict(parsed)
    return {}

def _to_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, datetime):
        return x.strftime("%Y-%m-%d")
    return str(x)

def ask_claude(prompt: str) -> str:
    try:
        msg = client.messages.create(
            model=MODEL_NAME,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text if msg and getattr(msg, "content", None) else ""
    except Exception as e:
        return f"(LLM 호출 실패) {e}"

def _fmt_lines(s: str) -> str:
    text = s.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'([.!?])(\s|$)', r'\1\n', text)
    text = re.sub(r'[ \t]*\n[ \t]*', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def _norm(x: Optional[str]) -> str:
    return (x or "").strip().lower()

def _normalize_speed(v: Optional[str]) -> str:
    t = _norm(v)
    if not t:
        return "none"
    if t in ["still", "stopped"]:
        return "none"
    return t

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)

def _load_last_species() -> Optional[str]:
    try:
        if LAST_STATE_PATH.exists():
            data = json.loads(LAST_STATE_PATH.read_text(encoding="utf-8"))
            val = (data.get("last_species") or "").strip().lower()
            return val or None
    except Exception:
        pass
    return None

def _save_last_species(species: str) -> None:
    try:
        LAST_STATE_PATH.write_text(
            json.dumps({"last_species": (species or "").strip().lower()}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass

def resolve_animal_simple(raw_animal: str) -> str:
    if not raw_animal or not isinstance(raw_animal, str):
        return "unknown"
    texts = [raw_animal] + CANDIDATES_SIMPLE
    embeddings = embedder.encode(texts, normalize_embeddings=True)
    query_vec = embeddings[0]
    cand_vecs = embeddings[1:]
    sims = np.dot(cand_vecs, query_vec)
    best_idx = int(np.argmax(sims))
    return CANDIDATES_SIMPLE[best_idx]

def infer_species(sample_input: Dict, semantic_data: List[Dict], threshold: float = 0.8):
    species_feature_weights: Dict[str, Dict[str, Dict[str, float]]] = {}
    for row in semantic_data:
        sp = _row_value(row, "species")
        if not sp:
            continue
        colors = _json_dict(_row_value(row, "color_weights"))
        shapes = _json_dict(_row_value(row, "shape_weights"))
        species_feature_weights[sp] = {"color": colors, "shape": shapes}

    input_colors: List[str] = [c.strip().lower() for c in (sample_input.get("Color") or [])]
    input_shapes: List[str] = [s.strip().lower() for s in (sample_input.get("Shape") or [])]

    emb_cache: Dict[str, np.ndarray] = {}
    def emb(text: str) -> np.ndarray:
        key = (text or "").lower()
        if key not in emb_cache:
            emb_cache[key] = embedder.encode(key)
        return emb_cache[key]

    scores: Dict[str, float] = {sp: 0.0 for sp in species_feature_weights.keys()}
    contributions: Dict[str, List[Dict]] = {sp: [] for sp in species_feature_weights.keys()}

    for c in input_colors:
        in_vec = emb(c)
        for sp, cat in species_feature_weights.items():
            best = 0.0; best_feat=None; best_sim=0.0; best_w=0.0
            for feat, w in cat.get("color", {}).items():
                sim = cosine_sim(in_vec, emb(feat))
                if sim >= threshold:
                    contrib = sim * w
                    if contrib > best:
                        best = contrib; best_feat = feat; best_sim = sim; best_w = w
            scores[sp] += best
            if best > 0 and best_feat is not None:
                contributions[sp].append({
                    "category": "color","input_term": c,"matched_feat": best_feat,
                    "sim": float(best_sim),"weight": float(best_w),"contribution": float(best),
                })

    for s in input_shapes:
        in_vec = emb(s)
        for sp, cat in species_feature_weights.items():
            best = 0.0; best_feat=None; best_sim=0.0; best_w=0.0
            for feat, w in cat.get("shape", {}).items():
                sim = cosine_sim(in_vec, emb(feat))
                if sim >= threshold:
                    contrib = sim * w
                    if contrib > best:
                        best = contrib; best_feat = feat; best_sim = sim; best_w = w
            scores[sp] += best
            if best > 0 and best_feat is not None:
                contributions[sp].append({
                    "category": "shape","input_term": s,"matched_feat": best_feat,
                    "sim": float(best_sim),"weight": float(best_w),"contribution": float(best),
                })

    if not scores:
        return None, []
    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_species, top_score = ranking[0]
    if top_score <= 0:
        first_species = _row_value(semantic_data[0], "species") if semantic_data else None
        return first_species, []
    reasons = sorted(contributions.get(top_species, []), key=lambda r: r["contribution"], reverse=True)[:4]
    return top_species, reasons

def build_features(sample_input: Dict, species_row) -> Dict:
    # 상태 우선순위 (위험도 높은 순)
    state_priority = ["attack", "flicking", "head raised", "coiled", "neutral"]

    raw_state = sample_input.get("State")
    # 정규화/선택 함수
    def choose_state(val):
        if val is None:
            return ""
        # 리스트면 우선순위에 따라 제일 먼저 등장하는 값을 택함
        if isinstance(val, (list, tuple)):
            normalized = [_norm(x) for x in val if x is not None]
            for p in state_priority:
                if p in normalized:
                    return p
            # 우선순위에 없는 경우엔 첫 번째 요소 사용 (정상화)
            return normalized[0] if normalized else ""
        # 문자열이면 그냥 정규화
        return _norm(val)

    state_val    = choose_state(raw_state)
    distance_val = _norm(sample_input.get("Distance"))
    speed_input  = sample_input.get("speed", sample_input.get("Speed"))
    speed_val    = _normalize_speed(speed_input)

    origin_speed_raw = _row_value(species_row, "origin_speed")
    if origin_speed_raw is None:
        origin_speed_raw = _row_value(species_row, "speed")
    origin_speed_val = _normalize_speed(origin_speed_raw)

    features: Dict[str, object] = {
        "state": state_val,
        "distance": distance_val,
        "speed": speed_val,
        "origin_speed": origin_speed_val,
    }

    for col in [
        "climbs_trees","group_behavior","swimming_ability","flight_ability",
        "toxicity","avoidance_tendency","aggression_tendency",
        "risk_level","vision_sensitivity","hearing_sensitivity",
    ]:
        v = _row_value(species_row, col)
        features[col] = v.strip().lower() if isinstance(v, str) else v

    return features

def _predict_core(pipe, expected_cols: List[str], sample_input: Dict, species: str):
    prep = pipe.named_steps["prep"]
    clf = pipe.named_steps["clf"]

    row = {}
    for c in expected_cols:
        val = sample_input.get(c, 0)
        if isinstance(val, list):
            val = val[0]
        row[c] = val

    X_new = pd.DataFrame([row], columns=expected_cols)
    y_pred = pipe.predict(X_new)[0]

    X_trans = prep.transform(X_new)
    node_indicator = clf.decision_path(X_trans)
    leaf_id = clf.apply(X_trans)[0]
    visited = np.where(node_indicator.toarray()[0] == 1)[0].tolist()
    path_node_ids = [nid for nid in visited if nid != leaf_id]
    feature_names = prep.get_feature_names_out(input_features=expected_cols)

    sentences = []
    for nid in path_node_ids:
        fid = clf.tree_.feature[nid]
        thr = float(clf.tree_.threshold[nid])
        if fid == -1:
            continue
        feat = feature_names[fid]
        val = X_trans[0, fid]
        comp = "≤" if val <= thr else ">"
        sentences.append(f"{feat} 값({val:.3f})이 {thr:.3f} {comp}이다.")

    sentences.append(f"따라서 {species}에 대해 '{y_pred}' 행동을 수행하기로 했다.")
    return y_pred, sentences

@lru_cache(maxsize=1)
def get_pipe():
    return load(MODEL_PATH)

def predict_with_model(sample_input: Dict, species: str):
    pipe = get_pipe()
    return _predict_core(pipe, EXPECTED_WITH_ORIGIN, sample_input, species)

def _facts_from_features(species: str, features: Dict) -> str:
    state = features.get("state") or "unknown"
    distance = features.get("distance") or "unknown"
    speed = features.get("speed") or "none"

    parts = []
    if state != "unknown":
        parts.append(f"자세는 {state}")
    if distance != "unknown":
        parts.append(f"거리는 {distance}")
    if speed == "none":
        parts.append("움직임은 없다")
    else:
        parts.append(f"움직임은 {speed}")
    return f"[행동 결정]\n{species}에 대한 판단 근거: " + ", ".join(parts) + "."

def _steps_to_sentence(steps: str) -> str:
    step_list = [re.sub(r'^\s*\d+\.\s*', '', s).strip() for s in steps.split('.') if s.strip()]
    if not step_list:
        return ""
    if len(step_list) == 1:
        return step_list[0]
    elif len(step_list) == 2:
        return f"{step_list[0]} 그리고 {step_list[1]}"
    else:
        parts = []
        for i, step in enumerate(step_list):
            if i == 0:
                parts.append("먼저 " + step)
            elif i == len(step_list) - 1:
                parts.append("마지막으로 " + step)
            else:
                parts.append("그다음 " + step)
        return ", ".join(parts)
def get_action_plan_raw(species: str, action: str, sample_input: Dict) -> str:
    from heapq import heappush, heappop
    import numpy as np

    # === Distance 인식 ===
    distance = (sample_input.get("Distance") or "medium").lower().strip()
    distance_map = {"close": 1, "medium": 2, "far": 3}
    dist_gap = distance_map.get(distance, 2)

    # === 환경 맵 ===
    grid = [
        ["", "", "나무", "나무", "풀", "나무", "나무", "풀", "나무", ""],
        ["", "", "나무", "나무", "풀", "풀", "풀", "돌", "나무", ""],
        ["", "", "풀", "풀", "풀", "풀", "풀", "풀", "풀", ""],
        ["", "", "풀", "풀", "풀", "풀", "풀", "풀", "", ""],
        ["", "", "풀", "풀", "풀", "뱀", "풀", "풀", "", ""],
        ["", "", "풀", "돌", "풀", "", "풀", "풀", "", ""],
        ["", "", "풀", "풀", "풀", "풀", "풀", "풀", "", ""],
        ["", "", "풀", "풀", "풀", "풀", "풀", "풀", "", ""],
        ["", "", "", "", "돌", "풀", "풀", "", "", ""],
        ["goal", "", "", "", "", "", "", "", "", ""]
    ]
    ROWS, COLS = len(grid), len(grid[0])
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # === 뱀 위치 찾기 & 사용자 배치 ===
    snake_pos = None
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == "뱀":
                snake_pos = (r, c)
                break
        if snake_pos:
            break

    if snake_pos:
        sr, sc = snake_pos
        my_row = min(sr + dist_gap, ROWS - 1)
        grid[my_row][sc] = "나"
    else:
        grid[5][5] = "나"

    # === 유틸 함수 ===
    def find(name):
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c] == name:
                    return (r, c)
        return None

    def valid(r, c):
        return (0 <= r < ROWS and 0 <= c < COLS) and grid[r][c] not in ["나무", "돌", "뱀"]

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(start, goal):
        pq = []
        heappush(pq, (heuristic(start, goal), 0, start, [start]))
        visited = set()
        while pq:
            f, g, (r, c), path = heappop(pq)
            if (r, c) == goal:
                return path
            if (r, c) in visited:
                continue
            visited.add((r, c))
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if valid(nr, nc) and (nr, nc) not in visited:
                    heappush(pq, (g + 1 + heuristic((nr, nc), goal), g + 1, (nr, nc), path + [(nr, nc)]))
        return None

    start = find("나")
    snake = find("뱀")
    goal_default = find("goal")

    # === 행동별 목표 ===
    def find_cover(start):
        sr, sc = start
        covers = []
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c] in ["나무", "돌"]:
                    dist = abs(sr - r) + abs(sc - c)
                    covers.append((dist, (r, c)))
        covers.sort(key=lambda x: x[0])
        return covers[0][1] if covers else goal_default

    def back_away(start, snake):
        sr, sc = start
        sr_snake, sc_snake = snake
        target_row = ROWS - 1 if sr_snake < sr else 0
        target_col = sc
        return (target_row, target_col)

    if action == "run_away":
        target = goal_default
    elif action == "find_cover":
        target = find_cover(start)
    elif action == "back_away":
        target = back_away(start, snake)
    elif action == "stay_calm":
        return "[행동 계획 수립]\n자 천천히 심호흡을 하자.\n조용히 침착함을 유지해야 해.\n"
    elif action == "call_for_help":
        return "[행동 계획 수립]\n먼저 조용히 주변에 사람이 있는지 확인하는 거야.\n사람이 있다면 손을 흔들어 위치를 알리자.\n그렇지 않다면 주머니 속으로 손을 넣어 핸드폰을 확인해.\n그리고 천천히 핸드폰을 꺼내 도움을 요청하자.\n"
    else:
        target = goal_default

    # === A* 경로 탐색 ===
    path = a_star(start, target)
    if not path:
        return f"[행동 계획 수립]\n{species} 상황에서 {action} 경로를 찾지 못했습니다.\n"

    # === ✅ move_summary (구간별 방향 계산) ===
    def summarize_path_detailed(path):
        if not path or len(path) < 2:
            return "이동 없음"

        def direction_from_to(a, b):
            dr, dc = b[0] - a[0], b[1] - a[1]
            if abs(dr) > abs(dc):
                return "남쪽" if dr > 0 else "북쪽"
            elif abs(dc) > 0:
                return "동쪽" if dc > 0 else "서쪽"
            return "제자리"

        segments = []
        prev_dir = direction_from_to(path[0], path[1])
        count = 1

        for i in range(1, len(path) - 1):
            cur_dir = direction_from_to(path[i], path[i + 1])
            if cur_dir == prev_dir:
                count += 1
            else:
                segments.append((prev_dir, count))
                prev_dir = cur_dir
                count = 1
        segments.append((prev_dir, count))

        desc = " → ".join([f"{d}으로 {n*2}m" for d, n in segments if n > 0])
        return f"{desc} 이동"

    move_summary = summarize_path_detailed(path)

    # === 주변 지형 요약 ===
    def describe_nearby_objects_detailed(grid, start, radius=3):
        sr, sc = start
        objects = []
        for r in range(max(0, sr - radius), min(ROWS, sr + radius + 1)):
            for c in range(max(0, sc - radius), min(COLS, sc + radius + 1)):
                val = grid[r][c]
                if val in ["나무", "돌", "풀"]:
                    dist = abs(sr - r) + abs(sc - c)
                    if dist == 0:
                        continue
                    objects.append(f"({r},{c})에 {val} (거리 {dist*2}m)")
        return ", ".join(objects) if objects else "주변에 특별한 지형 없음"

    nearby_desc = describe_nearby_objects_detailed(grid, start)


    prompt = f"""
You are about to perform the action '{action}' after encountering a {species}.

- Movement summary: {move_summary}
- Nearby terrain: {nearby_desc}

Speak as if you are quietly thinking to yourself while planning your movement for '{action}'.
Describe {move_summary} naturally in your own words, based on visible terrain.
Write in Korean, no more than 3 sentences.
"""

    text = ask_claude(prompt).strip()
    return f"[행동 계획 수립]\n{text}\n"

def get_action_plan_natural(species: str, action: str, sample_input: Dict) -> str:
    raw = get_action_plan_raw(species, action, sample_input).format(action=action, species=species)
    formatted = re.sub(r'\.\s*', '.\n', raw.strip())
    return _fmt_lines(formatted) + "\n"

def generate_observation_reason_one_liner(species: str, reasons: List[Dict]) -> str:
    top = sorted((reasons or []), key=lambda r: float(r.get("contribution", r.get("sim", 0.0))), reverse=True)[:4]
    color_terms = [r["input_term"] for r in top if r.get("category") == "color"]
    shape_terms = [r["input_term"] for r in top if r.get("category") == "shape"]

    bits = []
    if color_terms:
        bits.append("색깔이 " + ", ".join(dict.fromkeys(color_terms)))
    if shape_terms:
        bits.append("형태는 " + ", ".join(dict.fromkeys(shape_terms)))

    if bits:
        obs = "이고, ".join(bits)
        return f"[객체 인식]\n{obs} 봐선 {species}로 보인다.\n"
    else:
        return f"[객체 인식]\n{species}로 보인다.\n"

def generate_brief_observation(sample_input: Dict, species: str) -> str:
    colors = [c for c in (sample_input.get("Color") or []) if c]
    shapes = [s for s in (sample_input.get("Shape") or []) if s]
    bits = []
    if colors: bits.append("색깔이 " + ", ".join(colors))
    if shapes: bits.append("형태는 " + ", ".join(shapes))
    if bits:
        return f"[객체 인식]\n{', '.join(bits)} 봐선 여전히 {species}이네.\n"
    return f"[객체 인식]\n여전히 {species}이네.\n"

def generate_observation_monologue_with_claude(sample_input: Dict, animal: str, species: str, reasons: List[Dict]) -> str:
    top_reasons = sorted(
        (reasons or []),
        key=lambda r: float(r.get("contribution", r.get("sim", 0.0))),
        reverse=True
    )[:4]

    colors = [c for c in (sample_input.get("Color") or []) if c]
    shapes = [s for s in (sample_input.get("Shape") or []) if s]

    episodic = get_episodic(db, species) or []
    semantic_rows = get_semantic(db, animal) or []
    sem_for_species = next((row for row in semantic_rows if _row_value(row, "species") == species), None)

    sem_facts = []
    if sem_for_species:
        for k, v in _row_to_dict(sem_for_species).items():
            if k not in ["animal", "species", "color_weights", "shape_weights", "id"] and v not in [None, ""]:
                sem_facts.append(f"{_to_text(k)}: {_to_text(v)}")

    epi_facts = []
    for row in episodic:
        row_dict = _row_to_dict(row)
        date = _to_text(row_dict.get("event_date")).strip()
        ctx  = _to_text(row_dict.get("context")).strip()
        if date or ctx:
            epi_facts.append(f"{date} - {ctx}")

    top_reasons_raw = []
    for r in top_reasons:
        rr = dict(r)
        rr["input_term"] = _to_text(rr.get("input_term", ""))
        rr["matched_feat"] = _to_text(rr.get("matched_feat", ""))
        top_reasons_raw.append(rr)

    prompt = f"""
    You are in the mountains and have encountered a wild animal. Speak in a slightly startled and fearful tone.
Based only on the following 'clues' (up to 4) and 'memories', write a natural inner monologue in English consisting of 3 sentences.
Do not add any new facts—use only the information provided.
Mention both the key reasons that led to identifying the animal and any relevant past memories (semantic/episodic).
speak in korean 
[Target Species]
{species}

[Observed Input]
- Color: {", ".join(colors) if colors else "(none)"}
- Shape: {", ".join(shapes) if shapes else "(none)"}

[Top 4 Key Clues ONLY]
{json.dumps(top_reasons_raw, ensure_ascii=False)}

[Semantic Memory Summary]
{'; '.join(sem_facts) if sem_facts else '(none)'}

[Episodic Memory Summary]
{'; '.join(epi_facts) if epi_facts else '(none)'}

[출력 톤 예시]
"음.. 코가 들창코고 색이 갈색이니까 돼지코뱀이겠다. 아, 전에 다큐에서 돼지코뱀이 햇빛을 쬐던 모습을 본 적이 있지."
"""
    text = ask_claude(prompt).strip()
    if not text or text.startswith("(LLM 호출 실패"):
        return generate_observation_reason_one_liner(species, top_reasons)
    text = text.strip('\'"“”')
    return "[객체 인식]\n" + _fmt_lines(text) + "\n"

def generate_final_action_monologue_safe(species: str, decision_sentences: List[str], action_plan_natural: str, features: Dict) -> str:
    fact_block = f"{species}의 현재 상태: 자세는 {features.get('state','unknown')}, 거리는 {features.get('distance','unknown')}, 움직임은 {'움직임 없음' if features.get('speed','none')=='none' else features.get('speed','none')}."
    decision_text = " ".join(decision_sentences or [])
    combined = f"{fact_block}\n결정 경로: {decision_text}"

    prompt = f"""
Speak as if you’re thinking to yourself. You’re mentally retracing the reasoning path that led to your decision. Describe the animal’s current state in one sentence, then naturally explain the reasoning process in about two sentences, and finally state the action you decided to take. Do not add any new information.
You are in the mountains and have encountered a wild animal. Speak in a slightly startled and fearful tone.
{combined}

예) 지금 돼지코뱀이 멀리 있고 가만히 있으니까 일단 도망가자!
"""
    summary = ask_claude(prompt).strip()
    out = summary if summary and not summary.startswith("(LLM 호출 실패") else combined
    return f"[행동 결정]\n{_fmt_lines(out)}\n"

def cognition(sample_input: Dict, save_path: Optional[str] = None) -> None:
    logs: List[str] = []

    animal = resolve_animal_simple(sample_input.get("Animal", ""))

    semantic_data = get_semantic(db, animal)
    if not semantic_data:
        return

    species, reasons = infer_species(sample_input, semantic_data)
    if not species:
        return

    last_species = _load_last_species()
    is_repeat_same = (last_species is not None and last_species == (species or "").strip().lower())

    if is_repeat_same:
        logs.append(generate_brief_observation(sample_input, species))
    else:
        logs.append(generate_observation_monologue_with_claude(sample_input, animal, species, reasons))

    species_row = next((r for r in semantic_data if _row_value(r, "species") == species), None)
    if not species_row:
        return

    features = build_features(sample_input, species_row)

    y_pred, sentences = predict_with_model(features, species)

    raw_plan_for_db = get_action_plan_raw(species, y_pred, sample_input)

    try:
        insert_output(db, species, y_pred, raw_plan_for_db)
    except Exception as e:
        logs.append(f"(DB 저장 실패: {e})")

    action_plan_for_output = get_action_plan_natural(species, y_pred, sample_input)

    logs.append(generate_final_action_monologue_safe(species, sentences or [], action_plan_for_output, features))
    logs.append(action_plan_for_output)

    _save_last_species(species)

    if save_path:
        formatted_output = "\n\n".join(block.strip() for block in logs if block.strip())
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(formatted_output.strip() + "\n") 
