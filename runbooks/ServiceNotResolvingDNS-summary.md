ServiceNotResolvingDNS:

Issues:
Cluster-internal DNS resolution failing, breaking service discovery. Caused by: CoreDNS pods in "CrashLoopBackOff" or "OOMKilled", kube-dns Service has no endpoints, Corefile misconfiguration, upstream DNS unreachable (affects external lookups), NetworkPolicy blocking pod → CoreDNS traffic (UDP/TCP port 53), or stale DNS cache after service IP change.

Diagnosis:
- Check CoreDNS pods in "kube-system" ("k8s-app=kube-dns") — confirm "Running" and "Ready"
- Check kube-dns Service endpoints — if empty, CoreDNS pods don't have the "k8s-app=kube-dns" label or aren't Ready
- Review CoreDNS logs for: "SERVFAIL", "NXDOMAIN", "OOMKilled", config errors, or upstream timeout messages
- Test from a debug pod: "nslookup <service>.<namespace>.svc.cluster.local"
- If cluster names fail but external names work: service doesn't exist or has no ClusterIP
- If all DNS fails from pods but works from CoreDNS pod: NetworkPolicy blocking port 53 to "kube-system"
- Review ConfigMap "coredns" in "kube-system" for Corefile errors or wrong upstream servers

Mitigation:
- If CoreDNS OOMKilled: increase CoreDNS memory limits
- If Corefile misconfigured: fix ConfigMap and restart CoreDNS pods
- If no endpoints on kube-dns service: fix pod labels or readiness
- If NetworkPolicy blocking: add egress rule on affected namespaces allowing UDP/TCP port 53 to CoreDNS
- If upstream DNS unreachable: fix upstream server config in Corefile or restore network path to upstream
- If stale cache: wait for TTL expiry or restart CoreDNS pods to flush cache
