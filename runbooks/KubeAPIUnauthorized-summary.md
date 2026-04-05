KubeAPIUnauthorized: (401)

Issues:
API server returns 401 Unauthorized, blocking all cluster access. Caused by: expired or invalid JWT/bearer token, expired client certificate, incorrect or misconfigured kubeconfig, deleted service account token secret, or API server authentication configuration changes.

Diagnosis:
- Confirm 401 with "kubectl auth can-i --list" — 401 means auth failure (not RBAC)
- Check kubeconfig: "kubectl config current-context" and "kubectl config view --minify"
- Decode JWT token and inspect "exp" claim for expiration
- Check client cert expiry: "openssl x509 -noout -dates" on the cert in kubeconfig
- For in-pod SA auth: confirm token is mounted at "/var/run/secrets/kubernetes.io/serviceaccount/token" and SA still exists
- Check API server logs for "401" / "unauthorized" to identify which auth method is failing
- Correlate error onset with: token expiry, kubeconfig changes, cert rotation, SA token deletion, cluster upgrades

Mitigation:
- If token expired: refresh token (re-login, rotate, or re-generate)
- If client cert expired: rotate and reissue client certificate
- If kubeconfig misconfigured: correct cluster/user/context entries
- If SA token deleted: recreate the token Secret or re-create the ServiceAccount
- If auth config changed: review and restore API server authentication settings
