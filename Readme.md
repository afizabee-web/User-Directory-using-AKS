The app shows real data from a PostgreSQL StatefulSet running inside AKS:
✅ View all existing users in a live registry
✅ Create individual users instantly
✅ Bulk-generate test users with one click
✅ Dashboard shows Total Users, API Status, and DB Pods (3/3) — all live

But what makes this project special isn't the UI. It's what's running underneath.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 1. StatefulSets — Because databases aren't stateless
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PostgreSQL runs as a StatefulSet (not a Deployment). Why?
✅ Stable pod names: postgress-0, postgress-1, postgress-2
✅ Each pod gets its OWN PersistentVolumeClaim on Azure Managed Disk
✅ Ordered startup/shutdown prevents data corruption

💥 Real bug I hit: PostgreSQL refused to initialize because Azure Disk creates a "lost+found" directory at the mount root.
Fix: Set PGDATA to /var/lib/postgresql/data/pgdata (a subdirectory) — one line that saved hours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 2. AGIC — Azure Application Gateway Ingress Controller
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instead of running NGINX pods inside the cluster, AGIC uses Azure's managed Application Gateway. The controller translates Kubernetes Ingress rules into App Gateway config via ARM APIs.

Result: Built-in WAF, Azure-native SSL, zero in-cluster LB pods to manage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 3. Workload Identity — Zero secrets stored anywhere
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No passwords in Kubernetes Secrets. No long-lived client secrets. Just short-lived JWTs signed by the AKS OIDC issuer.

The auth chain:
Pod token → Azure AD → validates Federated Identity Credential → returns access token → Key Vault unlocked 🔓

💥 Real bug I hit: Error AADSTS700213 — federated credential existed but the subject didn't match the namespace.
Lesson: You need ONE federated credential PER namespace. Cost me 2 hours. Won't forget it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗝️ 4. Azure Key Vault + CSI Driver — Secrets as files, not env vars
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Postgres credentials live in Azure Key Vault. The CSI Secrets Store Driver mounts them directly into pods at /mnt/secrets-store/ — the app reads them like files. Zero hardcoded credentials. Anywhere.

💥 Gotcha: SecretProviderClass is namespace-scoped. Had to deploy it separately in both the database and app namespaces. Easy to miss, frustrating to debug.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What you see on afizabee.online is the surface.
The real project is the infrastructure beneath it:
— 3 PostgreSQL pods with individual Azure Disks
— Secretless auth via federated identity tokens
— Secrets injected at runtime, never stored in the cluster
— Enterprise-grade ingress via Azure Application Gateway

Building this end-to-end — fighting real errors, debugging AAD token flows, dealing with StatefulSet immutability — is something no tutorial can replicate.
