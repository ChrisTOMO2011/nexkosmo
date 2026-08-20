export type DeferredActionId =
  | "asset-upload"
  | "character-generation"
  | "producer-conversation"
  | "suggestion-application"
  | "suggestion-catalogue";

const deferredMessages: Record<DeferredActionId, string> = {
  "asset-upload":
    "Upload pipeline is not yet connected. This feature will be available in the Asset Upload and Ingestion phase.",
  "character-generation":
    "AI generation is not yet connected. This feature will be available in the AI Character Generation phase.",
  "producer-conversation":
    "Producer conversation is not yet connected. No conversation or message thread was created.",
  "suggestion-application":
    "This curated preset is not mapped to a Character command yet. No Character selection was changed.",
  "suggestion-catalogue":
    "Additional curated presets are deferred. No AI generation request was created.",
};

export function getDeferredActionMessage(action: DeferredActionId) {
  return deferredMessages[action];
}
