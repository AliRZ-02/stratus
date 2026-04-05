KubeProxyFailing:

Issues:
kube-proxy pods in "CrashLoopBackOff" or "Failed", breaking all ClusterIP/NodePort service routing. Caused by: API server unreachable (kube-proxy can't sync rules), node resource pressure (MemoryPressure, DiskPressure), misconfigured iptables/ipvs mode in ConfigMap, missing kernel modules, or incompatibility after a cluster upgrade.

Diagnosis:
- List kube-proxy pods in "kube-system" — identify which nodes are affected
- Check kube-proxy logs for: API server connection errors, panics, or fatal startup failures
- If API server errors: verify API server health and kube-proxy service account permissions
- Check node conditions for "MemoryPressure", "DiskPressure", or "PIDPressure"
- Describe kube-proxy DaemonSet — confirm pods are being scheduled on all nodes
- Check kube-proxy ConfigMap for correct "mode" (iptables vs ipvs) and network interface settings
- If post-upgrade: verify kube-proxy version compatibility with cluster version

Mitigation:
- If API server unreachable: restore API server connectivity; fix service account RBAC
- If resource pressure: free node resources or add capacity
- If config error: fix kube-proxy ConfigMap and restart DaemonSet
- If kernel modules missing: load required modules on affected nodes
- If upgrade incompatibility: align kube-proxy version with cluster version
