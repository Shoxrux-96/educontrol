from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.policy import Policy, PolicyAssignment, PolicyType
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyAssignRequest,
    PolicyAssignmentResponse,
)


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_policy(self, data: PolicyCreate, user_id: str) -> PolicyResponse:
        policy = Policy(
            name=data.name,
            description=data.description,
            policy_type=PolicyType(data.policy_type),
            config=data.config,
            created_by=user_id,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return PolicyResponse.model_validate(policy)

    async def list_policies(self) -> List[PolicyResponse]:
        result = await self.db.execute(
            select(Policy).order_by(Policy.created_at.desc())
        )
        policies = result.scalars().all()
        return [PolicyResponse.model_validate(p) for p in policies]

    async def get_policy(self, policy_id: str) -> PolicyResponse:
        result = await self.db.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        policy = result.scalar_one_or_none()
        if not policy:
            raise ValueError("Policy not found")
        return PolicyResponse.model_validate(policy)

    async def update_policy(self, policy_id: str, data: PolicyUpdate) -> PolicyResponse:
        result = await self.db.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        policy = result.scalar_one_or_none()
        if not policy:
            raise ValueError("Policy not found")

        if data.name is not None:
            policy.name = data.name
        if data.description is not None:
            policy.description = data.description
        if data.config is not None:
            policy.config = data.config
        if data.is_active is not None:
            policy.is_active = data.is_active

        await self.db.commit()
        await self.db.refresh(policy)
        return PolicyResponse.model_validate(policy)

    async def delete_policy(self, policy_id: str):
        result = await self.db.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        policy = result.scalar_one_or_none()
        if not policy:
            raise ValueError("Policy not found")
        assignments = await self.db.execute(
            select(PolicyAssignment).where(PolicyAssignment.policy_id == policy_id)
        )
        for a in assignments.scalars().all():
            await self.db.delete(a)
        await self.db.delete(policy)
        await self.db.commit()

    async def assign_policy(
        self, policy_id: str, data: PolicyAssignRequest, user_id: str
    ) -> PolicyAssignmentResponse:
        result = await self.db.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Policy not found")

        assignment = PolicyAssignment(
            policy_id=policy_id,
            target_type=data.target_type,
            target_id=data.target_id,
            assigned_by=user_id,
        )
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return PolicyAssignmentResponse.model_validate(assignment)

    async def unassign_policy(self, assignment_id: str):
        result = await self.db.execute(
            select(PolicyAssignment).where(PolicyAssignment.id == assignment_id)
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise ValueError("Assignment not found")
        await self.db.delete(assignment)
        await self.db.commit()

    async def get_policies_for_computer(self, computer_id: str) -> List[PolicyResponse]:
        result = await self.db.execute(
            select(PolicyAssignment).where(
                (PolicyAssignment.target_type == "all")
                | (
                    (PolicyAssignment.target_type == "computer")
                    & (PolicyAssignment.target_id == computer_id)
                )
            )
        )
        assignments = result.scalars().all()
        policy_ids = [a.policy_id for a in assignments]
        if not policy_ids:
            return []

        result = await self.db.execute(
            select(Policy).where(Policy.id.in_(policy_ids), Policy.is_active == True)
        )
        policies = result.scalars().all()
        return [PolicyResponse.model_validate(p) for p in policies]
