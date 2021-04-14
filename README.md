API for serving icons and fetching new ones.

## Getting Started

Install requirements.

## Running it as a service

```
nano /etc/systemd/system/icons.service
```

```
[Unit]
Description=API for serving icons and fetching new ones
After=network.target
[Service]
User=root
Group=root
WorkingDirectory=/root/git/pi-remote
ExecStart=uvicorn main:app --reload --port 5010 --host 0.0.0.0
[Install]
WantedBy=multi-user.target
```

```
systemctl enable icons
systemctl start icons
systemctl restart icons
systemctl status icons
```