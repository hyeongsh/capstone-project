INSERT INTO semantic_memory (
  animal, species, climbs_trees, group_behavior, swimming_ability, flight_ability,
  toxicity, avoidance_tendency, aggression_tendency, risk_level, speed,
  vision_sensitivity, hearing_sensitivity, color_weights, shape_weights
) VALUES
('bear', 'asiatic black bear', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'high', 'medium', 'medium', 'high',
 jsonb_build_object('black', 2.0, 'white chest patch', 2.0),
 jsonb_build_object('round ears', 1.5, 'large body', 1.5)),
('bear', 'brown bear', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'high', 'medium', 'medium', 'high',
 jsonb_build_object('brown', 2.0, 'dark fur', 1.5),
 jsonb_build_object('hump shoulder', 1.8, 'big paws', 1.5)),
('bear', 'cubs bear', TRUE, FALSE, TRUE, FALSE, FALSE, TRUE, FALSE, 'medium', 'slow', 'medium', 'high',
 jsonb_build_object('dark brown', 2.0, 'small size', 1.5),
 jsonb_build_object('short snout', 1.3, 'round ears', 1.2));

INSERT INTO semantic_memory (
  animal, species, climbs_trees, group_behavior, swimming_ability, flight_ability,
  toxicity, avoidance_tendency, aggression_tendency, risk_level, speed,
  vision_sensitivity, hearing_sensitivity, color_weights, shape_weights
) VALUES
('boar', 'korean wild boar', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'high', 'medium', 'low', 'medium',
 jsonb_build_object('brown', 2.0, 'black stripe', 1.5),
 jsonb_build_object('tusk', 2.0, 'stout body', 1.8)),
('boar', 'mountain boar', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'high', 'medium', 'low', 'medium',
 jsonb_build_object('dark gray', 2.0, 'muddy fur', 1.5),
 jsonb_build_object('curved tusk', 2.0, 'small tail', 1.2)),
('boar', 'young boar', FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, 'medium', 'medium', 'medium', 'medium',
 jsonb_build_object('striped', 2.0, 'light brown', 1.5),
 jsonb_build_object('small size', 1.3, 'short legs', 1.2));

INSERT INTO semantic_memory (
  animal, species, climbs_trees, group_behavior, swimming_ability, flight_ability,
  toxicity, avoidance_tendency, aggression_tendency, risk_level, speed,
  vision_sensitivity, hearing_sensitivity, color_weights, shape_weights
) VALUES
('deer', 'sika deer', FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, 'medium', 'fast', 'high', 'high',
 jsonb_build_object('reddish brown', 2.0, 'white spots', 1.8),
 jsonb_build_object('slender body', 1.5, 'antler', 1.8)),
('deer', 'roe deer', FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, 'medium', 'fast', 'high', 'high',
 jsonb_build_object('light brown', 2.0, 'white rump', 1.5),
 jsonb_build_object('small antler', 1.3, 'long legs', 1.2)),
('deer', 'water deer', FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, 'medium', 'medium', 'high', 'medium',
 jsonb_build_object('brownish gray', 2.0, 'pale belly', 1.5),
 jsonb_build_object('fang teeth', 2.0, 'slender body', 1.5));

INSERT INTO semantic_memory (
  animal, species, climbs_trees, group_behavior, swimming_ability, flight_ability,
  toxicity, avoidance_tendency, aggression_tendency, risk_level, speed,
  vision_sensitivity, hearing_sensitivity, color_weights, shape_weights
) VALUES
('bird', 'magpie', FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, 'low', 'fast', 'high', 'high',
 jsonb_build_object('black', 2.0, 'white', 1.8),
 jsonb_build_object('long tail', 2.0, 'sharp beak', 1.3)),
('bird', 'woodpecker', TRUE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, 'low', 'medium', 'high', 'medium',
 jsonb_build_object('black', 1.5, 'red crown', 2.0),
 jsonb_build_object('strong beak', 2.0, 'short tail', 1.3)),
('bird', 'owl', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, 'medium', 'slow', 'high', 'high',
 jsonb_build_object('brown', 2.0, 'gray', 1.5),
 jsonb_build_object('large eyes', 2.0, 'round face', 1.5));

INSERT INTO semantic_memory (
  animal, species, climbs_trees, group_behavior, swimming_ability, flight_ability,
  toxicity, avoidance_tendency, aggression_tendency, risk_level, speed,
  vision_sensitivity, hearing_sensitivity, color_weights, shape_weights
) VALUES
('rabbit', 'mountain hare', FALSE, FALSE, TRUE, FALSE, FALSE, TRUE, FALSE, 'low', 'fast', 'high', 'high',
 jsonb_build_object('gray', 2.0, 'white belly', 1.5),
 jsonb_build_object('long ears', 2.0, 'short tail', 1.3)),
('rabbit', 'field rabbit', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, 'low', 'fast', 'medium', 'high',
 jsonb_build_object('brown', 2.0, 'tan', 1.5),
 jsonb_build_object('long ears', 1.8, 'slim body', 1.2)),
('rabbit', 'korean hare', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, 'low', 'fast', 'medium', 'high',
 jsonb_build_object('brown gray', 2.0, 'white underfur', 1.5),
 jsonb_build_object('slender legs', 1.3, 'long ears', 1.5));

INSERT INTO episodic_memory (id, animal, impact, event_date, context) VALUES
('eb01', 'asiatic black bear', 3, '2023-06-10 07:30:00',
 jsonb_build_array('Hiking', 'Unexpected encounter', 'Bear was climbing a tree', 'Shock')),
('eb02', 'asiatic black bear', 2, '2024-04-03 09:00:00',
 jsonb_build_array('Forest edge', 'Heard rustling sound', 'Saw bear tracks nearby', 'Caution')),
('eb03', 'brown bear', 4, '2022-09-15 18:40:00',
 jsonb_build_array('News', 'Bear attack incident', 'Hiker injured near valley', 'Fear')),
('eb04', 'brown bear', 3, '2023-10-19 11:15:00',
 jsonb_build_array('Mountain path', 'Bear visible across river', 'Kept distance quietly', 'Alert')),
('eb05', 'cubs bear', 2, '2024-05-21 09:10:00',
 jsonb_build_array('Trail camera', 'Cub playing alone', 'Mother nearby', 'Caution')),
('eb06', 'cubs bear', 3, '2023-08-12 15:00:00',
 jsonb_build_array('Observation', 'Cub climbed a tree', 'Looked curious', 'Amazement'));

INSERT INTO episodic_memory (id, animal, impact, event_date, context) VALUES
('eb07', 'korean wild boar', 4, '2023-08-03 21:00:00',
 jsonb_build_array('Night walk', 'Sudden appearance', 'Ran across trail', 'Panic')),
('eb08', 'korean wild boar', 3, '2024-02-22 06:20:00',
 jsonb_build_array('Village road', 'Boar searching trash bin', 'Loud snorting', 'Fear')),
('eb09', 'mountain boar', 3, '2022-11-12 06:45:00',
 jsonb_build_array('Mountain village', 'Raided crops', 'Left footprints near stream', 'Anxiety')),
('eb10', 'mountain boar', 2, '2024-01-16 08:00:00',
 jsonb_build_array('Morning hike', 'Heard boar squeal', 'Did not see but sensed movement', 'Tension')),
('eb11', 'young boar', 2, '2024-04-02 15:20:00',
 jsonb_build_array('Forest road', 'Boar family crossing', 'Kept safe distance', 'Relief')),
('eb12', 'young boar', 1, '2023-09-09 13:10:00',
 jsonb_build_array('Countryside', 'Saw piglets running together', 'They disappeared fast', 'Amusement'));

INSERT INTO episodic_memory (id, animal, impact, event_date, context) VALUES
('eb13', 'sika deer', 2, '2023-10-09 16:50:00',
 jsonb_build_array('Forest path', 'Herd grazing quietly', 'Watched from afar', 'Calm')),
('eb14', 'sika deer', 1, '2024-03-15 07:30:00',
 jsonb_build_array('Early morning', 'Fawn hiding near bush', 'Peaceful moment', 'Warmth')),
('eb15', 'roe deer', 1, '2024-03-18 08:25:00',
 jsonb_build_array('Morning fog', 'Roe deer crossing trail', 'Quick movement', 'Admiration')),
('eb16', 'roe deer', 2, '2023-07-30 17:45:00',
 jsonb_build_array('Field edge', 'Deer startled by dog bark', 'Ran into forest', 'Surprise')),
('eb17', 'water deer', 3, '2023-12-11 19:05:00',
 jsonb_build_array('Car road', 'Deer jumped across road', 'Driver braked suddenly', 'Shock')),
('eb18', 'water deer', 2, '2024-02-02 20:00:00',
 jsonb_build_array('Wetland near hill', 'Spotted alone in dusk', 'Eyes reflecting light', 'Unease'));

INSERT INTO episodic_memory (id, animal, impact, event_date, context) VALUES
('eb19', 'magpie', 1, '2023-05-01 10:00:00',
 jsonb_build_array('Morning walk', 'Magpie calling loudly', 'Perched on branch', 'Peaceful')),
('eb20', 'magpie', 1, '2024-02-05 08:15:00',
 jsonb_build_array('Village road', 'Two magpies chasing each other', 'Sign of spring', 'Joy')),
('eb21', 'woodpecker', 1, '2024-02-14 09:15:00',
 jsonb_build_array('Winter forest', 'Heard tapping sound', 'Saw red crown', 'Curiosity')),
('eb22', 'woodpecker', 2, '2023-10-05 11:50:00',
 jsonb_build_array('Trail rest stop', 'Woodpecker drumming on tree', 'Echoed clearly', 'Interest')),
('eb23', 'owl', 2, '2022-11-30 22:40:00',
 jsonb_build_array('Night hike', 'Eyes glowing in dark', 'Soft hooting nearby', 'Unease')),
('eb24', 'owl', 1, '2023-12-24 23:10:00',
 jsonb_build_array('Cabin night', 'Heard distant hoot', 'Felt eerie calmness', 'Curiosity'));

INSERT INTO episodic_memory (id, animal, impact, event_date, context) VALUES
('eb25', 'mountain hare', 1, '2023-09-20 07:55:00',
 jsonb_build_array('Morning forest', 'Hopped across path', 'White belly visible', 'Delight')),
('eb26', 'mountain hare', 2, '2024-04-08 18:10:00',
 jsonb_build_array('Evening hill', 'Hare sitting still near bush', 'Ears twitching', 'Calm')),
('eb27', 'field rabbit', 1, '2024-01-10 14:30:00',
 jsonb_build_array('Countryside', 'Rabbit eating grass', 'Approached slowly', 'Joy')),
('eb28', 'field rabbit', 1, '2023-06-02 08:10:00',
 jsonb_build_array('Field edge', 'Two rabbits running together', 'Morning dew', 'Peace')),
('eb29', 'korean hare', 2, '2023-04-07 17:25:00',
 jsonb_build_array('Hiking', 'Ran away quickly', 'Hidden under bush', 'Surprise')),
('eb30', 'korean hare', 1, '2024-02-25 06:40:00',
 jsonb_build_array('Early dawn', 'Saw hare tracks on snow', 'Beautiful silence', 'Serenity'));

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'green', 0.6,
        'light green', 0.5,
        'brown', 0.7,
        'grey', 0.6
    ),
    shape_weights = jsonb_build_object(
        'long body', 0.7,
        'slender body', 0.6,
        'pointed snout', 0.5,
        'thin', 0.7
    )
WHERE species = 'asian vine snake' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'red', 0.6,
        'brown', 0.8,
        'black', 0.7,
        'grey', 0.5
    ),
    shape_weights = jsonb_build_object(
        'stripes', 0.5,
        'blotches', 0.6,
        'checkerboard pattern', 0.5,
        'long', 0.6
    )
WHERE species = 'corn snake' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'green', 0.6,
        'yellow', 0.5,
        'brown', 0.6,
        'grey', 0.6
    ),
    shape_weights = jsonb_build_object(
        'large eyes', 0.5,
        'slender body', 0.6,
        'long', 0.7,
        'thin', 0.6
    )
WHERE species = 'boomslang' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'red', 0.7,
        'black', 0.7,
        'yellow', 0.6,
        'brown', 0.6,
        'grey', 0.5
    ),
    shape_weights = jsonb_build_object(
        'slender body', 0.6,
        'banded pattern', 0.6,
        'thin', 0.6,
        'long', 0.7
    )
WHERE species = 'coral snake' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'yellow', 0.7,
        'brown', 0.8,
        'black', 0.6,
        'grey', 0.6
    ),
    shape_weights = jsonb_build_object(
        'stripes', 0.6,
        'long body', 0.7,
        'thin', 0.6,
        'round head', 0.6
    )
WHERE species = 'yellow rat snake' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'red', 0.6,
        'black', 0.7,
        'white', 0.6,
        'yellow', 0.5,
        'brown', 0.7
    ),
    shape_weights = jsonb_build_object(
        'chain pattern', 0.5,
        'banded pattern', 0.6,
        'thin', 0.6,
        'long', 0.6
    )
WHERE species = 'kingsnake' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'gray', 0.7,
        'black', 0.6,
        'brown', 0.8,
        'green', 0.5
    ),
    shape_weights = jsonb_build_object(
        'stripes', 0.5,
        'blotches', 0.5,
        'thick body', 0.6,
        'triangular head', 0.8,
        'diamond-shaped head', 0.8
    )
WHERE species = 'viper' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'gray', 0.7,
        'black', 0.8,
        'brown', 0.6
    ),
    shape_weights = jsonb_build_object(
        'very long', 0.8,
        'slender body', 0.7,
        'coffin-shaped head', 0.6,
        'thin', 0.7
    )
WHERE species = 'black mamba' AND animal = 'snake';

UPDATE semantic_memory
SET
    color_weights = jsonb_build_object(
        'grey', 1.0,
        'brown', 1.0,
        'black', 0.9,
        'green', 0.5
    ),
    shape_weights = jsonb_build_object(
        'thin', 1.0,
        'long', 0.9,
        'round head', 0.9,
        'diamond-shaped head', 1.0,
        'slender body', 0.8
    )
WHERE species = 'hognose snake' AND animal = 'snake';
