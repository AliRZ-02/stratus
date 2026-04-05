KubePodImagePullBackOff:

Issues:
Pod stuck in "ImagePullBackOff" or "ErrImagePull" — kubelet cannot pull the container image. Caused by: wrong image name, tag, or digest (image doesn't exist), missing or expired "imagePullSecrets", invalid registry credentials, registry unavailable or rate-limiting, network/firewall blocking registry access (port 443), node disk full (no space for image layers), or untrusted/expired registry TLS cert.

Diagnosis:
- Check pod events for "Failed to pull image" — note the specific error: "unauthorized", "manifest unknown"/"not found", or "timeout"/"i/o timeout"
- If "unauthorized": confirm "imagePullSecrets" is set in pod spec, Secret exists in namespace, and credentials are valid and not expired (watch for time-limited tokens: ECR, GCR)
- If "not found"/"manifest unknown": verify image name, registry hostname, repo path, and tag exist in registry
- If "timeout": test registry connectivity from a debug pod ("curl https://<registry>/v2/"); check NetworkPolicies and firewall egress rules
- If rate-limited (Docker Hub): confirm authenticated pull credentials are configured
- Check node disk space in "/var/lib/containerd" or "/var/lib/docker"
- Verify ServiceAccount has "imagePullSecrets" attached if using SA-based credentials

Mitigation:
- If wrong image/tag: fix image reference in Deployment spec
- If missing/expired credentials: recreate "imagePullSecrets" with valid credentials and reference in pod spec
- If registry unreachable: fix NetworkPolicy egress, firewall rules, or proxy config
- If disk full: free space on node or trigger image garbage collection
- If TLS cert untrusted: add registry CA to node container runtime trust store
- If rate-limited: add authenticated "imagePullSecrets" to avoid anonymous pull limits
