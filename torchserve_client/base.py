# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_base.ipynb.

# %% auto 0
__all__ = ['BaseClient', 'ManagementClient', 'InferenceClient']

# %% ../nbs/00_base.ipynb 3
import os
import requests

# %% ../nbs/00_base.ipynb 4
class BaseClient:
    def __init__(self, base_url=None):
        base_url = (
            base_url
            if base_url
            else os.environ.get("TORCHSERVE_URL", "http://localhost")
        )
        self.base_url = base_url.rstrip("/")

    def _make_request(self, method, endpoint, json=None, params=None, files=None):
        """
        json: dict. The JSON body of the request.
        params: dict. The URL parameters of the request.
        files: [dict]. The files to upload.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=json, params=params, files=files)
        response.raise_for_status()
        return response.json()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url={self.base_url})"

    def _filter_none_values(self, data):
        return {key: value for key, value in data.items() if value is not None}

# %% ../nbs/00_base.ipynb 6
class ManagementClient(BaseClient):
    def __init__(self, base_url=None, port=8081):
        super().__init__(base_url)
        self.port = port
        self.base_url = f"{self.base_url}:{self.port}"

    def register_model(
        self,
        url,
        model_name=None,
        handler=None,
        runtime=None,
        batch_size=1,
        max_batch_delay=100,
        initial_workers=0,
        synchronous=False,
        response_timeout=120,
    ):
        data = {
            "url": url,
            "model_name": model_name,
            "handler": handler,
            "runtime": runtime,
            "batch_size": batch_size,
            "max_batch_delay": max_batch_delay,
            "initial_workers": initial_workers,
            "synchronous": synchronous,
            "response_timeout": response_timeout,
        }
        data = self._filter_none_values(data)
        return self._make_request("POST", "/models", json=data)

    def scale_workers(
        self,
        model_name,
        version=None,
        min_worker=1,
        max_worker=None,
        synchronous=False,
        timeout=-1,
    ):
        if version:
            endpoint = f"/models/{model_name}/{version}"
        else:
            endpoint = f"/models/{model_name}"

        params = {
            "min_worker": min_worker,
            "max_worker": max_worker if max_worker is not None else min_worker,
            "synchronous": synchronous,
            "timeout": timeout,
        }

        return self._make_request("PUT", endpoint, json=params)

    def describe_model(self, model_name, version=None, customized=False):
        """
        Returns the model description.
        version :  is optional. if `all` return status of all version of a model. If not provided, the latest version will be returned.
        allowed
        """
        params = {}
        if customized:
            params["customized"] = customized

        if version:
            endpoint = f"/models/{model_name}/{version}"
        else:
            endpoint = f"/models/{model_name}"
        return self._make_request("GET", endpoint, params=params)

    def unregister_model(self, model_name, version=None):
        if version:
            endpoint = f"/models/{model_name}/{version}"
        else:
            endpoint = f"/models/{model_name}"

        return self._make_request("DELETE", endpoint)

    def list_models(self, limit=100, next_page_token=None):
        params = {"limit": limit, "next_page_token": next_page_token}
        params = self._filter_none_values(params)
        return self._make_request("GET", "/models", params=params)

    def api_description(self):
        return self._make_request("OPTIONS", "/")

    def set_default_version(self, model_name, version):
        endpoint = f"/models/{model_name}/{version}/set-default"
        return self._make_request("PUT", endpoint)

# %% ../nbs/00_base.ipynb 8
class InferenceClient(BaseClient):
    def __init__(self, base_url=None, port=8080):
        super().__init__(base_url)
        self.port = port
        self.base_url = f"{self.base_url}:{self.port}"

    def api_description(self):
        return self._make_request("OPTIONS", "/")

    def health_check(self):
        return self._make_request("GET", "/ping")

    def prediction(self, model_name, data, version=None):
        """
        inference_data = [
            ('data', open('docs/images/dogs-before.jpg', 'rb')),
            ('data', open('docs/images/kitten_small.jpg', 'rb')),
        ]
        """
        if version:
            endpoint = f"/predictions/{model_name}/{version}"
        else:
            endpoint = f"/predictions/{model_name}"

        return self._make_request("POST", endpoint, files=data)

    def explaination(self, model_name, data):
        """
        data <string : bytes>
        """
        endpoint = f"/explanations/{model_name}"
        return self._make_request("POST", endpoint, files=data)
