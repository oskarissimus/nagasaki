import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status
from nagasaki.settings import Settings


def validate_basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    settings = Settings()
    correct_username = secrets.compare_digest(
        credentials.username, settings.basic_auth_username
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.basic_auth_password
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
