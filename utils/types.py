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

class DocumentType(Enum):
    CERTIFICATE = "Certificate"
    DIPLOMA = "Diploma"
    lICENSE = "License"
    CONTRACT = "Contract"
    REPORT = "Report"
    OTHER = "Other"

    @classmethod
    def get_all_values(cls):
        return [doctype.value for doctype in cls]

