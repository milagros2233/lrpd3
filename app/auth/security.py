"""Securidad para operaciones en DB"""

import os
from fastapi import Depends, HTTPException, status
from app.auth.auth import verify_token


ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")


def is_admin(user_email: str = Depends(verify_token)) -> dict:
    """Verifica si el usuario es admin basado en su email."""
    if user_email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores",
        )
    return {"email": user_email}
