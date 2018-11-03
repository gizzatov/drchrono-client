import json

from social_core.tests.backends.oauth import OAuth2Test

from application.apps.oauth.backends import DrchronoOAuth2


class DrchronoOAuth2Test(OAuth2Test):
    backend_path = 'application.apps.oauth.backends.DrchronoOAuth2'
    user_data_url = DrchronoOAuth2.USER_DATA_URL
    expected_username = 'test_username'
    access_token_body = json.dumps({
        'access_token': 'foobar',
        'token_type': 'bearer'
    })
    user_data_body = json.dumps({
        "username": "test_username",
        "is_staff": False,
        "is_doctor": True,
        "doctor": 210082,
        "id": 266228,
        "practice_group": 243514,
    })

    def test_login(self):
        self.do_login()

    def test_partial_pipeline(self):
        self.do_partial_pipeline()
