from social_core.backends.oauth import BaseOAuth2


class DrchronoOAuth2(BaseOAuth2):
    """Drchrono OAuth authentication backend"""
    name = 'drchrono'
    AUTHORIZATION_URL = 'https://drchrono.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://drchrono.com/o/token/'
    SCOPE_SEPARATOR = ' '
    DEFAULT_SCOPE = ['patients:read', 'patients:summary:read']
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_URI = 'http://localhost:3000'
    REDIRECT_STATE = False
    STATE_PARAMETER = False
    USER_DATA_URL = 'https://drchrono.com/api/users/current'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_uri = self.REDIRECT_URI

    def get_user_details(self, response):
        """Return user details from Drchrono account"""
        return {'username': response.get('username'),
                'email': response.get('email') or '',
                'first_name': ''}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        headers = {'Authorization': f'Bearer {access_token}'}
        return self.get_json(self.USER_DATA_URL, headers=headers)
