API Server Health and Performance Summary

Key Issues
- Availability: API server instances unreachable, crashlooping, or returning "connection refused."
- Latency & Timeouts: Requests exceeding 1s thresholds or failing with "context deadline exceeded" and "request timeout."
- Aggregated APIs: Intermittent 500/503 errors from aggregated endpoints (e.g., metrics-server) due to connectivity or reliability issues.
- Throttling: "TooManyRequests" errors due to client-side bursts or controller reconciliation storms.

Diagnosis
1.  Pod & Event Status: "kubectl get pods -n kube-system -l component=kube-apiserver". Filter events for "CrashLoopBackOff", "Failed", or "TooManyRequests".
2.  Latency Metrics: Inspect API server request queue depth and etcd latency metrics.
3.  Logs: Search for "panic", "fatal", "context deadline exceeded", or certificate errors in API server logs.
4.  Dependencies: Check etcd health, admission webhook response times, and control plane node CPU/Memory usage.
5.  Connectivity: Verify network paths between nodes and the API server or load balancer.

Mitigation
- Recovery: Restart API server pods or control plane nodes.
- Resource Management: Address etcd bottlenecks; scale up control plane nodes or adjust API server resource limits.
- Load Reduction: Identify and throttle abusive clients; optimize or disable slow admission webhooks.
- Infrastructure: Resolve network partitioning, firewall blocks, or load balancer failures.