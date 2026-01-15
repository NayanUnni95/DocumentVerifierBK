from django.db import models

from db.base_db import BaseUpdaterModel
from utils.types import DocumentType


def default_doc_settings():
    return {
        "is_pubic": False,
    }


class Document(BaseUpdaterModel):
    title = models.CharField(max_length=150)
    type = models.CharField(
        max_length=50,
        choices=DocumentType.choices(),
        default=DocumentType.OTHER.value
    )
    description = models.CharField(max_length=300, null=True, blank=True)
    source_url = models.URLField(null=False)
    ocr_content = models.JSONField(null=False, blank=False)
    recipient_name = models.CharField(max_length=150)
    recipient_email = models.EmailField()
    issuing_affiliation = models.CharField(max_length=200)
    settings = models.JSONField(default=default_doc_settings)
    issue_at = models.DateTimeField(auto_now=True)
    expiry_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document"