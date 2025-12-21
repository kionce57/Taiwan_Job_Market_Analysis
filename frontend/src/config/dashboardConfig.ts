import type { ChartConfig } from '@/types/market';

/**
 * Dashboard Layout Configuration
 * Config-driven rendering for Bento Grid layout
 */
export const dashboardConfig: ChartConfig[] = [
  {
    id: 'hero-trend',
    title: '市場熱度趨勢',
    colSpan: 8,
    rowSpan: 2,
    type: 'trend',
  },
  {
    id: 'top-skills',
    title: '熱門技能 Top 10',
    colSpan: 4,
    type: 'skills',
  },
  {
    id: 'region-dist',
    title: '職缺地理分佈',
    colSpan: 4,
    type: 'regions',
  },
  {
    id: 'industry-dist',
    title: '產業佔比',
    colSpan: 4,
    type: 'industries',
  },
  {
    id: 'salary-dist',
    title: '薪資分佈',
    colSpan: 4,
    type: 'salary',
  },
];

export const chartColors = {
  primary: '#0ea5e9',
  primaryLight: '#38bdf8',
  primaryDark: '#0369a1',
  secondary: '#8b5cf6',
  accent: '#f59e0b',
  success: '#10b981',
  slate: '#64748b',
  
  // Gradient palette for charts
  palette: [
    '#0ea5e9',
    '#8b5cf6',
    '#f59e0b',
    '#10b981',
    '#ef4444',
    '#ec4899',
    '#6366f1',
    '#14b8a6',
    '#f97316',
    '#84cc16',
  ],
};
