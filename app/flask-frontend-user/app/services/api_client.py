"""
HTTP client for communicating with the Analizator Deszczówki backend API.
Handles authentication, request/response processing, error handling, and retry logic.
"""
import json
import logging
import time
from typing import Dict, Any, Optional

import requests
from flask import session, current_app

logger = logging.getLogger(__name__)


class APIError(Exception):
                                                  
    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class APIClient:
\
\
\
       

    def __init__(self):
                                        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _get_config(self) -> Dict[str, Any]:
\
\
\
           
        if not current_app:
            raise RuntimeError("APIClient used outside of Flask application context")
        return {
            'API_BASE_URL': current_app.config.get('API_BASE_URL', 'http://localhost:8000'),
            'API_TIMEOUT': current_app.config.get('API_TIMEOUT', 30),
            'API_MAX_RETRIES': current_app.config.get('API_MAX_RETRIES', 3),
            'API_RETRY_BACKOFF_FACTOR': current_app.config.get('API_RETRY_BACKOFF_FACTOR', 0.5),
        }

    def _get_auth_headers(self) -> Dict[str, str]:
\
\
\
\
\
           
        headers = {}
        access_token = session.get('access_token')
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
\
\
\
\
\
\
\
\
\
\
\
           
        try:
            data = response.json() if response.content else {}
        except json.JSONDecodeError:
            data = {}
            logger.warning(f"Non-JSON response from API: {response.text}")

        if current_app.config.get('DEBUG'):
            logger.debug(f"API Request: {response.request.method} {response.request.url}")
            logger.debug(f"API Response Status: {response.status_code}")

        if 200 <= response.status_code < 300:
            return data

        error_message = data.get('detail') or data.get('message') or f'HTTP {response.status_code} Error'

        logger.error(f"API Error: {error_message} (Status: {response.status_code})")

        raise APIError(
            message=error_message,
            status_code=response.status_code,
            response_data=data
        )

    def _request_with_retry(self, method: str, endpoint: str,
                          **kwargs) -> Dict[str, Any]:
\
\
\
\
\
\
\
\
\
\
\
\
\
           
        config = self._get_config()
        base_url = config['API_BASE_URL']
        timeout = config['API_TIMEOUT']
        max_retries = config['API_MAX_RETRIES']
        backoff_factor = config['API_RETRY_BACKOFF_FACTOR']

        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = kwargs.pop('headers', {})
        headers.update(self._get_auth_headers())
        kwargs['headers'] = headers

        if 'timeout' not in kwargs:
            kwargs['timeout'] = timeout

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                return self._handle_response(response)
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries:
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Request failed after {max_retries + 1} attempts: {str(e)}")
            except APIError:
                raise

        raise APIError(
            message=f"Failed to connect to API after {max_retries + 1} attempts: {str(last_exception)}",
            response_data={}
        )

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
                               
        return self._request_with_retry('GET', endpoint, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                                
        if data is not None:
            kwargs['json'] = data
        return self._request_with_retry('POST', endpoint, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                               
        if data is not None:
            kwargs['json'] = data
        return self._request_with_retry('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
                                  
        return self._request_with_retry('DELETE', endpoint, **kwargs)

    def patch(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                                 
        if data is not None:
            kwargs['json'] = data
        return self._request_with_retry('PATCH', endpoint, **kwargs)


api_client = APIClient()


def get_api_client() -> APIClient:
\
\
\
\
\
       
    return api_client


def api_get(endpoint: str, **kwargs) -> Dict[str, Any]:
                                                
    return api_client.get(endpoint, **kwargs)


def api_post(endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                                                 
    return api_client.post(endpoint, data, **kwargs)


def api_put(endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                                                
    return api_client.put(endpoint, data, **kwargs)


def api_delete(endpoint: str, **kwargs) -> Dict[str, Any]:
                                                   
    return api_client.delete(endpoint, **kwargs)


def api_patch(endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
                                                  
    return api_client.patch(endpoint, data, **kwargs)
