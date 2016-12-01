from .config import OWNERS
from .config import REPOSITORIES


class DockerhubHelper:
    @staticmethod
    def username_for_owner(owner):
        return OWNERS.get(owner)

    @staticmethod
    def username_for_repository(repository):
        return REPOSITORIES.get(repository)
