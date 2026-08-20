import { Toast } from "../../../../components/ui";
import {
  getDeferredActionMessage,
  type DeferredActionId,
} from "./deferred-action.messages";

type DeferredActionNoticeProps = {
  action: DeferredActionId;
};

export function DeferredActionNotice({ action }: DeferredActionNoticeProps) {
  return <Toast message={getDeferredActionMessage(action)} tone="warning" />;
}
