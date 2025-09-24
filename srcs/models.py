# ORM 모델 (SQLAlchemy Base)

from sqlalchemy import Column, Integer, SmallInteger, Float, String, JSON, BigInteger, ForeignKey
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