#!/usr/bin/env python3

import click
from fabric import Connection
from invoke import UnexpectedExit


@click.command()
@click.argument("host")
def main(host):
    connection = Connection(host)
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
        connection.run("git clone http://www.github.com/andrewgodwin/rfid-inventory /srv/rfid-inventory")
    # Install packages
    click.echo(click.style("Installing Python packages...", fg="green", bold=True))
    connection.sudo("pip3 install -r /srv/rfid-inventory/client-chafon/requirements.txt")


if __name__ == "__main__":
    main()
