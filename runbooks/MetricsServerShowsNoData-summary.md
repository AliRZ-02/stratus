MetricsServerShowsNoData:

Issues:
Metrics server not collecting or reporting resource metrics. Caused by: metrics-server pod in "CrashLoopBackOff"/"Failed", inability to reach kubelet on nodes (port 10250), TLS/certificate issues, missing RBAC permissions, or "v1beta1.metrics.k8s.io" APIService not registered. Results in broken "kubectl top", disabled HPA, and loss of resource visibility.

Diagnosis:
- Check metrics-server pod status in "kube-system"; inspect logs for startup errors, RBAC failures, or invalid flags
- Run "kubectl top pod" / "kubectl top node" — errors confirm metrics API is unavailable
- Check logs for "unable to fetch metrics from node" → kubelet unreachable
- Check logs for certificate errors → TLS misconfiguration between metrics-server and kubelet
- Verify APIService is registered: "kubectl get apiservice v1beta1.metrics.k8s.io"
- If HPA shows "unknown" metrics: confirm target pods have resource requests set

Mitigation:
- If pod is crashing: fix RBAC permissions, invalid flags, or certificate config; restart pod
- If kubelet unreachable: add "--kubelet-insecure-tls" flag (self-signed cert environments); confirm kubelet is up on port 10250
- If APIService missing: reinstall metrics-server
- To isolate kubelet vs. metrics-server: run "curl -k https://<node-ip>:10250/stats/summary" from a debug pod
- If issue followed a deployment change: roll back metrics-server to previous revision
