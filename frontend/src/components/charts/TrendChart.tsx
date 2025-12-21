import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { TimeSeriesPoint } from '@/types/market';
import { chartColors } from '@/config/dashboardConfig';
import { BaseChart } from './BaseChart';

interface TrendChartProps {
  data: TimeSeriesPoint[] | undefined;
  loading?: boolean;
}

/**
 * Hero Chart: Composed Line + Bar
 * Shows job count (bars) vs average salary (line)
 */
export function TrendChart({ data, loading }: TrendChartProps) {
  return (
    <BaseChart loading={loading || !data}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: '#64748b' }}
            tickFormatter={(value: string) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
            axisLine={{ stroke: '#e2e8f0' }}
            tickLine={false}
          />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 12, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value: number) => `${value}`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value: number) => `${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number, name: string) => {
              if (name === 'avgSalary') {
                return [`$${value.toLocaleString()}`, '平均薪資'];
              }
              return [value, '職缺數'];
            }}
            labelFormatter={(label: string) => {
              const date = new Date(label);
              return date.toLocaleDateString('zh-TW');
            }}
          />
          <Legend
            formatter={(value: string) => {
              return value === 'jobCount' ? '職缺數' : '平均薪資';
            }}
          />
          <Bar
            yAxisId="left"
            dataKey="jobCount"
            fill={chartColors.primaryLight}
            fillOpacity={0.8}
            radius={[4, 4, 0, 0]}
            name="jobCount"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avgSalary"
            stroke={chartColors.primaryDark}
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: chartColors.primaryDark }}
            name="avgSalary"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </BaseChart>
  );
}
