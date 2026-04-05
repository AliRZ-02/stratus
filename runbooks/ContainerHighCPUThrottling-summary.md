ContainerHighCPUThrottling:

Issues:
Container is hitting its CPU limit and being throttled by the Linux CFS scheduler, causing increased latency and reduced throughput. Caused by: CPU limit set too low relative to actual usage, bursty workload exceeding limit during spikes, inefficient application code (tight loops, excessive GC, blocking ops), or CPU requests set too low causing over-scheduling on the node.

Diagnosis:
- Calculate throttle ratio: "throttled_periods / total_periods * 100" — above 25% typically causes noticeable latency impact
- Correlate throttling timestamps with application latency/timeout metrics — confirms CPU is the bottleneck
- Check if throttling is constant (limit too low) or only during peaks (burst headroom needed)
- Compare CPU usage vs limit in metrics — if usage is consistently at the limit, the limit is undersized
- Check if throttling affects all replicas equally or only some — uneven distribution may indicate load balancer skew
- Check node CPU utilization — high node-level contention can compound throttling
- Check VPA recommendations if configured

Mitigation:
- If limit too low: increase CPU limit (and request proportionally if needed)
- If bursty but average usage is fine: widen the request-to-limit ratio to allow bursting
- If application is CPU-inefficient: profile app for hot loops, excessive GC, or blocking I/O; optimize code
- If node contention: reschedule pod to a less loaded node or add cluster capacity
- Consider removing CPU limits entirely for latency-sensitive workloads (with resource monitoring in place)
