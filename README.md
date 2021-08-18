# python-ddns

## Installation
```sh
make deploy
```
```sh
systemctl status ddnsc-daemon
```

## Examples
```json
{
    "volatile": true,
    "filter": {
        "conf": {
            "interfaces": ["eth0"]
        }
    },
    "database": {
        "name": "cloudflare",
        "conf": {
            "conf": {
                "email": "user@example.com",
                "token": "c2547eb745079dac9320b638f5e225cf483cc5cfdda41"
            },
            "zone": "example.com",
            "name": "@"
        }
    }
}
```

## Housekeeping
### `.gitignore`
The `.gitignore` file of this repo is generated by the following command:

```sh
curl -L https://github.com/github/gitignore/raw/master/{Python,Global/{Linux,Windows,macOS,Vim,SublimeText,VisualStudioCode}}.gitignore > .gitignore
```