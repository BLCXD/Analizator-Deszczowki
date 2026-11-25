"""Web Push subscription management endpoints.

Browser subscribes through the standard Push API and posts the subscription to
these same-origin endpoints so no CORS changes are needed.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.push import save_subscription, remove_subscription, vapid_public_key
from app.schemas.push import (
    PushSubscribeRequest,
    PushUnsubscribeRequest,
    PushVapidPublicKey,
)

router = APIRouter()


@router.get("/vapid-public-key", response_model=PushVapidPublicKey)
def get_vapid_public_key():
                                                                            
    return PushVapidPublicKey(public_key=vapid_public_key())


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
def subscribe(
    payload: PushSubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
                                                        
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    try:
        save_subscription(
            db=db,
            user_id=current_user.id,
            endpoint=payload.endpoint,
            p256dh_key=payload.p256dh_key,
            auth_key=payload.auth_key,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save subscription: {exc}",
        )
    return {"success": True}


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(
    payload: PushUnsubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
                                                          
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    removed = remove_subscription(
        db=db, user_id=current_user.id, endpoint=payload.endpoint
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )
    return None
