# Nexkosmo Site Move Checklist

Use this checklist when physically relocating Nexkosmo infrastructure to another property while keeping the same ISP.

## 1. Before booking the move

- Contact Aussie Broadband and confirm whether the existing static public IP/block can move to the new property.
- Confirm the new property connection type and activation date.
- Ask whether there will be any period when the old and new services overlap.
- Do not cancel the old connection until the new service is proven working.

## 2. Record the current network

- Photograph the UDM Pro connections.
- Photograph the 10G switch connections.
- Label every Ethernet/fibre cable before unplugging it.
- Record VLAN IDs and subnet assignments.
- Preserve Server 1's current internal address: `192.168.20.156`.
- Record Server 2, storage, access points and management addresses.
- Export/backup the UDM configuration.

## 3. Record the public-facing configuration

- Record current public/static IP addresses.
- Record DNS entries for `nexkosmo.com`.
- Record Staging/API-related DNS entries.
- Record firewall and port-forwarding rules.
- Record any Cloudflare configuration.
- Record Nginx public endpoints.
- Record certificates and certificate expiry dates.
- Do not change DNS before confirming whether the static IP is transferring.

## 4. Protect Nexkosmo before shutdown

- Finish at a clean deployment STOP-GATE.
- Record which release SHA is currently active.
- Record which candidate SHA is awaiting deployment.
- Back up PostgreSQL.
- Back up critical Server 1 configuration.
- Verify the backup can actually be read.
- Preserve the Staging deployment backups.
- Push all completed repository work to GitHub.
- Make sure no migration, build, render or deployment is running.

## 5. Shutdown order

1. Stop application workloads cleanly.
2. Stop Server 2 GPU workloads.
3. Shut down Server 2.
4. Shut down Server 1 cleanly.
5. Shut down storage systems.
6. Shut down switches/access points.
7. Shut down UDM Pro last.
8. Disconnect UPS power after equipment has shut down.

## 6. Physical transport

- Transport servers upright and securely supported.
- Remove or secure loose heavy components if necessary.
- Protect RTX 3090 and other large GPUs from shock.
- Protect hard-drive arrays from vibration and impact.
- Keep network equipment, cables and labelled accessories together.
- Avoid leaving servers in a hot vehicle.

## 7. New property — power first

- Check power outlets and circuit capacity before reconnecting.
- Position UPS before servers.
- Connect UDM/router.
- Connect 10G switch.
- Connect Server 1.
- Connect Server 2.
- Connect storage.
- Connect access points.
- Keep the same physical/network topology where practical.

## 8. Bring the network online

- Start modem/NTD.
- Start UDM Pro.
- Confirm WAN connection.
- Confirm public IP.
- If the static IP transferred, compare it with the recorded value.
- Start switch and access points.
- Verify VLANs are operating.
- Verify DHCP/static assignments.
- Verify `192.168.20.156` still reaches Server 1.

## 9. Start Nexkosmo infrastructure

- Start storage first if Server 1 depends on it.
- Start Server 1.
- Verify PostgreSQL.
- Verify Docker.
- Verify Nginx.
- Verify Staging containers.
- Verify health endpoints.
- Verify Server 2 can communicate with Server 1.
- Only then start GPU/render workers.

## 10. Public connectivity test

- Test `nexkosmo.com`.
- Test Staging externally.
- Test API endpoints.
- Test authentication/Keycloak.
- Test HTTPS certificates.
- Test DNS resolution from outside the local network.
- Test from a phone using mobile data, not Wi-Fi.

## 11. If the public IP changes

- Do not randomly change server configuration.
- Update the required DNS records deliberately.
- Update Cloudflare/origin configuration if applicable.
- Check firewall/NAT rules.
- Re-test HTTPS.
- Re-test Staging and API externally.
- Allow DNS propagation before diagnosing unrelated systems.

## 12. Final Nexkosmo acceptance

- Server 1 healthy.
- Server 2 healthy.
- Database healthy.
- Nginx healthy.
- Staging healthy.
- Authentication working.
- GitHub connectivity working.
- Codex SSH/deployment access working under the same restricted permissions.
- Backups healthy.
- Public website reachable.
- No unexpected Production changes.
- Record the new site's final public IP, network layout and test results.

## Permanent move rule

Preserve the internal network exactly where practical, then handle the public IP separately.

Do not physically move the infrastructure while a deployment correction is mid-flight. Reach a clean STOP-GATE, record the state, verify backups, then shut down.