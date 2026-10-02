import { env } from "cloudflare:workers";
import { loadKnowledge } from "../../knowledge-source";

export const dynamic = "force-dynamic";
export async function GET() {
  const snapshot = await loadKnowledge((env as { GITHUB_TOKEN?: string }).GITHUB_TOKEN);
  const status = snapshot.status === "access_denied" ? 403 : snapshot.status === "rate_limited" ? 429 : ["setup_required", "unavailable"].includes(snapshot.status) ? 503 : 200;
  return Response.json(snapshot, {
    status,
    headers: { "Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff", ...(snapshot.retryAfterSeconds ? { "Retry-After": String(snapshot.retryAfterSeconds) } : {}) },
  });
}
