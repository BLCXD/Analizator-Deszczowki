"""Application-level email notifications for AD."""

from collections.abc import Mapping, Sequence

from app.services.email import render_email, send_email


def notify_user(
    to_email: str,
    subject: str,
    paragraphs: Sequence[str],
    *,
    code: str | None = None,
    quote: str | None = None,
    facts: Mapping[str, str] | None = None,
    action: tuple[str, str] | None = None,
) -> bool:
    html_body, text_body = render_email(
        subject,
        paragraphs,
        code=code,
        quote=quote,
        facts=facts,
        action=action,
    )
    return send_email(to_email, subject, text_body, html_body)
