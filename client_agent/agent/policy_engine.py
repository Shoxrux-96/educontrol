import json
import logging
from typing import Optional

from agent.config import config

logger = logging.getLogger(__name__)


class PolicyEngine:
    def __init__(self):
        self.policies = {}
        self._load_cache()

    def _load_cache(self):
        try:
            with open(config.policy_cache_file, "r") as f:
                self.policies = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.policies = {}

    def _save_cache(self):
        try:
            with open(config.policy_cache_file, "w") as f:
                json.dump(self.policies, f)
        except Exception as e:
            logger.error(f"Failed to cache policies: {e}")

    def update(self, policies: list):
        for p in policies:
            self.policies[p["id"]] = p
        self._save_cache()
        logger.info(f"Policy engine updated with {len(policies)} policies")

    def get_policy(self, policy_id: str) -> Optional[dict]:
        return self.policies.get(policy_id)

    def get_policies_by_type(self, policy_type: str) -> list:
        return [
            p for p in self.policies.values()
            if p.get("type") == policy_type
        ]

    def clear(self):
        self.policies = {}
        self._save_cache()
