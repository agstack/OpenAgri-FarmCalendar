from urllib.parse import urljoin
from django.conf import settings

import requests


class AgstackClient:
    """
    A simple client for interacting with the AgStack API.
    """

    def __init__(self):
        self.asset_api_url = settings.AGSTACK_ASSET_REGISTY_API_URL
        self.user = settings.AGSTACK_USER
        self.password = settings.AGSTACK_PASS
        self.access_token = None
        self.login_url = urljoin(self.asset_api_url, settings.AGSTACK_ENDPOINTS['login'])
        self.register_field_url = urljoin(self.asset_api_url, settings.AGSTACK_ENDPOINTS['register_field_boundary'])

    def _login(self):
        """Login with user/password and store the access token."""
        response = requests.post(
            self.login_url,
            data={"username": self.user, "password": self.password},
        )
        self.access_token = response.json()["access_token"]

    def _ensure_access_token(self):
        """Make sure we have an access token before making API calls."""
        if not self.access_token:
            self._login()

    def register_field_boundary(self, wkt_geometry, threshold=95, s2_index=(8, 13)):
        self._ensure_access_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-FROM-ASSET-REGISTRY": "True",
            "Content-Type": "application/json"
        }

        data = {
            "wkt": wkt_geometry,
        }
        endpoint_url = self.register_field_url
        resp = requests.post(endpoint_url, json=data, headers=headers)

        # If token expired/invalid, login again and retry once
        if resp.status_code == 401 or 'invalid token' in resp.json().get('message', '').lower():
            self._login()
            headers["Authorization"] = f"Bearer {self.access_token}"
            resp = requests.post(endpoint_url, json=data, headers=headers)

        geo_id = None
        try:
            result = resp.json()
            if 'Geo Id' in result:
                geo_id = result['Geo Id']
            elif 'matched geo ids' in result:
                geo_id = result['matched geo ids'][0]
            else:
                raise ValueError("Invalid response from AgStack API")
        except Exception as e:
            raise ValueError("Invalid response from AgStack API")
        return geo_id


if __name__ == '__main__':
    client = AgstackClient()
    wkt_geometry = "POLYGON((5.714800882907841 50.83967331197391,5.714729694830028 50.839206943235155,5.716022320453463 50.839169065366434,5.715939892152838 50.83967094463168,5.714800882907841 50.83967331197391))"
    print(client.register_field_boundary(wkt_geometry))
