import { env } from "cloudflare:workers";
import ArchiveBrowser from "./archive-browser";
import { loadKnowledge } from "./knowledge-source";

export const dynamic = "force-dynamic";
export default async function Page() {
  const snapshot = await loadKnowledge((env as { GITHUB_TOKEN?: string }).GITHUB_TOKEN);
  return <ArchiveBrowser initialSnapshot={snapshot} />;
}
