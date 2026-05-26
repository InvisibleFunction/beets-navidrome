# beets-navidrome

This is a plugin for integrating Navidrome with Beets.

Currently it implements a listener to trigger a library rescan on import.

## Installation
`pip`:

```
pip install git+https://github.com/InvisibleFunction/beets-navidrome
```

## Configuration

Add `beets-navidrome` to your list of plugins in your configfile:

```
plugins: beets_navidrome
```

Configure your server in your beets config:

```
beets_navidrome:
  host: mynavidromehost.example.com
  port: "443"
  secure: true
  username: guy
  password: "12345"
```

All available options (and their defaults):

```
beets_navidrome:
  host: "localhost"
  port: "4533" # Must be a string
  secure: False
  username: "admin"
  password: "admin"
  api_version: "1.16.1"
```

## Functionality

* `import` listener to trigger rescan on import
* `navstatus` subcommand to check scanning status
* `navrescan` subcommand to manually trigger rescan

```
me@compy:~$ beet navidromestatus
beets-navidrome: Navidrome not currently scanning
me@compy:~$ beet navidromerescan
beets-navidrome: Navidrome library rescan triggered
me@compy:~$ beet navidromestatus
beets-navidrome: Navidrome Library scan in progress
```
