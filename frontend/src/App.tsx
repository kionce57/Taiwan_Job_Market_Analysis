import { RefreshCw, TrendingUp, Briefcase } from 'lucide-react';
import { BentoGrid, BentoCard } from '@/components/layout/BentoGrid';
import { TrendChart } from '@/components/charts/TrendChart';
import { SkillsChart } from '@/components/charts/SkillsChart';
import { RegionsChart } from '@/components/charts/RegionsChart';
import { IndustryChart } from '@/components/charts/IndustryChart';
import { SalaryDistChart } from '@/components/charts/SalaryDistChart';
import { useDashboardData } from '@/hooks/useDashboardData';
import { dashboardConfig } from '@/config/dashboardConfig';

function App() {
  const { data, loading, error, refetch } = useDashboardData();

  const renderChart = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendChart data={data?.trend} loading={loading} />;
      case 'skills':
        return <SkillsChart data={data?.skills} loading={loading} />;
      case 'regions':
        return <RegionsChart data={data?.regions} loading={loading} />;
      case 'industries':
        return <IndustryChart data={data?.industries} loading={loading} />;
      case 'salary':
        return <SalaryDistChart data={data?.salaryDist} loading={loading} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200/50">
        <div className="max-w-[1600px] mx-auto px-4 md:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl shadow-lg shadow-primary-500/20">
              <Briefcase className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">職缺市場儀表板</h1>
              <p className="text-xs text-slate-500">Taiwan Job Market Dashboard</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {data?.meta && (
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary-500" />
                  <span className="text-slate-600">
                    總職缺: <span className="font-semibold text-slate-800">{data.meta.totalJobs.toLocaleString()}</span>
                  </span>
                </div>
                <div className="text-slate-400">
                  更新: {new Date(data.meta.lastUpdated).toLocaleString('zh-TW')}
                </div>
              </div>
            )}
            
            <button
              onClick={refetch}
              disabled={loading}
              className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors disabled:opacity-50"
              title="重新載入"
            >
              <RefreshCw className={`w-5 h-5 text-slate-600 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="max-w-[1600px] mx-auto px-4 md:px-6 pt-4">
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
            載入失敗: {error}
            <button onClick={refetch} className="ml-2 underline hover:no-underline">
              重試
            </button>
          </div>
        </div>
      )}

      {/* Dashboard Grid */}
      <main className="pb-8">
        <BentoGrid>
          {dashboardConfig.map((config) => (
            <BentoCard
              key={config.id}
              title={config.title}
              colSpan={config.colSpan}
              rowSpan={config.rowSpan}
            >
              {renderChart(config.type)}
            </BentoCard>
          ))}
        </BentoGrid>
      </main>
    </div>
  );
}

export default App;
