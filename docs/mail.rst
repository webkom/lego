Mail
====

Mailing Lists
-------------
@orhanhenrik


Restricted Mail
---------------

The first entrypoint for our mail is GSuite. The restricted address needs to be forwarded to our
local postfix server. The mail is from now on handled by LEGO.

Steps:

1) Mail hits GSuite and gets forwarded to out local postfix instance.
2) Transport maps is used to forward mail to the LMTP server running in LEGO.
3) LEGO uses the token attached to the message to decide where to send the message.
4) We transform the message to pass SPF, DKIM and DMARC.
5) LEGO sends out the new message to all recipients.


To start the LMTP server:

::

  python manage.py restricted_email

LMTP stands for Local Mail Transfer Protocol and is almost the same protocol as SMTP.

The LMTP server has two settings:

::

    LMTP_HOST = '0.0.0.0'
    LMTP_PORT = 8024


Postfix Configuration
---------------------

This section describes some important parts of the Postfix settings.

TLS settings
************

main.cf
::

    smtpd_tls_cert_file=/etc/ssl/abakus/star.abakus.no.bundle.crt
    smtpd_tls_key_file=/etc/ssl/abakus/star.abakus.no.key
    smtpd_use_tls=yes
    smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
    smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache


Relay settings / Transports
***************************

We use ``smtp-relay.gmail.com`` for outgoing mail.

main.cf
::

    smtp_sasl_auth_enable = yes
    smtp_sasl_security_options = noanonymous
    header_size_limit = 4096000
    smtp_tls_policy_maps = hash:/etc/postfix/tls_policy
    transport_maps = hash:/etc/postfix/transport

tls_policy
::

    [smtp-relay.gmail.com]:587	encrypt

transport
::

    <restricted_address>@<restricted_domain>    lmtp:[<lmtp_host>]:<lmtp_port>
    * 		smtp:[smtp-relay.gmail.com]:587


Other common settings
*********************

The most important parts of these settings is the RPL lists. Consider this as an example.

main.cf
::

    smtpd_relay_restrictions =
        permit_mynetworks
        permit_sasl_authenticated
        defer_unauth_destination
        reject_invalid_hostname
        reject_non_fqdn_sender
        reject_unknown_sender_domain
        reject_unknown_recipient_domain
        reject_unauth_pipelining
        reject_rbl_client bl.spamcop.net
        reject_rbl_client sbl-xbl.spamhaus.org
        reject_rbl_client cbl.abuseat.org
        reject_rbl_client b.barracudacentral.org
        check_policy_service inet:127.0.0.1:10023  # PostGrey

    mydestination = luke.abakus.no, localhost.abakus.no, localhost, abakus.no, nyitrondheim.no, hs.abakus.no

    mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 129.241.208.0/23
    mailbox_size_limit = 0
    recipient_delimiter = +
    inet_interfaces = all
    inet_protocols = ipv4

    # Spamassassin Milter
    milter_protocol = 2
    milter_default_action = accept
    smtpd_milters = unix:/spamass/spamass.sock
    milter_connect_macros = i j {daemon_name} v {if_name} _
