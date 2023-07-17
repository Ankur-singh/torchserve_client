# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_base.ipynb.

# %% auto 0
__all__ = ['BaseClient']

# %% ../nbs/00_base.ipynb 4
import os
import requests

# %% ../nbs/00_base.ipynb 5
class BaseClient:
    def __init__(self, base_url=None):
        base_url = (
            base_url
            if base_url
            else os.environ.get("TORCHSERVE_URL", "http://localhost")
        )
        self.base_url = base_url.rstrip("/")

    def _make_request(self, method, endpoint, data=None, params=None, files=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=data, params=params, files=files)
        response.raise_for_status()
        return response.json()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url={self.base_url})"

    def _filter_none_values(self, data):
        return {key: value for key, value in data.items() if value is not None}
