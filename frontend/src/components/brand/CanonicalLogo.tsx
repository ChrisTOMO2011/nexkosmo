import canonicalLogoUrl from "../../../../assets/brand/nexkosmo-x-star.svg?url";

type CanonicalLogoProps = {
  compact?: boolean;
};

export function CanonicalLogo({ compact = false }: CanonicalLogoProps) {
  return (
    <a className="canonical-brand" href="/studio" aria-label="Nexkosmo home">
      <img
        className="canonical-brand__mark"
        src={canonicalLogoUrl}
        alt=""
        width="64"
        height="64"
        data-canonical-asset="assets/brand/nexkosmo-x-star.svg"
      />
      {!compact && (
        <span className="canonical-brand__wordmark" aria-hidden="true">
          <strong>NEXKOSMO</strong>
          <small>Your AI Producer</small>
        </span>
      )}
    </a>
  );
}
