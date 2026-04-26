import base64
import json
import os
import secrets
import string
import time
from datetime import datetime, timezone
from typing import Any

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import secretmanager


def _now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _generate_db_password(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in candidate)
            and any(c.isupper() for c in candidate)
            and any(c.isdigit() for c in candidate)
            and any(c in "!@#$%^&*()-_=+" for c in candidate)
        ):
            return candidate


def _add_secret_version(project_id: str, secret_name: str, secret_value: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}/secrets/{secret_name}"
    response = client.add_secret_version(
        request={"parent": parent, "payload": {"data": secret_value.encode("utf-8")}}
    )
    return response.name


def _secret_version_number(version_resource_name: str) -> str:
    # Input format: projects/<project>/secrets/<name>/versions/<n>
    return version_resource_name.rsplit("/", 1)[-1]


def _decode_pubsub_payload(event: dict[str, Any]) -> dict[str, Any] | None:
    data = event.get("data")
    if not data:
        return None

    try:
        decoded = base64.b64decode(data).decode("utf-8")
        print(f"Pub/Sub payload: {decoded}")
        return json.loads(decoded)
    except Exception:
        print("Pub/Sub payload could not be decoded as JSON")
        return None


def _is_recursive_secret_event(payload: dict[str, Any] | None, jwt_secret_name: str, db_secret_name: str) -> bool:
    if not payload:
        return False

    resource_name = str(payload.get("name", ""))
    if not resource_name:
        return False

    # Secret Manager version events include names like:
    # projects/<id>/secrets/<secret>/versions/<n>
    return (
        f"/secrets/{jwt_secret_name}/versions/" in resource_name
        or f"/secrets/{db_secret_name}/versions/" in resource_name
    )


def _wait_sql_operation(session: AuthorizedSession, project_id: str, op_name: str, timeout_sec: int = 180) -> None:
    deadline = time.time() + timeout_sec
    url = f"https://sqladmin.googleapis.com/sql/v1beta4/projects/{project_id}/operations/{op_name}"

    while time.time() < deadline:
        res = session.get(url, timeout=30)
        res.raise_for_status()
        body = res.json()
        status = body.get("status")
        if status == "DONE":
            err = body.get("error", {})
            if err.get("errors"):
                raise RuntimeError(f"Cloud SQL operation failed: {json.dumps(err)}")
            return
        time.sleep(3)

    raise TimeoutError(f"Timed out waiting for Cloud SQL operation {op_name}")


def _update_cloud_sql_user_password(
    session: AuthorizedSession,
    project_id: str,
    instance_name: str,
    db_user: str,
    new_password: str,
) -> None:
    if not instance_name or not db_user:
        return

    url = (
        f"https://sqladmin.googleapis.com/sql/v1beta4/projects/{project_id}/instances/"
        f"{instance_name}/users?name={db_user}"
    )
    payload = {"name": db_user, "password": new_password}
    res = session.put(url, json=payload, timeout=60)
    res.raise_for_status()
    op_name = res.json().get("name")
    if op_name:
        _wait_sql_operation(session, project_id, op_name)


def _wait_run_operation(session: AuthorizedSession, op_name: str, timeout_sec: int = 180) -> None:
    deadline = time.time() + timeout_sec
    url = f"https://run.googleapis.com/v2/{op_name}"

    while time.time() < deadline:
        res = session.get(url, timeout=30)
        res.raise_for_status()
        body = res.json()
        if body.get("done"):
            if body.get("error"):
                raise RuntimeError(f"Cloud Run operation failed: {json.dumps(body['error'])}")
            return
        time.sleep(3)

    raise TimeoutError(f"Timed out waiting for Cloud Run operation {op_name}")


def _update_cloud_run_secret_versions(
    session: AuthorizedSession,
    project_id: str,
    region: str,
    service_name: str,
    secret_versions_by_env: dict[str, str],
    tag: str,
) -> None:
    if not service_name:
        return

    service_url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}"
    get_res = session.get(service_url, timeout=30)
    get_res.raise_for_status()

    service = get_res.json()
    template = service.get("template") or {}
    labels = template.get("labels") or {}
    labels["secret-reload"] = tag

    containers = template.get("containers") or []
    for container in containers:
        env_vars = container.get("env") or []
        for env_var in env_vars:
            env_name = env_var.get("name")
            if env_name not in secret_versions_by_env:
                continue

            value_source = env_var.get("valueSource") or {}
            secret_key_ref = value_source.get("secretKeyRef") or {}
            if not secret_key_ref:
                continue

            new_version = secret_versions_by_env[env_name]
            if secret_key_ref.get("version") != new_version:
                secret_key_ref["version"] = new_version
                value_source["secretKeyRef"] = secret_key_ref
                env_var["valueSource"] = value_source

    patch_url = f"{service_url}?updateMask=template.labels,template.containers"
    patch_res = session.patch(
        patch_url,
        json={"template": {"labels": labels, "containers": containers}},
        timeout=60,
    )
    patch_res.raise_for_status()

    op_name = patch_res.json().get("name")
    if op_name:
        _wait_run_operation(session, op_name)


def rotate_secret(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context

    project_id = os.environ["PROJECT_ID"]
    region = os.environ.get("REGION", "us-central1")
    jwt_secret_name = os.environ.get("JWT_SECRET_NAME", "jwt-secret")
    db_secret_name = os.environ.get("DB_SECRET_NAME", "db-password")
    cloud_sql_instance = os.environ.get("CLOUD_SQL_INSTANCE", "")
    cloud_sql_db_user = os.environ.get("CLOUD_SQL_DB_USER", "livemenu_user")
    backend_service = os.environ.get("BACKEND_SERVICE_NAME", "")
    frontend_service = os.environ.get("FRONTEND_SERVICE_NAME", "")
    rotate_db_user_password = os.environ.get("ROTATE_DB_USER_PASSWORD", "true").lower() == "true"
    force_cloud_run_refresh = os.environ.get("FORCE_CLOUD_RUN_REFRESH", "true").lower() == "true"

    payload = _decode_pubsub_payload(event)
    if _is_recursive_secret_event(payload, jwt_secret_name, db_secret_name):
        result = {
            "status": "skipped",
            "reason": "recursive_secret_event",
        }
        print(json.dumps(result))
        return result

    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    session = AuthorizedSession(credentials)

    ts = _now_tag()
    new_jwt = secrets.token_urlsafe(64)
    new_db_password = _generate_db_password()

    jwt_version = _add_secret_version(project_id, jwt_secret_name, new_jwt)
    db_version = _add_secret_version(project_id, db_secret_name, new_db_password)
    jwt_version_num = _secret_version_number(jwt_version)
    db_version_num = _secret_version_number(db_version)

    if rotate_db_user_password:
        _update_cloud_sql_user_password(
            session=session,
            project_id=project_id,
            instance_name=cloud_sql_instance,
            db_user=cloud_sql_db_user,
            new_password=new_db_password,
        )

    if force_cloud_run_refresh:
        _update_cloud_run_secret_versions(
            session=session,
            project_id=project_id,
            region=region,
            service_name=backend_service,
            secret_versions_by_env={
                "SECRET_KEY": jwt_version_num,
                "DB_PASSWORD": db_version_num,
            },
            tag=ts,
        )
        _update_cloud_run_secret_versions(
            session=session,
            project_id=project_id,
            region=region,
            service_name=frontend_service,
            secret_versions_by_env={
                "SECRET_KEY": jwt_version_num,
            },
            tag=ts,
        )

    result = {
        "status": "ok",
        "timestamp": ts,
        "jwt_secret": jwt_secret_name,
        "jwt_version": jwt_version,
        "jwt_version_number": jwt_version_num,
        "db_secret": db_secret_name,
        "db_version": db_version,
        "db_version_number": db_version_num,
        "updated_sql_user": rotate_db_user_password and bool(cloud_sql_instance and cloud_sql_db_user),
        "refreshed_cloud_run": force_cloud_run_refresh,
    }
    print(json.dumps(result))
    return result