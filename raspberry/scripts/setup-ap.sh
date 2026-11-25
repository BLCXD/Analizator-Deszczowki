#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || ${#2} -lt 8 ]]; then
  echo "Usage: sudo $0 <wifi-name> <wifi-password (at least 8 characters)>" >&2
  exit 2
fi

ssid=$1
password=$2
connection=ad-esp32-ap

if nmcli -t -f NAME connection show | grep -Fxq "$connection"; then
  nmcli connection modify "$connection" \
    connection.autoconnect yes \
    802-11-wireless.ssid "$ssid" \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.psk "$password" \
    ipv4.method shared \
    ipv4.addresses 10.42.0.1/24 \
    ipv4.dns "10.42.0.1" \
    ipv4.dns-search "deszczowka.io" \
    ipv4.dns-priority -50 \
    ipv6.method disabled
else
  nmcli connection add type wifi ifname wlan0 con-name "$connection" ssid "$ssid" \
    connection.autoconnect yes 802-11-wireless.mode ap 802-11-wireless.band bg \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.psk "$password" \
    ipv4.method shared ipv4.addresses 10.42.0.1/24 ipv4.dns "10.42.0.1" \
    ipv4.dns-search "deszczowka.io" ipv4.dns-priority -50 ipv6.method disabled
fi

nmcli connection up "$connection"
echo "ADE Wi-Fi is available; local portal: https://baza.deszczowka.io/"
