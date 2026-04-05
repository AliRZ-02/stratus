NodesUnreachable:

Issues:
One or more nodes marked "NotReady" or "Unknown" — kubelet unable to communicate with control plane. Caused by: CNI plugin pod failures breaking node networking, node-to-control-plane network partition, NetworkPolicy blocking kubelet port (10250), missing or incorrect routes, cloud provider networking issues (VPC/security groups), or kubelet certificate/authentication errors.

Diagnosis:
- Describe affected node — check "Ready" condition and "LastHeartbeatTime"; stale heartbeat = kubelet not communicating
- Check CNI plugin DaemonSet pods on affected node in "kube-system" — CNI failure breaks all node networking
- Run ping/connectivity test from a healthy node to the unreachable node's IP
- Review NetworkPolicies for rules that could block control plane → kubelet (port 10250) traffic
- Check node network interfaces and routes — verify route to API server and cluster network exists
- If cloud-hosted: check VPC, subnet, and security group rules for node-to-node and node-to-control-plane ports

Mitigation:
- If CNI pods failing: fix or restart CNI DaemonSet; investigate CNI plugin logs
- If network partition: restore network path between node and control plane
- If NetworkPolicy blocking: add rule permitting kubelet communication on port 10250
- If routing missing: restore correct routes on node
- If cloud networking: fix security group rules or VPC routing
- If kubelet cert error: rotate kubelet certificates
