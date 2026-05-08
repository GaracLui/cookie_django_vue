### Step 1 — Configure rootless Podman (one-time setup per user)
```
# Enable lingering so containers survive logout
loginctl enable-linger $USER

# Make sure subuid/subgid are configured for your user
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER

# Restart the user namespace
podman system migrate

```
#### Enable the Podman socket (needed by podman-compose)
```bash
systemctl --user enable --now podman.socket

# Verify it's running
systemctl --user status podman.socket
```
Persist containers after logout
```
bashloginctl enable-linger $USER
```
