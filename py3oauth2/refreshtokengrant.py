# -*- coding: utf-8 -*-

from py3oauth2.errors import (
    AccessDenied,
    UnauthorizedClient,
)
from py3oauth2.message import (
    AccessTokenResponse,
    Parameter,
    Request,
)


__all__ = ['RefreshTokenRequest']


class RefreshTokenRequest(Request):
    response = AccessTokenResponse

    grant_type = Parameter(str, required=True,
                           default='refresh_token', editable=False)
    refresh_token = Parameter(str, required=True)
    scope = Parameter(str)

    def answer(self, provider, owner):
        previous = provider.store.get_access_token_by_refresh_token(
            self.refresh_token)
        if previous is None:
            raise AccessDenied(self)

        if not provider.authorize_client(previous.get_client()):
            raise UnauthorizedClient(self)

        if self.scope:
            scope = provider.normalize_scope(self.scope)
            if not previous.get_scope().issuperset(scope):
                raise AccessDenied(self)
        else:
            scope = previous.get_scope()

        token = provider.store.issue_access_token(previous.get_client(),
                                                  previous.get_owner(),
                                                  scope)
        provider.store.discard_access_token(previous)

        return self.response.from_dict(self, {
            'access_token': token.get_token(),
            'token_type': token.get_type(),
            'expires_in': token.get_expires_in(),
            'refresh_token': token.get_refresh_token(),
            'scope': ' '.join(token.get_scope()),
        })