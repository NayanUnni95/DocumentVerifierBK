from django.db import models

from db.base_db import CustomBaseModel, BaseCreatorModel, BaseUpdaterModel
from utils.types import AffiliationType


def default_user_settings():
    return {
        "allow_notification": False,
        "verification_alert": False,
        "weekly_summary": False,
        "allow_two_factor": False,
    }


class User(CustomBaseModel):
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=True)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    settings = models.JSONField(default=default_user_settings)

    class Meta:
        db_table = "user"
        app_label = 'api'


class Affiliation(BaseUpdaterModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="affiliation",
    )
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=50,
        choices=AffiliationType.choices(),
        default=AffiliationType.ORGANIZATION.value,
    )
    website = models.URLField()

    class Meta:
        db_table = "affiliation"
        app_label = 'api'


class UserOAuthCredential(BaseCreatorModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oauth_credential",
    )
    provider = models.CharField(max_length=50)
    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()

    class Meta:
        db_table = "user_oauth_credential"
        app_label = 'api'
        constraints = [
            models.UniqueConstraint(
                fields=["user", "provider"],
                name="unique_user_provider",
            )
        ]
