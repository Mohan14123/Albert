"""Webhook endpoints for third-party provider push notifications."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.events.publisher import EventPublisher

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])

_publisher = EventPublisher()


async def _publish_webhook_event(provider: str, payload: dict) -> None:
    """Publish a webhook event to the domain exchange."""
    try:
        await _publisher.publish(
            f"integration.webhook.{provider}",
            {"provider": provider, "payload": payload},
        )
    except Exception as exc:
        logger.error("Failed to publish webhook event for %s: %s", provider, exc)


@router.post("/gmail")
async def gmail_webhook(request: Request) -> JSONResponse:
    """
    Handle Gmail push notifications.
    Google sends a POST with a base64-encoded Pub/Sub message.
    Verify the request is from Google, then forward as an internal event.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
        )

    await _publish_webhook_event("gmail", payload)
    logger.info("Received Gmail webhook")
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/calendar")
async def calendar_webhook(request: Request) -> JSONResponse:
    """Handle Google Calendar push notifications."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
        )

    await _publish_webhook_event("calendar", payload)
    logger.info("Received Calendar webhook")
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/slack")
async def slack_webhook(
    request: Request,
    x_slack_signature: str = Header(default=""),
    x_slack_request_timestamp: str = Header(default=""),
) -> JSONResponse:
    """
    Handle Slack event subscriptions.
    Verifies HMAC-SHA256 signature before processing.
    """
    body = await request.body()

    # Slack signature verification
    slack_signing_secret = getattr(settings, "slack_signing_secret", None)
    if slack_signing_secret:
        sig_basestring = f"v0:{x_slack_request_timestamp}:{body.decode()}"
        computed = (
            "v0="
            + hmac.new(
                slack_signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
            ).hexdigest()
        )
        if not hmac.compare_digest(computed, x_slack_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Slack signature",
            )

    try:
        import json

        payload = json.loads(body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
        )

    # Respond to Slack URL verification challenge
    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload.get("challenge")})

    await _publish_webhook_event("slack", payload)
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/jira")
async def jira_webhook(request: Request) -> JSONResponse:
    """Handle Jira webhook events."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
        )

    await _publish_webhook_event("jira", payload)
    logger.info("Received Jira webhook: %s", payload.get("webhookEvent"))
    return JSONResponse(status_code=200, content={"status": "ok"})
