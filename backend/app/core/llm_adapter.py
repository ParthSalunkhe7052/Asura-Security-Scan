"""
LLM Adapter for OpenRouter API Integration

This module provides a unified interface for interacting with LLM providers,
currently supporting OpenRouter API.
"""

import os
import requests
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()


class LLMAdapter:
    """Adapter for LLM API interactions via OpenRouter"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "openrouter")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Base list of candidate free models, highest priority first
        # Will be filtered against available endpoints from OpenRouter
        env_models = os.getenv("LLM_MODELS")
        if env_models:
            self.free_models = [m.strip() for m in env_models.split(",") if m.strip()]
        else:
            self.free_models = [
                "google/gemini-2.0-flash-exp:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                "qwen/qwen2.5-7b-instruct:free",
                "deepseek/deepseek-r1:free",
            ]

        # Cache of verified working model IDs (populated lazily)
        self._verified_models: List[str] = []
        self._last_model_verification_ts: float = 0.0
        
        # Default to first model in list
        self.model = self.free_models[0]
        
        self._logger = logging.getLogger(__name__)
        self.api_key_missing = not bool(self.api_key)
        if self.api_key_missing:
            self._logger.warning("OpenRouter API key not configured")
        self._logger.info(f"LLM Adapter initialized with provider: {self.provider}")
        self._logger.info(f"Default model: {self.model}")
    
    def _verify_available_models(self) -> List[str]:
        """Fetch available models and return filtered candidate list."""
        # Re-verify at most every 5 minutes
        now = time.time()
        if self._verified_models and (now - self._last_model_verification_ts) < 300:
            return self._verified_models
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }
            resp = requests.get(f"{self.base_url}/models", headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                ids = {m.get("id") for m in data.get("data", []) if m.get("id")}
                verified = [m for m in self.free_models if m in ids]
                # If none verified, keep original list to avoid empty
                self._verified_models = verified if verified else self.free_models.copy()
                self._last_model_verification_ts = now
                self._logger.info(f"Verified models: {self._verified_models}")
            else:
                # On failure, retain previous or fallback to base list
                self._logger.warning(f"Model verification failed with {resp.status_code}")
                if not self._verified_models:
                    self._verified_models = self.free_models.copy()
            return self._verified_models
        except Exception as e:
            self._logger.warning(f"Model verification error: {e}")
            if not self._verified_models:
                self._verified_models = self.free_models.copy()
            return self._verified_models

    def _post_with_retry(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], model: str) -> requests.Response:
        """POST with exponential backoff on 429 for meta-llama model."""
        max_retries = 3
        base_delay = 1.0
        attempt = 0
        while True:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code != 429:
                return response
            is_llama = model.startswith("meta-llama/")
            if not is_llama or attempt >= max_retries:
                return response
            delay = base_delay * (2 ** attempt)
            self._logger.warning(f"429 rate limit for {model}. Retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(delay)
            attempt += 1

    def send_with_fallback(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a prompt with automatic fallback to other free models if rate-limited
        
        Args:
            prompt: The text prompt to send
            **kwargs: Additional parameters
        
        Returns:
            Response dictionary
        """
        # Get list of models to try (verified if possible)
        models_to_try = kwargs.pop("models", None) or self._verify_available_models()
        
        last_error = None
        
        if self.api_key_missing:
            return {
                "success": False,
                "response": None,
                "error": "OpenRouter API key missing",
                "model": self.model,
                "usage": {}
            }
        for i, model in enumerate(models_to_try):
            self._logger.info(f"Trying model {i+1}/{len(models_to_try)}: {model}")
            
            # Try this model
            result = self.send(prompt, model=model, **kwargs)
            
            # If successful, return immediately
            if result["success"]:
                return result
            
            # If rate limited or endpoint missing, try next model
            err = result.get("error", "").lower()
            if ("rate limit" in err) or ("endpoint not found" in err) or ("model not available" in err):
                self._logger.warning("Model unavailable (rate limit or endpoint), trying next")
                last_error = result["error"]
                continue
            
            # For other errors, return immediately (don't try other models)
            return result
        
        # All models failed
        return {
            "success": False,
            "response": None,
            "error": f"All models failed. Last error: {last_error}",
            "model": "none",
            "usage": {}
        }
    
    def send(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a prompt to the LLM and get a response
        
        Args:
            prompt: The text prompt to send to the LLM
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dictionary containing:
                - success: bool
                - response: str (LLM response text)
                - error: str (if success=False)
                - model: str (model used)
                - usage: dict (token usage info)
        """
        try:
            if self.api_key_missing:
                return {
                    "success": False,
                    "response": None,
                    "error": "OpenRouter API key missing",
                    "model": self.model,
                    "usage": {}
                }
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/asura-security",  # Optional
                "X-Title": "ASURA Security Scanner"  # Optional
            }
            
            # Build request payload
            model_to_use = kwargs.get("model", self.model)
            payload = {
                "model": model_to_use,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            self._logger.info(f"Sending prompt to {model_to_use}")
            
            # Make API request
            response = self._post_with_retry(
                f"{self.base_url}/chat/completions",
                headers,
                payload,
                model_to_use,
            )
            
            # Handle different status codes
            if response.status_code == 200:
                data = response.json()
                
                # Extract response text
                if "choices" in data and len(data["choices"]) > 0:
                    response_text = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "response": response_text,
                        "model": data.get("model", self.model),
                        "usage": data.get("usage", {}),
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "response": None,
                        "error": "No response from model",
                        "model": self.model,
                        "usage": {}
                    }
            
            elif response.status_code == 401:
                error_msg = "Authentication failed. Invalid API key."
                self._logger.error(error_msg)
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
                    "usage": {}
                }
            
            elif response.status_code == 429:
                error_msg = "Rate limit exceeded. Please try again later."
                self._logger.warning(error_msg)
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f" Details: {error_data['error'].get('message', '')}"
                except Exception as e:  # nosec B110
                    # Failed to parse error details - not critical, main error message is sufficient
                    self._logger.debug(f"Could not parse rate limit error details: {e}")
                
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
                    "usage": {}
                }
            elif response.status_code == 404:
                error_msg = "Model endpoint not found"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        details = error_data["error"].get("message", "")
                        if details:
                            error_msg += f": {details}"
                except Exception:
                    pass
                self._logger.error(f"{error_msg} for {model_to_use}")
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": model_to_use,
                    "usage": {}
                }
            
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error'].get('message', '')}"
                except:
                    error_msg += f": {response.text[:200]}"
                self._logger.error(error_msg)
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
                    "usage": {}
                }
        
        except requests.exceptions.Timeout:
            error_msg = "Request timed out after 30 seconds"
            self._logger.warning(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "model": self.model,
                "usage": {}
            }
        
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to OpenRouter API. Check your internet connection."
            self._logger.error(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "model": self.model,
                "usage": {}
            }
        
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            self._logger.error(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "model": self.model,
                "usage": {}
            }


# Global instance for easy access
_llm_adapter_instance: Optional[LLMAdapter] = None


def get_llm_adapter() -> LLMAdapter:
    """
    Get or create the global LLM adapter instance
    
    Returns:
        LLMAdapter instance
    """
    global _llm_adapter_instance
    
    if _llm_adapter_instance is None:
        _llm_adapter_instance = LLMAdapter()
    
    return _llm_adapter_instance


def send_prompt(prompt: str, use_fallback: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to send a prompt using the global adapter
    
    Args:
        prompt: The text prompt to send
        use_fallback: If True, automatically try other models if rate-limited (default: True)
        **kwargs: Additional parameters
    
    Returns:
        Response dictionary
    """
    adapter = get_llm_adapter()
    
    if use_fallback:
        return adapter.send_with_fallback(prompt, **kwargs)
    else:
        return adapter.send(prompt, **kwargs)


# CLI interface for testing
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LLM Adapter")
    parser.add_argument("prompt", nargs="?", default="Hello from ASURA", help="Prompt to send to LLM")
    parser.add_argument("--model", help="Override model to use")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0-1)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ASURA LLM ADAPTER TEST")
    print("=" * 60)
    print(f"\nPrompt: {args.prompt}\n")
    
    try:
        adapter = LLMAdapter()
        
        kwargs = {
            "temperature": args.temperature,
            "max_tokens": args.max_tokens
        }
        if args.model:
            kwargs["model"] = args.model
        
        result = adapter.send(args.prompt, **kwargs)
        
        print("\n" + "=" * 60)
        print("RESPONSE")
        print("=" * 60)
        
        if result["success"]:
            print(f"\n✅ Success!")
            print(f"\nModel: {result['model']}")
            print(f"\nResponse:\n{result['response']}")
            
            if result.get("usage"):
                print(f"\nUsage:")
                for key, value in result["usage"].items():
                    print(f"  {key}: {value}")
        else:
            print(f"\n❌ Failed: {result['error']}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
