# knot-fog-stack

## Development

## Initialize Swarm mode

In your deployment machine, initialize Docker Swarm mode:

```bash
docker swarm init
```

## Configure DNS

This stack uses [Traefik](https://traefik.io) as a reverse proxy for the services and requires that you configure your DNS server to point, at least, the **things**, **users**, **bt** and **connector** subdomains to the machine where the stack is being deployed, so that it can route the requests to the appropriated service. It is possible to configure it to route by path or port, but instructions for that won't be provided here for brevity.

If you don't have a domain or can't configure the main DNS server, you can configure a test domain in your machine before proceeding. Either setup a local DNS server, e.g. [bind9](https://wiki.debian.org/Bind9), or alternatively update your hosts file to include the following addresses:

```
127.0.0.1	things
127.0.0.1	users
127.0.0.1	bt
127.0.0.1	connector
```

## Deploy

Deploy the stage 1 services:

```bash
docker stack deploy -c stage-1.yml knot-fog
```