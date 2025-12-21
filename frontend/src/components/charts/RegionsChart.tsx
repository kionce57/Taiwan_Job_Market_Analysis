import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { CategoryPoint } from '@/types/market';
import { chartColors } from '@/config/dashboardConfig';
import { BaseChart } from './BaseChart';

interface RegionsChartProps {
  data: CategoryPoint[] | undefined;
  loading?: boolean;
}

/**
 * Regional Distribution Bar Chart
 * Placeholder for future heatmap implementation
 */
export function RegionsChart({ data, loading }: RegionsChartProps) {
  return (
    <BaseChart loading={loading || !data}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 20, left: 20, bottom: 40 }}
        >
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: '#64748b' }}
            angle={-45}
            textAnchor="end"
            axisLine={false}
            tickLine={false}
            height={60}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number, _name: string, props: { payload?: CategoryPoint }) => {
              const percentage = props.payload?.percentage;
              return [`${value} (${percentage?.toFixed(1) ?? '—'}%)`, '職缺數'];
            }}
          />
          <Bar
            dataKey="value"
            radius={[6, 6, 0, 0]}
            maxBarSize={40}
          >
            {data?.map((entry, index) => {
              // Color intensity based on percentage
              const opacity = entry.percentage 
                ? Math.max(0.4, Math.min(1, entry.percentage / 30))
                : 0.8;
              return (
                <Cell
                  key={`cell-${index}`}
                  fill={chartColors.secondary}
                  fillOpacity={opacity}
                />
              );
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </BaseChart>
  );
}
