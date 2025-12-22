import { useState, FormEvent } from 'react';
import { RefreshCw, TrendingUp, Briefcase, Search, X } from 'lucide-react';
import { BentoGrid, BentoCard } from '@/components/layout/BentoGrid';
import { TrendChart } from '@/components/charts/TrendChart';
import { SkillsChart } from '@/components/charts/SkillsChart';
import { RegionsChart } from '@/components/charts/RegionsChart';
import { IndustryChart } from '@/components/charts/IndustryChart';
import { SalaryDistChart } from '@/components/charts/SalaryDistChart';
import { useDashboardData } from '@/hooks/useDashboardData';
import { dashboardConfig } from '@/config/dashboardConfig';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const { data, loading, error, refetch } = useDashboardData(activeFilter ?? undefined);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = searchTerm.trim();
    setActiveFilter(trimmed || null);
  };

  const clearSearch = () => {
    setSearchTerm('');
    setActiveFilter(null);
  };

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

          {/* Search Box */}
          <form onSubmit={handleSearch} className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="搜尋職缺名稱，例如：Python、前端工程師..."
                className="w-full pl-10 pr-10 py-2 text-sm border border-slate-200 rounded-xl bg-white/50 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition-all"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-100 rounded-full transition-colors"
                >
                  <X className="w-3 h-3 text-slate-400" />
                </button>
              )}
            </div>
          </form>
          
          <div className="flex items-center gap-4">
            {/* Active Filter Badge */}
            {activeFilter && (
              <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-primary-50 border border-primary-200 rounded-full text-sm">
                <span className="text-primary-700">篩選: {activeFilter}</span>
                <button onClick={clearSearch} className="hover:bg-primary-100 rounded-full p-0.5">
                  <X className="w-3 h-3 text-primary-500" />
                </button>
              </div>
            )}

            {data?.meta && (
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary-500" />
                  <span className="text-slate-600">
                    {activeFilter ? '符合職缺' : '總職缺'}: <span className="font-semibold text-slate-800">{data.meta.totalJobs.toLocaleString()}</span>
                  </span>
                </div>
                <div className="text-slate-400">
                  更新: {new Date(data.meta.lastUpdated).toLocaleString('zh-TW')}
                </div>
              </div>
            )}
            
            <button
              onClick={() => refetch()}
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
            <button onClick={() => refetch()} className="ml-2 underline hover:no-underline">
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
