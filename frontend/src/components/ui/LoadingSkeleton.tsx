type LoadingSkeletonProps = {
  lines?: number;
  label?: string;
  className?: string;
};

export function LoadingSkeleton({
  lines = 3,
  label = "Loading content",
  className = "",
}: LoadingSkeletonProps) {
  return (
    <div
      className={`ui-loading-skeleton ${className}`.trim()}
      role="status"
      aria-label={label}
    >
      {Array.from({ length: lines }, (_, index) => (
        <span key={index} />
      ))}
    </div>
  );
}
