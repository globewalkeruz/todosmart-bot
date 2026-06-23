export function SkeletonCard({ height = 80 }: { height?: number }) {
  return (
    <div
      className="skeleton"
      style={{ height, borderRadius: 'var(--r-card)' }}
    />
  );
}

export function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, padding: '0 16px' }}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} height={74 + (i % 2) * 16} />
      ))}
    </div>
  );
}

export function SkeletonStatChips() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, padding: '0 16px' }}>
      {Array.from({ length: 3 }).map((_, i) => (
        <SkeletonCard key={i} height={72} />
      ))}
    </div>
  );
}
