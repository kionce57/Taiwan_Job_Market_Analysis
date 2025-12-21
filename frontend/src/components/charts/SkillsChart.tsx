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

interface SkillsChartProps {
  data: CategoryPoint[] | undefined;
  loading?: boolean;
}

/**
 * Top Skills Horizontal Bar Chart
 * Shows top 10 in-demand skills
 */
export function SkillsChart({ data, loading }: SkillsChartProps) {
  // Take top 10 and reverse for horizontal display (top at top)
  const chartData = data?.slice(0, 10).reverse();

  return (
    <BaseChart loading={loading || !data}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
        >
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fontSize: 12, fill: '#334155' }}
            axisLine={false}
            tickLine={false}
            width={55}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number) => [`${value} 個職缺`, '需求數']}
          />
          <Bar
            dataKey="value"
            radius={[0, 6, 6, 0]}
            maxBarSize={24}
          >
            {chartData?.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={chartColors.palette[index % chartColors.palette.length]}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </BaseChart>
  );
}
