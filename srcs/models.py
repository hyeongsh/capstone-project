# ORM 모델 (SQLAlchemy Base)

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    JSON,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db import Base


class Object(Base):
	__tablename__ = 'objects'

	object_id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	importance = Column(SmallInteger, nullable=False, default=2)
	danger_level = Column(Float, nullable=False, default=0.0)
	base_emotion = Column(JSON, nullable=False)

	label_aliases = relationship('LabelAlias', back_populates='object', cascade='all, delete-orphan')
	action_policies = relationship('ActionPolicy', back_populates='object', cascade='all, delete-orphan')
	episodes = relationship('Episode', back_populates='object', cascade='all, delete-orphan')


class LabelAlias(Base):
	__tablename__ = 'label_aliases'
	
	alias = Column(String, primary_key=True, index=True)
	object_id = Column(Integer, ForeignKey('objects.object_id', ondelete='CASCADE'), nullable=False)
	
	object = relationship('Object', back_populates='label_aliases')


class ActionPolicy(Base):
	__tablename__ = 'action_policies'

	id = Column(Integer, primary_key=True, index=True)
	object_id = Column(Integer, ForeignKey('objects.object_id', ondelete='CASCADE'), nullable=False)
	policy_data = Column(JSON, nullable=False)

	object = relationship('Object', back_populates='action_policies')


class Episode(Base):
	__tablename__ = 'episodes'

	id = Column(BigInteger, primary_key=True, index=True)
	object_id = Column(Integer, ForeignKey('objects.object_id', ondelete='CASCADE'), nullable=False)

	object = relationship('Object', back_populates='episodes')


class SemanticMemory(Base):
	__tablename__ = 'semantic_memory'
	__table_args__ = (
		CheckConstraint("risk_level IN ('low','medium','high')", name='ck_semantic_memory_risk_level'),
		CheckConstraint("speed IN ('slow','medium','fast')", name='ck_semantic_memory_speed'),
		CheckConstraint("vision_sensitivity IN ('low','medium','high')", name='ck_semantic_memory_vision'),
		CheckConstraint("hearing_sensitivity IN ('low','medium','high')", name='ck_semantic_memory_hearing'),
	)

	id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
	animal = Column(String(50), nullable=False)
	species = Column(String(100))
	climbs_trees = Column(Boolean, default=False)
	group_behavior = Column(Boolean, default=False)
	swimming_ability = Column(Boolean, default=False)
	flight_ability = Column(Boolean, default=False)
	toxicity = Column(Boolean, default=False)
	avoidance_tendency = Column(Boolean, default=False)
	aggression_tendency = Column(Boolean, default=False)
	risk_level = Column(String(10))
	speed = Column(String(10))
	vision_sensitivity = Column(String(10))
	hearing_sensitivity = Column(String(10))
	color_weights = Column(JSONB)
	shape_weights = Column(JSONB)


class ModelOutput(Base):
	__tablename__ = 'model_output'

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	animal = Column(String(50), nullable=False)
	predicted_behavior = Column(String(100))
	action_plan = Column(Text)


class EpisodicMemory(Base):
	__tablename__ = 'episodic_memory'

	id = Column(String(50), primary_key=True, index=True)
	animal = Column(String(50), nullable=False)
	impact = Column(Integer)
	event_date = Column(DateTime)
	context = Column(JSONB)
