from abc import ABC, abstractmethod

class LabelAliasesRepository(ABC):
	
	@abstractmethod
	def get_object_id_by_alias(self, alias: str) -> int:
		pass
