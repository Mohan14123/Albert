class IntegrationError(Exception):
    pass

class TokenExpired(IntegrationError):
    pass

class ProviderUnavailable(IntegrationError):
    pass

class InvalidOAuthCode(IntegrationError):
    pass

class WebhookVerificationFailed(IntegrationError):
    pass
