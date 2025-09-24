# CRUD 함수 모음

from sqlalchemy.orm import Session
from models import Object, LabelAlias, ActionPolicy, Episode

def create_object(db: Session, 
				  name: str, 
				  importance: int = 2,
				  danger_level: float = 0.0,
				  base_emotion: dict = None):
	if base_emotion is None:
		base_emotion = {}
	obj = Object(name = name, importance = importance, danger_level = danger_level, base_emotion = base_emotion)
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj

def get_object_by_id(db: Session, object_id: int):
	return db.query(Object).filter(Object.object_id == object_id).first()

def get_object_by_name(db: Session, name: str):
	return db.query(Object).filter(Object.name == name).first()

def list_objects(db: Session, skip: int = 0, limit: int = 100):
	return db.query(Object).offset(skip).limit(limit).all()

def delete_object(db: Session, object_id: int):
	obj = get_object_by_id(db, object_id)
	if obj:
		db.delete(obj)
		db.commit()
	return obj

def create_label_alias(db: Session, alias: str, object_id: int):
	label_alias = LabelAlias(alias=alias, object_id=object_id)
	db.add(label_alias)
	db.commit()
	db.refresh(label_alias)
	return label_alias

def get_label_alias_by_alias(db: Session, alias: str):
	return db.query(LabelAlias).filter(LabelAlias.alias == alias).first()

def list_label_aliases(db: Session, skip: int = 0, limit: int = 100):
	return db.query(LabelAlias).offset(skip).limit(limit).all()

def delete_label_alias(db: Session, alias: str):
	label_alias = get_label_alias_by_alias(db, alias)
	if label_alias:
		db.delete(label_alias)
		db.commit()
	return label_alias

def create_action_policy(db: Session, object_id: int, policy_data: dict = None):
	if policy_data is None:
		policy_data = {}

	policy = ActionPolicy(object_id = object_id, policy_data = policy_data)
	
	db.add(policy)
	db.commit()
	db.refresh(policy)
	return policy

def get_action_policy_by_id(db: Session, id: int):
	return db.query(ActionPolicy).filter(ActionPolicy.id == id).first()

def get_action_policy_by_object_id(db: Session, object_id: int):
	return db.query(ActionPolicy).filter(ActionPolicy.object_id == object_id).first()

def list_action_policy(db: Session, skip: int = 0, limit: int = 100):
	return db.query(ActionPolicy).offset(skip).limit(limit).all()

def delete_action_policy(db: Session, policy_id: int):
	policy = get_action_policy_by_id(policy_id)
	if policy:
		db.delete(policy)
		db.commit()
	return policy

def create_episode(db: Session, object_id: int):
	episode = Episode(object_id = object_id)
	db.add(episode)
	db.commit()
	db.refresh(episode)
	return episode

def get_episode_by_id(db: Session, id: int):
	return db.query(Episode).filter(Episode.id == id).first()

def list_episodes(db: Session, skip: int = 0, limit: int = 100):
	return db.query(Episode).offset(skip).limit(limit).all()

def delete_episode(db: Session, episode_id: int):
	episode = get_episode_by_id(episode_id)
	if episode:
		db.delete(episode)
		db.commit()
	return episode