from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import pytest
import smtplib

from app.services.email import render_email, send_email


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass", "SMTP_FROM": "AD <ad@example.com>"})
def test_send_email_uses_starttls_and_sends_message():
    server = MagicMock()
    server.__enter__.return_value = server

    with patch("app.services.email.smtplib.SMTP", return_value=server) as smtp:
        assert send_email("user@example.com", "Subject", "Body")

    smtp.assert_called_once_with("mail.example.com", 587, timeout=10)
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("user", "pass")
    message = server.send_message.call_args.args[0]
    assert isinstance(message, EmailMessage)
    assert message["To"] == "user@example.com"
    assert message.get_content() == "Body\n"


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "465", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass", "SMTP_FROM": "ad@example.com"})
def test_send_email_uses_implicit_tls_on_port_465():
    server = MagicMock()
    server.__enter__.return_value = server

    with patch("app.services.email.smtplib.SMTP_SSL", return_value=server) as smtp_ssl:
        assert send_email("user@example.com", "Subject", "Body")

    assert smtp_ssl.call_args.args[:2] == ("mail.example.com", 465)
    assert smtp_ssl.call_args.kwargs["timeout"] == 10
    server.starttls.assert_not_called()
    server.login.assert_called_once_with("user", "pass")
    server.send_message.assert_called_once()


def test_send_email_is_disabled_without_smtp_host():
    with patch.dict("os.environ", {"SMTP_HOST": ""}), patch("app.services.email.smtplib.SMTP") as smtp:
        assert not send_email("user@example.com", "Subject", "Body")
    smtp.assert_not_called()


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USERNAME": "", "SMTP_PASSWORD": "", "SMTP_FROM": ""})
def test_send_email_rejects_incomplete_credentials():
    with pytest.raises(ValueError, match="SMTP_USERNAME and SMTP_PASSWORD"):
        send_email("user@example.com", "Subject", "Body")


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USER": "user", "SMTP_PASS": "pass"}, clear=True)
def test_send_email_supports_short_credential_names_and_defaults_sender_to_login():
    server = MagicMock()
    server.__enter__.return_value = server

    with patch("app.services.email.smtplib.SMTP", return_value=server):
        assert send_email("user@example.com", "Subject", "Body")

    message = server.send_message.call_args.args[0]
    assert message["From"] == "user"


def test_render_email_returns_escaped_html_and_plain_text():
    html_body, text_body = render_email(
        "Reset <hasła>",
        ["Witaj <użytkowniku>"],
        action=("Ustaw hasło", "https://app.example/reset?a=1&b=2"),
    )

    assert "Reset &lt;hasła&gt;" in html_body
    assert "Witaj &lt;użytkowniku&gt;" in html_body
    assert 'href="https://app.example/reset?a=1&amp;b=2"' in html_body
    assert "Ustaw hasło: https://app.example/reset?a=1&b=2" in text_body


def test_render_email_rejects_non_http_action_urls():
    with pytest.raises(ValueError, match=r"absolute HTTP\(S\) URL"):
        render_email("Reset", ["Treść"], action=("Ustaw hasło", "javascript:alert(1)"))


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass"}, clear=True)
def test_send_email_includes_both_plain_text_and_html_alternatives():
    server = MagicMock()
    server.__enter__.return_value = server

    with patch("app.services.email.smtplib.SMTP", return_value=server):
        assert send_email("user@example.com", "Subject", "Text body", "<p>HTML body</p>")

    message = server.send_message.call_args.args[0]
    assert message.get_body(preferencelist=("plain",)).get_content() == "Text body\n"
    assert message.get_body(preferencelist=("html",)).get_content() == "<p>HTML body</p>\n"


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "25", "SMTP_AUTH": "true", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass", "SMTP_FROM": "ad@example.com"}, clear=True)
def test_send_email_rejects_unsupported_port():
    with pytest.raises(ValueError, match="SMTP port 25 requires SMTP_AUTH=false"):
        send_email("user@example.com", "Subject", "Body")


@patch.dict("os.environ", {"SMTP_HOST": "smtp", "SMTP_PORT": "25", "SMTP_AUTH": "false", "SMTP_FROM": "reset@deszczowka.io"}, clear=True)
def test_send_email_uses_private_unauthenticated_relay():
    with patch("smtplib.SMTP") as smtp:
        assert send_email("user@example.com", "Subject", "Body")
        smtp.assert_called_once_with("smtp", 25, timeout=10)
        smtp.return_value.__enter__.return_value.send_message.assert_called_once()


@patch.dict("os.environ", {"SMTP_HOST": "smtp", "SMTP_PORT": "25", "SMTP_AUTH": "false"}, clear=True)
def test_send_email_requires_sender_address_without_smtp_auth():
    with pytest.raises(ValueError, match="SMTP_FROM is required"):
        send_email("user@example.com", "Subject", "Body")


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass", "SMTP_FROM": "ad@example.com"})
def test_send_email_propagates_authentication_failure_and_closes_connection():
    server = MagicMock()
    server.__enter__.return_value = server
    server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"authentication failed")

    with patch("app.services.email.smtplib.SMTP", return_value=server):
        with pytest.raises(smtplib.SMTPAuthenticationError):
            send_email("user@example.com", "Subject", "Body")

    server.__exit__.assert_called_once()


@patch.dict("os.environ", {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587", "SMTP_USERNAME": "user", "SMTP_PASSWORD": "pass", "SMTP_FROM": "ad@example.com"})
def test_send_email_propagates_delivery_failure_and_closes_connection():
    server = MagicMock()
    server.__enter__.return_value = server
    server.send_message.side_effect = smtplib.SMTPRecipientsRefused({"user@example.com": (550, b"rejected")})

    with patch("app.services.email.smtplib.SMTP", return_value=server):
        with pytest.raises(smtplib.SMTPRecipientsRefused):
            send_email("user@example.com", "Subject", "Body")

    server.__exit__.assert_called_once()
