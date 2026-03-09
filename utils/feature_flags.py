class FeatureFlags:
    """
    Centralized configuration for feature flags.
    Allows enabling/disabling features without modifying environment variables.
    """
    ENABLE_OCR = True
    ENABLE_USER_REGISTRATION = True
    ENABLE_MOCK_STORAGE = False
