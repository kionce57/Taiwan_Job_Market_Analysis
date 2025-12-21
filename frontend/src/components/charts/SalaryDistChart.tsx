import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { CategoryPoint } from '@/types/market';
import { chartColors } from '@/config/dashboardConfig';
import { BaseChart } from './BaseChart';

interface SalaryDistChartProps {
  data: CategoryPoint[] | undefined;
  loading?: boolean;
}

/**
 * Salary Distribution Area Chart
 * Shows salary ranges with median marker
 */
export function SalaryDistChart({ data, loading }: SalaryDistChartProps) {
  // Calculate median position (simplified - middle of highest value range)
  const medianIndex = (() => {
    if (!data?.length) return 0;
    let totalCount = 0;
    data.forEach(d => totalCount += d.value);
    const halfCount = totalCount / 2;
    let cumulative = 0;
    for (let i = 0; i < data.length; i++) {
      cumulative += data[i].value;
      if (cumulative >= halfCount) return i;
    }
    return data.length - 1;
  })();

  const medianLabel = data?.[medianIndex]?.label ?? '';

  return (
    <BaseChart loading={loading || !data}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="salaryGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.success} stopOpacity={0.8} />
              <stop offset="95%" stopColor={chartColors.success} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
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
              return [`${value} (${percentage?.toFixed(1) ?? 'N/A'}%)`, '職缺數'];
            }}
          />
          <ReferenceLine
            x={medianLabel}
            stroke={chartColors.accent}
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{
              value: '中位數',
              position: 'top',
              fill: chartColors.accent,
              fontSize: 11,
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={chartColors.success}
            strokeWidth={2}
            fill="url(#salaryGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </BaseChart>
  );
}
