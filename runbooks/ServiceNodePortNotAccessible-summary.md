ServiceNodePortNotAccessible:

Issues:
NodePort service unreachable from outside the cluster. Caused by: firewall/security group blocking the NodePort, kube-proxy not running (iptables/ipvs rules not programmed), no ready endpoints (selector mismatch or pods not Ready), node has no external IP or is behind NAT, or NodePort outside the valid range (30000–32767).

Diagnosis:
- Describe Service — confirm "type: NodePort" and note the assigned "nodePort"
- Check Endpoints — if empty, selector mismatch or pods not Ready
- Check kube-proxy pods in "kube-system" — if failing, NodePort rules won't be programmed
- Test with "curl <node-ip>:<node-port>" from an external client
- Check node firewall rules and cloud security groups — confirm NodePort is open for inbound traffic
- Verify nodes have a reachable external IP; if behind NAT, confirm port forwarding is configured
- Check "externalTrafficPolicy" — if "Local", only nodes running the pod will accept traffic

Mitigation:
- If firewall blocking: open NodePort in cloud security group / node iptables rules
- If no endpoints: fix pod readiness or service selector
- If kube-proxy failing: fix kube-proxy (see "KubeProxyFailing")
- If no external IP: expose via LoadBalancer service or Ingress instead
- If "externalTrafficPolicy: Local": route traffic only to nodes that have a running pod, or switch to "Cluster"
