"""
Tests for the main Evolution API client.
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from pyevolutionapi import EvolutionClient
from pyevolutionapi.exceptions import (
    EvolutionAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)


class TestEvolutionClient:
    """Test cases for EvolutionClient."""
    
    def test_client_initialization(self, mock_base_url, mock_api_key):
        """Test client initialization with parameters."""
        client = EvolutionClient(
            base_url=mock_base_url,
            api_key=mock_api_key,
            default_instance="test-instance"
        )
        
        assert client.base_url == mock_base_url
        assert client.api_key == mock_api_key
        assert client.default_instance == "test-instance"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        
    def test_client_initialization_from_env(self, monkeypatch):
        """Test client initialization from environment variables."""
        monkeypatch.setenv("EVOLUTION_BASE_URL", "http://test.com")
        monkeypatch.setenv("EVOLUTION_API_KEY", "test-key")
        monkeypatch.setenv("EVOLUTION_INSTANCE_NAME", "env-instance")
        
        client = EvolutionClient()
        
        assert client.base_url == "http://test.com"
        assert client.api_key == "test-key"
        assert client.default_instance == "env-instance"
        
    def test_resources_initialization(self, client):
        """Test that all resources are properly initialized."""
        assert hasattr(client, 'instance')
        assert hasattr(client, 'instances')  # Alias
        assert hasattr(client, 'messages')
        assert hasattr(client, 'message')  # Alias
        assert hasattr(client, 'chat')
        assert hasattr(client, 'group')
        assert hasattr(client, 'profile')
        assert hasattr(client, 'webhook')
        
    @patch('httpx.Client.request')
    def test_successful_request(self, mock_request, client, mock_response):
        """Test successful API request."""
        mock_request.return_value = mock_response
        
        response = client.request("GET", "/test-endpoint")
        
        assert response == mock_response
        mock_request.assert_called_once()
        
    @patch('httpx.Client.request')
    def test_request_with_instance_placeholder(self, mock_request, client, mock_response):
        """Test request with instance placeholder replacement."""
        mock_request.return_value = mock_response
        
        client.request("GET", "/test/{instance}/endpoint", instance="my-instance")
        
        # Check that the URL was called with the correct instance name
        call_args = mock_request.call_args
        assert "my-instance" in call_args.kwargs["url"]
        
    @patch('httpx.Client.request')
    def test_authentication_error_handling(self, mock_request, client):
        """Test handling of 401 authentication errors."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_response.text = '{"message": "Unauthorized"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.request("GET", "/test-endpoint")
            
        assert exc_info.value.status_code == 401
        
    @patch('httpx.Client.request')
    def test_not_found_error_handling(self, mock_request, client):
        """Test handling of 404 not found errors."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.json.return_value = {"message": "Not Found"}
        mock_response.text = '{"message": "Not Found"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "/test-endpoint")
            
        assert exc_info.value.status_code == 404
        
    @patch('httpx.Client.request')
    def test_validation_error_handling(self, mock_request, client):
        """Test handling of 400 validation errors."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {"message": "Validation Error"}
        mock_response.text = '{"message": "Validation Error"}'
        mock_request.return_value = mock_response
        
        with pytest.raises(ValidationError) as exc_info:
            client.request("GET", "/test-endpoint")
            
        assert exc_info.value.status_code == 400
        
    @patch('httpx.Client.request')
    def test_timeout_error_handling(self, mock_request, client):
        """Test handling of timeout errors."""
        mock_request.side_effect = httpx.TimeoutException("Request timed out")
        
        with pytest.raises(Exception):  # Should be EvolutionTimeoutError
            client.request("GET", "/test-endpoint")
            
    def test_context_manager(self, mock_base_url, mock_api_key):
        """Test client as context manager."""
        with EvolutionClient(base_url=mock_base_url, api_key=mock_api_key) as client:
            assert isinstance(client, EvolutionClient)
            
    def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client._client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.is_success = True
            mock_get.return_value = mock_response
            
            result = client.health_check()
            
            assert result is True
            mock_get.assert_called_once_with("/")
            
    def test_health_check_failure(self, client):
        """Test failed health check."""
        with patch.object(client._client, 'get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            result = client.health_check()
            
            assert result is False