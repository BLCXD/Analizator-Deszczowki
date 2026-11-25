"""Schemas for Web Push subscription management."""
from pydantic import BaseModel, Field


class PushSubscribeRequest(BaseModel):
    endpoint: str = Field(..., description="Push service endpoint URL")
    p256dh_key: str = Field(..., description="Client public key (base64url)")
    auth_key: str = Field(..., description="Auth secret (base64url)")


class PushUnsubscribeRequest(BaseModel):
    endpoint: str = Field(..., description="Push service endpoint URL to remove")


class PushVapidPublicKey(BaseModel):
    public_key: str = Field(..., description="VAPID public key (base64url)")
