import { ReactNode } from 'react';

interface BentoGridProps {
  children: ReactNode;
}

/**
 * Responsive Bento Grid Layout
 * 12 columns on desktop, 1 column on mobile
 */
export function BentoGrid({ children }: BentoGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 p-4 md:p-6 max-w-[1600px] mx-auto">
      {children}
    </div>
  );
}

interface BentoCardProps {
  title: string;
  colSpan?: number;
  rowSpan?: number;
  children: ReactNode;
}

/**
 * Bento Grid Card with glassmorphism styling
 */
export function BentoCard({ title, colSpan = 4, rowSpan = 1, children }: BentoCardProps) {
  return (
    <div
      className={`
        chart-card
        col-span-1 md:col-span-${colSpan}
        ${rowSpan > 1 ? `row-span-${rowSpan}` : ''}
        min-h-[300px]
        flex flex-col
      `}
      style={{
        gridColumn: `span ${colSpan} / span ${colSpan}`,
        gridRow: rowSpan > 1 ? `span ${rowSpan} / span ${rowSpan}` : undefined,
      }}
    >
      <h2 className="chart-title">{title}</h2>
      <div className="flex-1 min-h-0">
        {children}
      </div>
    </div>
  );
}
