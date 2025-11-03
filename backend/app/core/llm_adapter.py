"""
LLM Adapter for OpenRouter API Integration

This module provides a unified interface for interacting with LLM providers,
currently supporting OpenRouter API.
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMAdapter:
    """Adapter for LLM API interactions via OpenRouter"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "openrouter")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # List of free models to try (in order of preference)
        # Tested and working as of Nov 2, 2025
        self.free_models = [
            "meta-llama/llama-3.2-3b-instruct:free",  # ✅ Working - Llama 3.2
            "qwen/qwen-2-7b-instruct:free",  # Qwen 2
            "google/gemini-2.0-flash-exp:free",  # Gemini (may be rate limited)
            "deepseek/deepseek-r1:free"  # DeepSeek (may be rate limited)
        ]
        
        # Default to first model in list
        self.model = self.free_models[0]
        
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY not found in environment variables")
        
        print(f"✅ LLM Adapter initialized with provider: {self.provider}")
        print(f"   Default model: {self.model}")
    
    def send_with_fallback(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a prompt with automatic fallback to other free models if rate-limited
        
        Args:
            prompt: The text prompt to send
            **kwargs: Additional parameters
        
        Returns:
            Response dictionary
        """
        # Get list of models to try
        models_to_try = kwargs.pop("models", None) or self.free_models.copy()
        
        last_error = None
        
        for i, model in enumerate(models_to_try):
            print(f"🤖 Trying model {i+1}/{len(models_to_try)}: {model}")
            
            # Try this model
            result = self.send(prompt, model=model, **kwargs)
            
            # If successful, return immediately
            if result["success"]:
                return result
            
            # If rate limited, try next model
            if "rate limit" in result.get("error", "").lower():
                print(f"   ⚠️  Model rate-limited, trying next...")
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
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/asura-security",  # Optional
                "X-Title": "ASURA Security Scanner"  # Optional
            }
            
            # Build request payload
            payload = {
                "model": kwargs.get("model", self.model),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            print(f"🤖 Sending prompt to {self.model}...")
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
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
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
                    "usage": {}
                }
            
            elif response.status_code == 429:
                error_msg = "Rate limit exceeded. Please try again later."
                print(f"⚠️  {error_msg}")
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f" Details: {error_data['error'].get('message', '')}"
                except:
                    pass
                
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
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
                
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "model": self.model,
                    "usage": {}
                }
        
        except requests.exceptions.Timeout:
            error_msg = "Request timed out after 30 seconds"
            print(f"⚠️  {error_msg}")
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "model": self.model,
                "usage": {}
            }
        
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to OpenRouter API. Check your internet connection."
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "model": self.model,
                "usage": {}
            }
        
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            print(f"❌ {error_msg}")
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
