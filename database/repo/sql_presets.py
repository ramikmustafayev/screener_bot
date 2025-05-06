from database.repo.base import BaseRepo
from database.models import SQLPreset


class SQLPresetsRepo(BaseRepo):
    model=SQLPreset
