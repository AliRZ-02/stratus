Certificate: and Trust Management Summary

Key Issues:
* Expiration: Certificates (Ingress, mTLS, or Client) expiring in <30 days or failing to rotate automatically.
* Issuance Failures: Cert-manager unable to fulfill requests due to failing ACME challenges (HTTP-01/DNS-01) or invalid "Issuers".
* System Downtime: Cert-manager controller or webhook down, blocking all certificate operations.
* Auth Failure: Expired client certificates causing TLS handshake failures for cluster components.

Diagnosis:
1.  Resource Status: "kubectl get certificate,certificaterequest,order,challenge -A". Look for "Ready=False" or "Pending".
2.  Controller Health: Verify "cert-manager" namespace pods; check logs for API access denied or leader election issues.
3.  Challenge Verification: For ACME, verify DNS records or Ingress path accessibility from the internet.
4.  Metadata Audit: Inspect "lastTransitionTime" and error messages in "kubectl describe certificate".
5.  Issuer Check: Confirm "Issuer" or "ClusterIssuer" status and verify credentials (API keys, secrets).

Mitigation:
* Manual Renewal: Delete the Certificate's Secret to force a re-issuance attempt.
* Fix Infrastructure: Adjust firewall/Ingress to allow ACME validation; fix DNS propagation issues.
* System Recovery: Restart cert-manager pods; reinstall CRDs if corrupted; fix RBAC permissions.
* Client Fix: Manually approve pending CSRs for node/client rotation failures.