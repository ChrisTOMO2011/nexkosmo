type ToastProps = {
  message: string;
  tone?: "neutral" | "success" | "warning" | "danger";
};

export function Toast({ message, tone = "neutral" }: ToastProps) {
  return (
    <div
      className={`ui-toast ui-toast--${tone} status-announcer`}
      role="status"
      aria-live="polite"
    >
      {message}
    </div>
  );
}
