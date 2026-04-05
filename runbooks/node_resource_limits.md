Node: Resource and Capacity Management Summary

Key Issues:
* Disk Pressure: Available disk space or inodes below eviction thresholds (caused by logs, image cache, or emptyDir).
* CPU Saturation: High utilization (>80-90%) leading to container throttling, latency, and Kubelet unresponsiveness.
* FD Exhaustion: Number of open files/sockets approaching "fs.file-max" or per-process limits.
* Pod Density: Node exceeding 95% of its pod capacity (default 110), straining the CRI and CNI.

Diagnosis:
1.  Resource Profiling: "kubectl top node" and "kubectl describe node" to identify the specific pressure condition.
2.  Top Consumers: Identify pods with high usage or those lacking resource limits.
3.  Disk Analysis: SSH to node; check "/var/log" and "/var/lib/containerd/" (or docker) for growth.
4.  FD Audit: Use "lsof" or check "/proc/sys/fs/file-nr" to see current vs. max file descriptors.
5.  Scheduling: Check for uneven pod distribution or "hot spots" due to affinity rules.

Mitigation:
* Workload Rebalance: Cordon and drain the node to redistribute pods.
* Disk Cleanup: Adjust Kubelet GC thresholds; prune unused images; fix log rotation.
* Limits: Increase system limits ("sysctl -w fs.file-max"); add resource requests/limits to runaway pods.
* Scaling: Trigger cluster autoscaler or manually add nodes to reduce pod density.