Kubelet: Lifecycle and Connectivity Summary

Key Issues:
* Process Failure: Kubelet service stopped, crashed (OOM/Panic), or disabled on the host.
* Auth/Certs: Expired Kubelet certificates, stuck CertificateSigningRequests (CSR), or RBAC preventing auto-renewal.
* Connectivity: Network partitioning between node and API server, or control plane unavailability causing "Unknown" status.
* Instability: Readiness flapping due to intermittent network issues or resource pressure near thresholds.

Diagnosis:
1.  Node Status: "kubectl describe node <name>" — check "Conditions" (Ready, Unknown) and "Events".
2.  Service Health: SSH to node; run "systemctl status kubelet" and "journalctl -u kubelet".
3.  Auth Check: "kubectl get csr" — look for "Pending" requests; check cert expiry on the node.
4.  Network: Verify connectivity to the API server health endpoint from the node.
5.  Runtime: Check container runtime status (containerd/docker) as Kubelet depends on it.

Mitigation:
* Recover Service: Restart Kubelet ("systemctl restart kubelet").
* Fix Auth: Manually approve pending CSRs; verify CA connectivity; fix RBAC permissions.
* Infrastructure: Resolve firewall blocks or cloud provider network failures.
* Cleanup: Address OOM or disk issues that may be causing Kubelet process crashes.