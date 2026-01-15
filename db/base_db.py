import uuid

from django.db import models

from db.user import User
from utils.date_util import DateUtil


class CustomBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class BaseCreatorModel(CustomBaseModel):
    created_at = models.DateTimeField(auto_now_add=True, default=DateUtil.get_current_time)
    created_by = models.ForeignKey(
        User,
        nullable=False,
        max_length=36,
        on_delete=models.CASCADE,
        related_name="updated_%(class)s_set"
    )

    def set_audit_fields(self, user_id: str):
        self.created_by = user_id
        self.created_at = DateUtil.get_current_time()

    class Meta:
        abstract = True

class BaseUpdaterModel(BaseCreatorModel):
    updated_at = models.DateTimeField(auto_now=True, default=DateUtil.get_current_time)
    updated_by = user = models.ForeignKey(
        User,
        nullable=False,
        max_length=36,
        on_delete=models.CASCADE,
        related_name="updated_%(class)s_set"
    )

    def set_audit_fields(self, user_id: str):
        if not self.created_at:
            self.created_at = DateUtil.get_current_time()
        if not self.created_by:
            self.created_by = user_id
        self.updated_by = user_id
        self.updated_at = DateUtil.get_current_time()

    class Meta:
        abstract = True