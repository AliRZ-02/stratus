Control: Plane Component Lifecycle Summary

Key Issues:
* Startup Failures: Core components (Scheduler, Controller-Manager, Etcd) failing to start or crashlooping due to configuration errors or missing certificates.
* Component Unavailability: Controller Manager disappearing from Prometheus discovery or failing to reconcile resource states (Deployments, ReplicaSets).
* Resource Exhaustion: Control plane components killed by OOM killer or throttled by high CPU usage.

Diagnosis:
1.  Status Audit: "kubectl describe pods -n kube-system -l tier=control-plane".
2.  Configuration Check: Verify static pod manifests in "/etc/kubernetes/manifests" for invalid flags or volume mounts.
3.  Dependency Health: Confirm etcd is reachable and that the API server is accepting requests.
4.  Journal Logs: SSH to control plane nodes; check "journalctl -u kubelet" and component logs for startup fatal errors.
5.  Metrics Check: Identify if Prometheus can scrape component "/metrics" endpoints.

Mitigation:
* Config Repair: Revert recent configuration changes or fix invalid flags in manifests.
* Node Stability: Address MemoryPressure or DiskPressure on control plane nodes.
* Certificate Fix: Renew expired control plane certificates or fix RBAC for service accounts.
* Process Recovery: Restart the affected service or delete the static pod to trigger a restart by the Kubelet.