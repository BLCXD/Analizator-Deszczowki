"""SMTP delivery shared by account email and alert tasks."""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from collections.abc import Mapping, Sequence
from html import escape
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)


def mail_enabled() -> bool:
    return bool(os.getenv("SMTP_HOST", "").strip())


def render_email(
    subject: str,
    paragraphs: Sequence[str],
    *,
    code: str | None = None,
    quote: str | None = None,
    facts: Mapping[str, str] | None = None,
    action: tuple[str, str] | None = None,
) -> tuple[str, str]:
    """Render escaped HTML and plain text variants using email-client-safe tables."""
    safe_subject = escape(subject)
    html_parts = []
    text_parts = []
    for paragraph in paragraphs:
        html_parts.append(
            '<tr><td class="mail-copy" style="padding:0 0 16px;color:#24313a;font:16px/1.6 Arial,sans-serif;white-space:pre-line">'
            f"{escape(paragraph)}</td></tr>"
        )
        text_parts.append(paragraph)

    if code is not None:
        html_parts.append(
            '<tr><td style="padding:16px;background:#f1f5f7;border-radius:8px;text-align:center;'
            'font:bold 24px/1.4 monospace;letter-spacing:2px">'
            f"{escape(code)}</td></tr>"
        )
        text_parts.append(code)
    if quote is not None:
        html_parts.append(
            '<tr><td style="padding:12px 16px;border-left:3px solid #68a88a;'
            'color:#52616a;font:italic 15px/1.5 Arial,sans-serif">'
            f"{escape(quote)}</td></tr>"
        )
        text_parts.append(f"> {quote}")
    if facts:
        rows = "".join(
            '<tr><td style="padding:6px 12px 6px 0;color:#52616a">'
            f"{escape(str(label))}</td><td style=\"padding:6px 0;font-weight:bold\">{escape(str(value))}</td></tr>"
            for label, value in facts.items()
        )
        html_parts.append(f'<tr><td><table role="presentation" style="width:100%">{rows}</table></td></tr>')
        text_parts.extend(f"{label}: {value}" for label, value in facts.items())
    if action is not None:
        label, url = action
        parsed_url = urlsplit(url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Email action URL must be an absolute HTTP(S) URL")
        html_parts.append(
            '<tr><td style="padding:24px 0;text-align:center"><a '
            f'href="{escape(url, quote=True)}" style="display:inline-block;padding:12px 20px;'
            'border-radius:6px;background:#247a55;color:#fff;text-decoration:none;'
            f'font:bold 15px Arial,sans-serif">{escape(label)}</a></td></tr>'
        )
        text_parts.append(f"{label}: {url}")

    html_body = (
        '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="light dark"><style>'
        '@media(prefers-color-scheme:dark){.mail-card{background:#17211d!important;color:#edf5f0!important}'
            '.mail-title,.mail-copy{color:#edf5f0!important}}</style></head>'
        '<body style="margin:0;padding:24px;background:#f3f6f4">'
        '<table role="presentation" style="width:100%;border-collapse:collapse"><tr><td align="center">'
        '<table class="mail-card" role="presentation" style="width:100%;max-width:600px;'
        'border-collapse:collapse;background:#fff;border-radius:10px;padding:28px">'
        f'<tr><td class="mail-title" style="padding:0 0 20px;color:#183b2c;font:bold 22px Arial,sans-serif">{safe_subject}</td></tr>'
        f'{"".join(html_parts)}'
        '<tr><td style="padding-top:18px;color:#738078;font:12px Arial,sans-serif">Analizator Deszczówki</td></tr>'
        '</table></td></tr></table></body></html>'
    )
    return html_body, "\n\n".join(text_parts)


def send_email(to_email: str, subject: str, body: str, html_body: str | None = None) -> bool:
    if not mail_enabled():
        return False
    host = os.getenv("SMTP_HOST", "").strip()

    port = int(os.getenv("SMTP_PORT", "587"))
    auth = os.getenv("SMTP_AUTH", "true").strip().lower() == "true"
    username = os.getenv("SMTP_USERNAME") or os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS", "")
    sender = os.getenv("SMTP_FROM") or os.getenv("MAIL_FROM") or username
    if auth and (not username or not password):
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD are required when SMTP_HOST is set")
    if not sender:
        raise ValueError("SMTP_FROM is required when SMTP_AUTH=false")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    if html_body is not None:
        message.add_alternative(html_body, subtype="html")
    context = ssl.create_default_context()

    if port == 25:
        if auth:
            raise ValueError("SMTP port 25 requires SMTP_AUTH=false")
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.send_message(message)
    elif port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=10, context=context) as server:
            server.ehlo()
            server.login(username, password)
            server.send_message(message)
    elif port == 587:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
            server.send_message(message)
    else:
        raise ValueError("SMTP_PORT must be 587 (STARTTLS) or 465 (SSL)")

    logger.info("Email sent through configured SMTP server")
    return True
