#!/usr/bin/env python3

import click
from fabric import Connection
from invoke import UnexpectedExit


@click.command()
@click.option("--device", default="/dev/ttyUSB0")
@click.argument("host")
@click.argument("url")
@click.argument("token")
def main(host, url, token, device):
    connection = Connection(host)
    # Stop the service if it's running and installed
    click.echo(
        click.style("Stopping any existing installation...", fg="green", bold=True)
    )
    try:
        connection.sudo("systemctl stop rfid-client")
    except UnexpectedExit:
        pass
    # Ensure base tools are installed
    click.echo(click.style("Installing base tools...", fg="green", bold=True))
    connection.sudo("apt-get update -q")
    connection.sudo("apt-get install -y git python3-pip")
    # Make sure the directory is set up
    click.echo(click.style("Pulling down repo...", fg="green", bold=True))
    connection.sudo("mkdir -p /srv/rfid-inventory")
    connection.sudo("chown %s /srv/rfid-inventory" % connection.user)
    try:
        with connection.cd("/srv/rfid-inventory"):
            connection.run("git pull")
    except UnexpectedExit:
        connection.run(
            "git clone http://www.github.com/andrewgodwin/rfid-inventory /srv/rfid-inventory"
        )
    # Install packages
    click.echo(click.style("Installing Python packages...", fg="green", bold=True))
    connection.sudo(
        "pip3 install -r /srv/rfid-inventory/chafon-pc/requirements.txt"
    )
    # Write out a systemd unit file
    click.echo(click.style("Writing systemd unit file...", fg="green", bold=True))
    unit_file = unit_template.format(device=device, url=url, token=token).strip()
    connection.sudo(
        "bash -c \"echo '%s' > /etc/systemd/system/rfid-client.service\"" % unit_file
    )
    # Start it
    click.echo(click.style("Enabling and starting service...", fg="green", bold=True))
    connection.sudo("systemctl daemon-reload")
    connection.sudo("systemctl enable rfid-client")
    connection.sudo("systemctl start rfid-client")


unit_template = """
[Unit]
Description=RFID scanner client

[Service]
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/bin/python3 /srv/rfid-inventory/chafon-pc/client.py {device} {url} {token}

[Install]
WantedBy=multi-user.target
"""

if __name__ == "__main__":
    main()
