import { Bot, ExternalLink } from "lucide-react";
import { Button } from "../../../../components/ui";
import sophiaReference from "../../../../assets/discovery/build-moment-reference.jpeg";
import type {
  ActiveProducerProfile,
  ProducerContextMetadata,
} from "./domain-workspace.types";

type ActiveProducerPanelProps = {
  profile?: ActiveProducerProfile;
  context: ProducerContextMetadata;
  onDeferredConversation: () => void;
};

export function ActiveProducerPanel({
  profile,
  context,
  onDeferredConversation,
}: ActiveProducerPanelProps) {
  const displayName = profile?.displayName ?? "Sophia";
  const roleLabel = profile?.roleLabel ?? "AI Producer";
  const actionSubject = profile
    ? profile.displayName.split(/\s+/u)[0]
    : "Sophia";
  const showSophiaPortrait = /(^|\s)sophia(\s|$)/iu.test(displayName);

  return (
    <section
      className="copilot-card"
      data-domain={context.domain}
      data-project-id={context.projectId}
      data-production-id={context.productionId}
      data-entity-id={context.entityId}
      data-provider-status={profile?.providerStatus ?? "not-configured"}
    >
      <div className="copilot-heading">
        <span
          className={`bot-orbit${showSophiaPortrait ? " producer-portrait producer-portrait--sophia" : ""}`}
          style={
            showSophiaPortrait
              ? { backgroundImage: `url(${sophiaReference})` }
              : undefined
          }
          aria-hidden="true"
        >
          {!showSophiaPortrait && <Bot aria-hidden="true" />}
        </span>
        <strong>{displayName}</strong>
      </div>
      <p>{roleLabel}</p>
      <Button
        trailingIcon={<ExternalLink aria-hidden="true" />}
        onClick={onDeferredConversation}
      >
        Ask {actionSubject}
      </Button>
    </section>
  );
}
