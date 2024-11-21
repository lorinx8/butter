from typing import List, Optional
from fastapi import HTTPException
from app.repositories.dict_group_repository import DictGroupRepository
from app.schemas.dict import DictGroupCreate, DictGroupUpdate
from app.repositories.models import DictGroup


class DictGroupService:
    def __init__(self, group_repository: DictGroupRepository):
        self.group_repository = group_repository

    def create_group(self, group_data: DictGroupCreate) -> DictGroup:
        # 如果指定了parent_id,验证父组是否存在
        if group_data.parent_id:
            parent = self.group_repository.get_by_id(group_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404, detail="Parent group not found")

        # 如果指定了code,检查是否已存在
        if group_data.code:
            existing = self.group_repository.get_by_code(group_data.code)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Group code already exists")

        return self.group_repository.create(
            name=group_data.name,
            code=group_data.code,
            description=group_data.description,
            is_system=group_data.is_system,
            parent_id=group_data.parent_id
        )

    def get_group(self, group_id: str) -> DictGroup:
        group = self.group_repository.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group

    def get_groups(self, skip: int = 0, limit: int = 100) -> List[DictGroup]:
        return self.group_repository.get_all(skip=skip, limit=limit)

    def get_children(self, parent_id: Optional[str]) -> List[DictGroup]:
        return self.group_repository.get_children(parent_id)

    def update_group(self, group_id: str, group_data: DictGroupUpdate) -> DictGroup:
        # 验证组是否存在
        existing = self.group_repository.get_by_id(group_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Group not found")

        # 如果要更新code,检查新code是否已存在
        if group_data.code:
            code_exists = self.group_repository.get_by_code(group_data.code)
            if code_exists and code_exists.id != group_id:
                raise HTTPException(
                    status_code=400, detail="Group code already exists")

        update_data = group_data.model_dump(exclude_unset=True)
        group = self.group_repository.update(group_id, **update_data)
        return group

    def delete_group(self, group_id: str) -> bool:
        # 检查是否有子组
        children = self.group_repository.get_children(group_id)
        if children:
            raise HTTPException(
                status_code=400, detail="Cannot delete group with children")

        if not self.group_repository.delete(group_id):
            raise HTTPException(status_code=404, detail="Group not found")
        return True
