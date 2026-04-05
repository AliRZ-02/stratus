ContainerMemoryIssues:

Issues:
Container memory usage is critically high (near limit) or has already been OOMKilled (exit code 137). Caused by: memory leak (linear growth over time independent of load), undersized memory limit, load-driven spike (legitimate burst exceeding limit), Java/JVM off-heap memory not accounted for in limit, or unbounded caches/connection pools.

Diagnosis:
- Check pod termination reason — "OOMKilled" and exit code "137" confirms OOM kill
- Check previous container logs ("--previous") for "OutOfMemory", "heap", "GC overhead", "allocation failed"
- Review memory metrics trend over 24h:
  - Steady linear growth regardless of load → likely memory leak
  - Spikes correlated with request rate → legitimate burst, limit too low
  - Drops after restart then climbs again → confirms leak
- For JVM apps: check heap vs off-heap usage — off-heap (NIO, native) counts against container limit but not heap metrics
- Check if memory limit equals request (Guaranteed QoS) — appropriate for memory-sensitive workloads
- Check VPA recommendations if configured

Mitigation:
- Immediate: increase memory limit to stop OOMKills
- If memory leak: profile app, fix object retention, add cache eviction policies; consider heap dump on OOM ("-XX:+HeapDumpOnOutOfMemoryError")
- If load-driven spike: increase limit or horizontally scale to distribute memory load
- If JVM off-heap: set heap size ("-Xmx") to leave headroom for off-heap within container limit
- If unbounded cache/pool: cap pool size and add eviction policies
