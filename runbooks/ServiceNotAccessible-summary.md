ServiceNotAccessible:

Issues:
Service is unreachable or connections are refused. Caused by: no ready endpoints (empty selector match, pods not Ready), port or targetPort misconfiguration, kube-proxy not running or iptables/ipvs rules stale, NetworkPolicy blocking ingress traffic, CoreDNS not resolving service name, or application not listening on the expected port.

Diagnosis:
- Describe Service — check selector, ports, and targetPort
- Check Endpoints/EndpointSlices — if empty: selector mismatch or pods not Ready
- If selector matches but endpoints empty: check pod "Ready" condition and readiness probe failures
- If endpoints exist but connections refused: verify application is listening on "targetPort" inside the container
- Check kube-proxy pods in "kube-system" — if failing, iptables/ipvs rules won't be programmed
- Test DNS: "nslookup <service>.<namespace>.svc.cluster.local" from a debug pod
- Review NetworkPolicies in namespace for rules blocking ingress to backend pods

Mitigation:
- If selector mismatch: fix service selector or pod labels
- If pods not Ready: fix failing readiness probes or application startup issues
- If port mismatch: align "port"/"targetPort" in Service spec with container port
- If kube-proxy failing: restart kube-proxy DaemonSet and investigate logs
- If NetworkPolicy blocking: add ingress rule permitting service traffic
- If DNS broken: follow CoreDNS diagnosis (see "ServiceNotResolvingDNS")
