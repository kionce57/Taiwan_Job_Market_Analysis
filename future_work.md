# Future Work - Taiwan Job Market Analysis

## Architecture Overview

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    Frontend     │ ──▶ │   API Router     │ ──▶ │   Repository    │
│  (React/Charts) │     │  (dashboard.py)  │     │ (repository.py) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
     Consumes              Transforms              SQL Queries
     JSON Response         DataFrame → Model       Business Logic
```

---

## Where to Modify

| Want to change...                                      | Modify...                               |
|--------------------------------------------------------|-----------------------------------------|
| SQL query logic (aggregation, filters)                 | `repository.py`                         |
| Data transformation (percentages, formatting)          | `dashboard.py` (router)                 |
| Response schema (add new fields)                       | `models/dashboard.py` + frontend types  |
| Chart visualization                                    | Frontend components                     |

### API Contract Stability

As long as the response models in `models/dashboard.py` remain unchanged, the frontend won't break. You can freely modify:

- SQL queries
- Table joins
- Aggregation logic
- Filter conditions

The repository is your data access layer - change queries there without touching the API interface.

---

## Frontend Chart Files

| File                  | Chart Type                            | Data Field         |
|-----------------------|---------------------------------------|--------------------|
| `TrendChart.tsx`      | Line chart (job count + salary)       | `data.trend`       |
| `SkillsChart.tsx`     | Bar chart (top skills)                | `data.skills`      |
| `RegionsChart.tsx`    | Pie/Donut chart (job by region)       | `data.regions`     |
| `IndustryChart.tsx`   | Pie chart (job by industry)           | `data.industries`  |
| `SalaryDistChart.tsx` | Bar chart (salary distribution)       | `data.salaryDist`  |
| `BaseChart.tsx`       | Shared loading skeleton               | N/A                |

---

## Key Chart Structure

All charts follow this pattern:

```tsx
// Example: SkillsChart.tsx

interface SkillsChartProps {
  data?: CategoryPoint[];  // <-- Data from API
  loading?: boolean;
}

export function SkillsChart({ data, loading }: SkillsChartProps) {
  // 1. Loading state
  if (loading || !data) return <ChartSkeleton />;
  
  // 2. Transform data for chart library (Recharts)
  const chartData = data.map(item => ({
    name: item.label,
    value: item.value,
  }));
  
  // 3. Render chart using Recharts components
  return (
    <BarChart data={chartData}>
      <XAxis dataKey="name" />
      <YAxis />
      <Bar dataKey="value" fill="#0ea5e9" />
    </BarChart>
  );
}
```

---

## Chart Modification Guide

| Want to...                     | Change...                                      |
|--------------------------------|------------------------------------------------|
| Change chart type (bar → pie)  | Use different Recharts component               |
| Change colors                  | `fill`, `stroke` props or `chartColors` config |
| Change data mapping            | `chartData` transformation                     |
| Add new chart                  | Create new file + add to `dashboardConfig.ts`  |