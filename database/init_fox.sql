INSERT INTO objects (name, importance, danger_level, base_emotion)
VALUES ('fox', 3, 0.6, '{"curiosity":0.4, "fear":0.6}');

INSERT INTO label_aliases (alias, object_id)
SELECT alias, o.object_id
FROM objects o, 
	(VALUES
		('red fox'),
		('kit fox'),
		('grey fox')
	) AS v(alias)
WHERE o.name = 'fox'
ON CONFLICT DO NOTHING;

INSERT INTO action_policies (object_id, emotion_rule, action, action_params)
SELECT o.object_id,
	'{"fear":">curiosity"}',
	'escape',
	'{"speed":"fast"}'
FROM objects o
WHERE o.name='fox';

INSERT INTO action_policies (object_id, emotion_rule, action, action_params)
SELECT o.object_id,
	'{"curiosity":">fear"}',
	'approach',
	'{"speed":"slow"}'
FROM objects o
WHERE o.name='fox';