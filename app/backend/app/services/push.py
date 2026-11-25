"""Real Web Push notification delivery via the Push API + pywebpush.

Browser subscribes through the standard Push API and posts the subscription to
the backend (same-origin Flask proxy, no CORS changes needed). The backend
stores it in push_subscriptions and alert tasks deliver via pywebpush using
VAPID keys.
"""
import base64
import logging
import os
from typing import Any, Dict, List, Optional
from cryptography.hazmat.primitives.asymmetric import ec

from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)

VAPID_CLAIMS = {
    "sub": os.getenv("VAPID_SUBJECT", "mailto:alerts@analizator-deszczowki.local"),
}

_VAPID_PUBLIC: Optional[str] = None
_VAPID_PRIVATE: Optional[str] = None


def _generate_vapid_keypair() -> tuple[str, str]:
                                                                                      
    private_key = ec.generate_private_key(ec.SECP256R1())
    priv_numbers = private_key.private_numbers()
    pub_numbers = private_key.public_key().public_numbers()
    priv_raw = priv_numbers.private_value.to_bytes(32, "big")
    pub_raw = b"\x04" + pub_numbers.x.to_bytes(32, "big") + pub_numbers.y.to_bytes(32, "big")
    return (
        base64.urlsafe_b64encode(pub_raw).decode().rstrip("="),
        base64.urlsafe_b64encode(priv_raw).decode().rstrip("="),
    )


def vapid_public_key() -> str:
                                                                       
    global _VAPID_PUBLIC
    if _VAPID_PUBLIC is None:
        key = os.getenv("VAPID_PUBLIC_KEY")
        if key:
            _VAPID_PUBLIC = key
        else:
            _VAPID_PUBLIC, _ = _generate_vapid_keypair()
            os.environ["VAPID_PUBLIC_KEY"] = _VAPID_PUBLIC
    return _VAPID_PUBLIC


def vapid_private_key() -> str:
                                                                        
    global _VAPID_PRIVATE
    if _VAPID_PRIVATE is None:
        key = os.getenv("VAPID_PRIVATE_KEY")
        if key:
            _VAPID_PRIVATE = key
        else:
            _, _VAPID_PRIVATE = _generate_vapid_keypair()
            os.environ["VAPID_PRIVATE_KEY"] = _VAPID_PRIVATE
    return _VAPID_PRIVATE


def save_subscription(
    db: Session,
    user_id: int,
    endpoint: str,
    p256dh_key: str,
    auth_key: str,
) -> PushSubscription:
                                                
    sub = (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == user_id, PushSubscription.endpoint == endpoint)
        .first()
    )
    if sub:
        sub.p256dh_key = p256dh_key
        sub.auth_key = auth_key
    else:
        sub = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
        )
        db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def remove_subscription(db: Session, user_id: int, endpoint: str) -> bool:
                                                
    sub = (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == user_id, PushSubscription.endpoint == endpoint)
        .first()
    )
    if not sub:
        return False
    db.delete(sub)
    db.commit()
    return True


def get_subscriptions_for_user(db: Session, user_id: int) -> List[PushSubscription]:
                                                          
    return db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all()


def _subscription_info(sub: PushSubscription) -> Dict[str, Any]:
    return {
        "endpoint": sub.endpoint,
        "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
    }


def _delivery_result(subscription_info: Dict[str, Any], payload: str) -> tuple[bool, bool]:
\
\
\
\
       
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=vapid_private_key(),
            vapid_claims=VAPID_CLAIMS,
            ttl=86400,
        )
        return True, False
    except WebPushException as exc:
        if exc.response is not None and exc.response.status_code in (404, 410):
            logger.warning("Push subscription expired (%s), dropping", exc.response.status_code)
            return False, True
        logger.error("Push delivery failed: %s", exc)
        return False, False


def send_push(subscription_info: Dict[str, Any], payload: str) -> bool:
                                                                  
    ok, _dead = _delivery_result(subscription_info, payload)
    return ok


def send_to_user(
    db: Session,
    user_id: int,
    payload: str,
) -> Dict[str, int]:
\
\
\
       
    subs = get_subscriptions_for_user(db, user_id)
    sent = failed = dropped = 0
    for sub in subs:
        ok, dead = _delivery_result(_subscription_info(sub), payload)
        if ok:
            sent += 1
        elif dead:
            db.delete(sub)
            dropped += 1
        else:
            failed += 1
    db.commit()
    return {"sent": sent, "failed": failed, "dropped": dropped}
