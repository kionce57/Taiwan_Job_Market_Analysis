/**
 * Dashboard Data Types
 * Single Source of Truth - matches backend Pydantic models
 */

export interface TimeSeriesPoint {
  date: string;
  jobCount: number;
  avgSalary: number;
}

export interface CategoryPoint {
  label: string;
  value: number;
  percentage?: number;
}

export interface DashboardMeta {
  lastUpdated: string;
  totalJobs: number;
}

export interface DashboardData {
  meta: DashboardMeta;
  trend: TimeSeriesPoint[];
  skills: CategoryPoint[];
  regions: CategoryPoint[];
  industries: CategoryPoint[];
  salaryDist: CategoryPoint[];
}

export interface ChartConfig {
  id: string;
  title: string;
  colSpan: number;
  rowSpan?: number;
  type: 'trend' | 'skills' | 'regions' | 'industries' | 'salary';
}
