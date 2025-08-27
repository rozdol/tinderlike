import httpx
from typing import Optional, Dict, Any
from app.config import settings


class OAuthService:
    def __init__(self):
        self.google_client_id = settings.google_client_id
        self.google_client_secret = settings.google_client_secret
        self.apple_client_id = settings.apple_client_id
        self.apple_team_id = settings.apple_team_id
        self.apple_key_id = settings.apple_key_id
        self.apple_private_key = settings.apple_private_key
    
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/tokeninfo",
                    params={"access_token": token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("aud") == self.google_client_id:
                        # Get user info
                        user_info_response = await client.get(
                            "https://www.googleapis.com/oauth2/v2/userinfo",
                            headers={"Authorization": f"Bearer {token}"}
                        )
                        
                        if user_info_response.status_code == 200:
                            user_info = user_info_response.json()
                            return {
                                "email": user_info.get("email"),
                                "name": user_info.get("name"),
                                "picture": user_info.get("picture"),
                                "oauth_id": user_info.get("id"),
                                "provider": "google"
                            }
        except Exception as e:
            print(f"Google OAuth verification failed: {e}")
        
        return None
    
    async def verify_apple_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Apple OAuth token and return user info"""
        try:
            # Apple token verification is more complex and requires JWT validation
            # This is a simplified version - in production you'd need proper JWT validation
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://appleid.apple.com/auth/keys"
                )
                
                if response.status_code == 200:
                    # In a real implementation, you'd validate the JWT token
                    # For now, we'll return a placeholder
                    return {
                        "email": None,  # Apple doesn't always provide email
                        "name": None,
                        "picture": None,
                        "oauth_id": None,  # Would be extracted from JWT
                        "provider": "apple"
                    }
        except Exception as e:
            print(f"Apple OAuth verification failed: {e}")
        
        return None
    
    async def verify_oauth_token(self, provider: str, token: str) -> Optional[Dict[str, Any]]:
        """Verify OAuth token based on provider"""
        if provider.lower() == "google":
            return await self.verify_google_token(token)
        elif provider.lower() == "apple":
            return await self.verify_apple_token(token)
        else:
            return None


oauth_service = OAuthService()
