Cluster: Compute Capacity and Overcommit Summary

Key Issues:
* Resource Overcommit: Total CPU or Memory requests exceed cluster capacity, making the cluster unable to tolerate node failures without leaving pods in "Pending".
* High CPU Utilization: Nodes or control-plane components running at >80-90% CPU, causing throttling, latency spikes, and potential unresponsiveness.
* Scheduling Failures: New workloads failing to start with "InsufficientCPU" or "InsufficientMemory" errors.
* Scaling Bottlenecks: Cluster Autoscaler failing to add nodes due to cloud provider limits or quota restrictions.

Diagnosis:
1.  Capacity Audit: "kubectl describe nodes" — compare "Allocatable" against "Non-terminated Pods" requests.
2.  Top Consumers: "kubectl top node" and "kubectl top pod -A" to identify pods with high usage vs. low requests (or vice versa).
3.  Pressure Events: Check for "OOMKilled" or "CPUThrottling" in pod events; check "journalctl" for system-level resource exhaustion.
4.  Autoscaler Health: Inspect "cluster-autoscaler" logs and status configmaps for "scale up needed but not possible" messages.
5.  Control Plane: Monitor API server latency and Controller-Manager reconciliation speeds.

Mitigation:
* Scale Out: Manually add nodes or increase the maximum node count in the autoscaler configuration.
* **Right-sizing**: Adjust pod resource "requests" to match actual historical usage; implement "LimitRanges".
* Load Shedding: Cordon and drain heavily loaded nodes to redistribute traffic.
* Scheduling Optimization: Review affinity/anti-affinity rules that may be creating "hot spots" on specific nodes.