import { PageHeader } from "@/components/widgets";
import { ChatPanel } from "@/components/ChatPanel";
import { isAIConfigured } from "@/services/ai/client";

export default function ChatPage() {
  return (
    <>
      <PageHeader title="AI Assistant" subtitle="Grounded in your engine — ask about captains, transfers, differentials, boosts" />
      <ChatPanel aiEnabled={isAIConfigured()} />
    </>
  );
}
