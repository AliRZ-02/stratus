AutoscalerScalingTooSlowly:

Issues:
Cluster autoscaler scales nodes too slowly relative to workload demand, leaving pods pending longer than acceptable. Caused by: conservative autoscaler config parameters, slow cloud provider node provisioning, autoscaler scan interval latency, single-node-at-a-time expansion config, or cloud provider API rate limiting.

Diagnosis:
- Check autoscaler ConfigMap for conservative settings: "scan-interval", "scale-down-delay-after-add", "max-node-provision-time", "max-nodes-per-time"
- Review autoscaler logs for throttling, rate limiting, or retry messages
- Compare pending pod wait duration vs. autoscaler "scan-interval" (default 10s)
- Check time between scale-up decision and node "Ready" state — long gaps indicate cloud provisioning delays
- Verify "expander" config and "max-nodes-total" — autoscaler may be adding only one node per cycle

Mitigation:
- Reduce "scan-interval" for faster reaction to pending pods
- Increase "max-nodes-per-time" or adjust expander to allow larger scale-up batches
- If cloud provisioning is slow: consider pre-warmed node pools or faster instance types
- If API rate limiting: optimize autoscaler API call frequency or request higher cloud provider limits
- If node startup is slow: investigate node bootstrap/system pod scheduling delays
