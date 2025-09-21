from repository.implementation.objects_repository_impl import ObjectsRepositoryImpl
from repository.implementation.label_aliases_repository_impl import LabelAliasesRepositoryImpl
from service.memory_manager import MemoryManager

def create_memory_manager():
    objects_repo = ObjectsRepositoryImpl()
    label_aliases_repo = LabelAliasesRepositoryImpl()
    return MemoryManager(objects_repo, label_aliases_repo)