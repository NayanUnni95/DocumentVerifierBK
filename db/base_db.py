import uuid

from django.db import models

from utils.date_util import DateUtil


class CustomBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class BaseCreatorModel(CustomBaseModel):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'api.User',
        null=False,
        on_delete=models.CASCADE,
        related_name="created_%(class)s_set"
    )

    def set_audit_fields(self, user_id: str):
        self.created_by = user_id
        self.created_at = DateUtil.get_current_time()

    class Meta:
        abstract = True

class BaseUpdaterModel(BaseCreatorModel):
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'api.User',
        null=False,
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