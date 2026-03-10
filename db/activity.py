from django.db import models
from db.base_db import CustomBaseModel
from utils.types import ActivityType

class Activity(CustomBaseModel):
    user = models.ForeignKey(
        'api.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activities"
    )
    doc_owner = models.ForeignKey(
        'api.User',
        null=False,
        on_delete=models.CASCADE,
        related_name="document_activities"
    )
    doc = models.ForeignKey(
        'api.Document',
        null=False,
        on_delete=models.CASCADE,
        related_name="activities"
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices(),
        default=ActivityType.UPLOAD.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity"
        app_label = 'api'
