from enum import Enum


class AffiliationType(Enum):
    UNIVERSITY = "University"
    INSTITUTION = "Institution"
    ORGANIZATION = "Organization"

    @classmethod
    def get_all_values(cls):
        return [affiliation.value for affiliation in cls]
    

class OAuthProviderType(Enum):
    GOOGLE = "Google"
    FACEBOOK = "Facebook"

    @classmethod
    def get_all_values(cls):
        return [provider.value for provider in cls]