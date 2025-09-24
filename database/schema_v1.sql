-- 0) 유틸: 상태 enum
DO $$ BEGIN
  CREATE TYPE detection_status AS ENUM ('NOTHING','REVALIDATION','SPECIFIC');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 1) 장기기억: 객체 사전
CREATE TABLE IF NOT EXISTS objects (
  object_id      SERIAL PRIMARY KEY,
  name           TEXT NOT NULL UNIQUE,              -- canonical: 'fox'
  importance     SMALLINT NOT NULL DEFAULT 2,       -- 1=LOW,2=MED,3=HIGH
  danger_level   REAL NOT NULL DEFAULT 0,           -- 0.0~1.0
  base_emotion   JSONB NOT NULL                     -- {"curiosity":0.4,"fear":0.6}
);

-- 2) 라벨 매핑 (모델 라벨 → canonical 객체)
CREATE TABLE IF NOT EXISTS label_aliases (
  alias          TEXT PRIMARY KEY,
  object_id      INT  NOT NULL REFERENCES objects(object_id) ON DELETE CASCADE
);

-- 3) (선택) 행동정책
CREATE TABLE IF NOT EXISTS action_policies (
	policy_id      SERIAL PRIMARY KEY,
	object_id      INT NOT NULL REFERENCES objects(object_id) ON DELETE CASCADE,
	emotion_rule   JSONB NOT NULL, -- {"fear": ">0.7", "curiosity": "<0.3"}
	action         TEXT NOT NULL, -- "escape" | "observe" | "approach"
	action_params  JSONB DEFAULT '{}' -- {"speed": "fast", "direction": "back"}
);

-- 4) 사건 기록 (확정 episode)
CREATE TABLE IF NOT EXISTS episodes (
  episode_id     BIGSERIAL PRIMARY KEY,
  object_id      INT    NOT NULL REFERENCES objects(object_id),
  context        JSONB  NOT NULL,                   -- {"distance":"near","speed":0.8,"sudden":true,...}
  emotions_final JSONB  NOT NULL,                   -- {"fear":0.85,"curiosity":0.2,"surprise":0.8}
  action         TEXT   NOT NULL,                   -- 'escape' | 'observe' | ...
  action_params  JSONB  NOT NULL DEFAULT '{}'      -- {"speed":"fast","direction":"back"}
);
