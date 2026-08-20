import { Toast } from "../../../../components/ui";

type DomainStatusNoticeProps = {
  message: string;
};

export function DomainStatusNotice({ message }: DomainStatusNoticeProps) {
  return <Toast message={message} />;
}
