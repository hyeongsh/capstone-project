from repository.interface.objects_repository import ObjectsRepository
from repository.interface.label_aliases_repository import LabelAliasesRepository
from collections import deque

class MemoryManager:
	def __init__(
		self, 
		objects_repository: ObjectsRepository, 
		label_aliases_repository: LabelAliasesRepository
	):
		self.obj_repo = objects_repository
		self.alias_repo = label_aliases_repository
		self.recent_dq = deque(maxlen=10)
		self.current_object: str = ""
		
	def validate_object(self, data: list):
		raw_list = []
		return_value = False
		for item in data:
			# 1. label_aliases 를 통해 object 객체 확인
			label = item.get("label")
			prob = item.get("prob")
			memory_object_id = self.alias_repo.get_object_id_by_alias(label)
			new_object = self.obj_repo.get_name_by_id(memory_object_id)
			if new_object:
				self.recent_dq.append(new_object)
				# 2. 5번 연속 존재한 객체인지 확인
				if new_object != self.current_object:
					if self.recent_dq.count(new_object) >= 5:
						# TODO: 추후에 중요도 기반으로 현재 보고 있는 객체를 변경하는 로직이 들어가면 좋을 듯
						self.current_object = new_object
						return_value = True
			raw_list.append({"label": new_object, "prob": prob})

		if self.recent_dq.count(self.current_object) < 5:
			self.current_object = "" 
		# 3. 현재 객체를 제대로 탐색할 것인가에 대한 반환 결과
		return return_value