import os
from datetime import datetime
from uuid import UUID

import bcrypt
from fastapi import HTTPException, status, UploadFile
from fastapi.routing import APIRoute
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.routing import BaseRoute

import app.models as models
import app.schemas as schemas


def ensure_all_permissions_exist(db: Session, routes: list[APIRoute]) -> None:
    for route in routes:
        for method in route.methods:
            path_parts = route.path.split("/")
            for i in range(len(path_parts)):
                permission_scope = "/" + "/".join(path_parts[1:i+1])

                existing_permission_scope = db.scalar(
                    select(models.PermissionScope)
                    .where(models.PermissionScope.route == permission_scope)
                    .where(models.PermissionScope.method == method)
                )

                if existing_permission_scope is None:
                    new_permission_scope = models.PermissionScope(
                        route=permission_scope,
                        method=method
                    )
                    db.add(new_permission_scope)
                    db.commit()