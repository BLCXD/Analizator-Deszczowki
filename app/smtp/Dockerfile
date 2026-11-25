FROM debian:bookworm-slim

RUN echo 'postfix postfix/mailname string mail.deszczowka.io' | debconf-set-selections \
    && echo 'postfix postfix/main_mailer_type string Internet Site' | debconf-set-selections \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends postfix ca-certificates libsasl2-modules \
    && rm -rf /var/lib/apt/lists/*

COPY main.cf /etc/postfix/main.cf
RUN chmod 0644 /etc/postfix/main.cf
RUN sed -i -E '/^smtp[[:space:]]+unix[[:space:]]/s/[[:space:]]y([[:space:]]+-[[:space:]]+-[[:space:]]+smtp)$/ n\1/' /etc/postfix/master.cf \
    && grep -Eq '^smtp[[:space:]]+unix[[:space:]]+-[[:space:]]+-[[:space:]]+n[[:space:]]+-[[:space:]]+-[[:space:]]+smtp$' /etc/postfix/master.cf

CMD ["bash", "-c", "cp /run/secrets/smtp2go_sasl_passwd /etc/postfix/sasl_passwd && chown root:postfix /etc/postfix/sasl_passwd && chmod 0640 /etc/postfix/sasl_passwd && postmap /etc/postfix/sasl_passwd && chown root:postfix /etc/postfix/sasl_passwd.db && chmod 0640 /etc/postfix/sasl_passwd.db && exec postfix start-fg"]
