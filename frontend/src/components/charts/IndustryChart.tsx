import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { CategoryPoint } from '@/types/market';
import { chartColors } from '@/config/dashboardConfig';
import { BaseChart } from './BaseChart';

interface IndustryChartProps {
  data: CategoryPoint[] | undefined;
  loading?: boolean;
}

/**
 * Industry Distribution Donut Chart
 * Groups industries < 5% as "Other"
 */
export function IndustryChart({ data, loading }: IndustryChartProps) {
  // Group small industries into "Other"
  const processedData = (() => {
    if (!data) return [];
    
    const threshold = 5;
    const mainIndustries: CategoryPoint[] = [];
    let otherValue = 0;
    let otherPercentage = 0;

    data.forEach((item) => {
      if ((item.percentage ?? 0) >= threshold) {
        mainIndustries.push(item);
      } else {
        otherValue += item.value;
        otherPercentage += item.percentage ?? 0;
      }
    });

    if (otherValue > 0) {
      mainIndustries.push({
        label: '其他',
        value: otherValue,
        percentage: otherPercentage,
      });
    }

    return mainIndustries;
  })();

  return (
    <BaseChart loading={loading || !data}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={processedData}
            cx="50%"
            cy="50%"
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={2}
            dataKey="value"
            nameKey="label"
            stroke="none"
          >
            {processedData.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={chartColors.palette[index % chartColors.palette.length]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number, _name: string, props: { payload?: CategoryPoint }) => {
              const percentage = props.payload?.percentage;
              return [`${value} (${percentage?.toFixed(1)}%)`, '職缺數'];
            }}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            iconType="circle"
            iconSize={10}
            formatter={(value: string) => (
              <span className="text-xs text-slate-600">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </BaseChart>
  );
}
