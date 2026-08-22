/**
 * ===============================================================================
 * GLOBAL SUPERSTORE ANALYTICS STUDIO - INTERACTIVE ENGINE & VISUALIZATIONS
 * ===============================================================================
 */

// Global Dashboard State
let rawData = null;
let filteredCube = [];
let chartInstances = {};

// Color Palette Constants
const COLORS = {
  indigo: '#6366f1',
  indigoAlpha: 'rgba(99, 102, 241, 0.4)',
  emerald: '#10b981',
  emeraldAlpha: 'rgba(16, 185, 129, 0.4)',
  amber: '#f59e0b',
  rose: '#f43f5e',
  roseAlpha: 'rgba(244, 63, 94, 0.4)',
  cyan: '#06b6d4',
  purple: '#a855f7',
  slate: '#64748b',
  textSecondary: '#9ca3af',
  gridColor: 'rgba(255, 255, 255, 0.06)'
};

// Chart.js Global Theme Defaults
Chart.defaults.color = COLORS.textSecondary;
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.92)';
Chart.defaults.plugins.tooltip.titleColor = '#fff';
Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.12)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.boxPadding = 4;
Chart.defaults.plugins.tooltip.usePointStyle = true;

// Number Formatting Helpers
const formatCurrency = (val) => {
  if (Math.abs(val) >= 1_000_000) {
    return '$' + (val / 1_000_000).toFixed(2) + 'M';
  } else if (Math.abs(val) >= 1_000) {
    return '$' + (val / 1_000).toFixed(1) + 'K';
  }
  return '$' + val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatNumber = (val) => val.toLocaleString();
const formatPercent = (val) => (val >= 0 ? '' : '-') + Math.abs(val).toFixed(2) + '%';

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  setupTabNavigation();
  setupEventListeners();
  await loadDashboardData();
});

// Tab Navigation Logic
function setupTabNavigation() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add('active');
        // Trigger resize for charts in newly active tab
        Object.values(chartInstances).forEach(chart => chart.resize());
      }
    });
  });
}

// Event Listeners for Filters and Actions
function setupEventListeners() {
  const filterIds = ['year-select', 'market-select', 'category-select', 'segment-select'];
  filterIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => applyFilters());
    }
  });

  const resetBtn = document.getElementById('reset-filters-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      filterIds.forEach(id => {
        document.getElementById(id).value = 'ALL';
      });
      applyFilters();
    });
  }

  const copyDaxBtn = document.getElementById('copy-dax-btn');
  if (copyDaxBtn) {
    copyDaxBtn.addEventListener('click', () => {
      const codeText = document.querySelector('#dax-code-viewer code').innerText;
      navigator.clipboard.writeText(codeText).then(() => {
        const originalText = copyDaxBtn.innerHTML;
        copyDaxBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
        setTimeout(() => { copyDaxBtn.innerHTML = originalText; }, 2000);
      });
    });
  }

  const exportBtn = document.getElementById('export-summary-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

// Load Analytical JSON Data
async function loadDashboardData() {
  try {
    const res = await fetch('dashboard_data.json');
    if (!res.ok) throw new Error('Failed to load dashboard_data.json');
    rawData = await res.json();
    filteredCube = rawData.cube;
    renderAll();
  } catch (err) {
    console.error('Error loading dashboard data:', err);
  }
}

// Apply Slicer Filters
function applyFilters() {
  if (!rawData || !rawData.cube) return;

  const selectedYear = document.getElementById('year-select').value;
  const selectedMarket = document.getElementById('market-select').value;
  const selectedCategory = document.getElementById('category-select').value;
  const selectedSegment = document.getElementById('segment-select').value;

  filteredCube = rawData.cube.filter(row => {
    if (selectedYear !== 'ALL' && row.Year.toString() !== selectedYear) return false;
    if (selectedMarket !== 'ALL' && row.Market !== selectedMarket) return false;
    if (selectedCategory !== 'ALL' && row.Category !== selectedCategory) return false;
    if (selectedSegment !== 'ALL' && row.Segment !== selectedSegment) return false;
    return true;
  });

  renderAll();
}

// Render All Components
function renderAll() {
  updateKPICards();
  renderMonthlyTrendChart();
  renderCategoryDonutChart();
  renderYoYTable();
  renderSegmentBarChart();
  renderMarketBarChart();
  renderCountryTables();
  renderSubCategoryChart();
  renderDiscountMarginChart();
  renderSubCategoryMatrixTable();
  renderShipModeCharts();
}

// Update Top Ribbon KPI Cards
function updateKPICards() {
  let totalSales = 0;
  let totalProfit = 0;
  let totalOrders = 0;
  let totalShipping = 0;
  let totalQuantity = 0;
  let lossCount = 0;
  let lossAmount = 0;

  filteredCube.forEach(r => {
    totalSales += r.Sales;
    totalProfit += r.Profit;
    totalOrders += r.Orders;
    totalShipping += r.Shipping_Cost;
    totalQuantity += r.Quantity;
    if (r.Profit < 0) {
      lossCount += r.Row_Count;
      lossAmount += Math.abs(r.Profit);
    }
  });

  const marginPct = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;
  const aov = totalOrders > 0 ? totalSales / totalOrders : 0;

  document.getElementById('kpi-sales').innerText = formatCurrency(totalSales);
  document.getElementById('kpi-profit').innerText = formatCurrency(totalProfit);
  document.getElementById('kpi-margin').innerText = formatPercent(marginPct);
  document.getElementById('kpi-orders').innerText = formatNumber(totalOrders);
  document.getElementById('kpi-loss').innerText = formatCurrency(lossAmount);

  // Dynamic status badges
  const profitBadge = document.getElementById('kpi-profit-badge');
  if (totalProfit >= 0) {
    profitBadge.className = 'kpi-badge positive';
    profitBadge.innerHTML = `<i class="fa-solid fa-arrow-trend-up"></i> Net Gain: ${formatCurrency(totalProfit)}`;
  } else {
    profitBadge.className = 'kpi-badge negative';
    profitBadge.innerHTML = `<i class="fa-solid fa-arrow-trend-down"></i> Net Deficit: ${formatCurrency(totalProfit)}`;
  }

  const marginBadge = document.getElementById('kpi-margin-badge');
  if (marginPct >= 12.0) {
    marginBadge.className = 'kpi-badge positive';
    marginBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> High Margin Tier`;
  } else if (marginPct >= 8.0) {
    marginBadge.className = 'kpi-badge neutral';
    marginBadge.innerHTML = `<i class="fa-solid fa-bullseye"></i> Moderate Margin Tier`;
  } else {
    marginBadge.className = 'kpi-badge negative';
    marginBadge.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Below Target (< 8%)`;
  }

  document.getElementById('kpi-aov-badge').innerHTML = `<i class="fa-solid fa-receipt"></i> Avg AOV: $${aov.toFixed(2)}`;
}

// Chart 1: Monthly Revenue & Profit Trajectory (Tab 1)
function renderMonthlyTrendChart() {
  const ctx = document.getElementById('monthlyTrendChart');
  if (!ctx) return;

  // Aggregate monthly data based on rawData.monthly_trends or filtered year
  const selectedYear = document.getElementById('year-select').value;
  let trends = rawData.monthly_trends;
  if (selectedYear !== 'ALL') {
    trends = trends.filter(t => t.Year.toString() === selectedYear);
  }

  const labels = trends.map(t => t.YearMonth);
  const salesData = trends.map(t => t.Sales);
  const profitData = trends.map(t => t.Profit);

  if (chartInstances['monthlyTrend']) {
    chartInstances['monthlyTrend'].destroy();
  }

  chartInstances['monthlyTrend'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Gross Sales ($)',
          data: salesData,
          borderColor: COLORS.indigo,
          backgroundColor: 'rgba(99, 102, 241, 0.15)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          yAxisID: 'y'
        },
        {
          label: 'Net Profit ($)',
          data: profitData,
          borderColor: COLORS.emerald,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [4, 4],
          tension: 0.35,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { color: COLORS.gridColor } },
        y: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => formatCurrency(v) }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { callback: (v) => formatCurrency(v) }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Chart 2: Category Revenue Donut (Tab 1)
function renderCategoryDonutChart() {
  const ctx = document.getElementById('categoryDonutChart');
  if (!ctx) return;

  const catMap = {};
  filteredCube.forEach(r => {
    catMap[r.Category] = (catMap[r.Category] || 0) + r.Sales;
  });

  const labels = Object.keys(catMap);
  const data = Object.values(catMap);

  if (chartInstances['catDonut']) {
    chartInstances['catDonut'].destroy();
  }

  chartInstances['catDonut'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [COLORS.indigo, COLORS.amber, COLORS.cyan],
        borderColor: '#111827',
        borderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 12, padding: 15, color: '#e2e8f0' }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.raw)}`
          }
        }
      }
    }
  });
}

// Table: YoY Growth Matrix (Tab 1)
function renderYoYTable() {
  const tbody = document.getElementById('yoyTableBody');
  if (!tbody) return;

  const yoyData = [
    { year: 2011, sales: 2259451, salesYoY: '—', profit: 248941, profitYoY: '—', margin: '11.02%', orders: '4,440' },
    { year: 2012, sales: 2677439, salesYoY: '+18.50%', profit: 307415, profitYoY: '+23.49%', margin: '11.48%', orders: '5,343' },
    { year: 2013, sales: 3405746, salesYoY: '+27.20%', profit: 406935, profitYoY: '+32.37%', margin: '11.95%', orders: '6,721' },
    { year: 2014, sales: 4299866, salesYoY: '+26.25%', profit: 504166, profitYoY: '+23.89%', margin: '11.73%', orders: '8,531' }
  ];

  tbody.innerHTML = yoyData.map(row => `
    <tr>
      <td><strong>${row.year}</strong></td>
      <td>${formatCurrency(row.sales)}</td>
      <td><span class="badge-pill bg-indigo">${row.salesYoY}</span></td>
      <td>${formatCurrency(row.profit)}</td>
      <td><span class="badge-pill bg-emerald">${row.profitYoY}</span></td>
      <td><strong>${row.margin}</strong></td>
      <td>${row.orders}</td>
    </tr>
  `).join('');
}

// Chart 3: Segment Bar Chart (Tab 1)
function renderSegmentBarChart() {
  const ctx = document.getElementById('segmentBarChart');
  if (!ctx) return;

  const segMap = {};
  filteredCube.forEach(r => {
    if (!segMap[r.Segment]) segMap[r.Segment] = { sales: 0, profit: 0 };
    segMap[r.Segment].sales += r.Sales;
    segMap[r.Segment].profit += r.Profit;
  });

  const labels = Object.keys(segMap);
  const sales = labels.map(l => segMap[l].sales);
  const profits = labels.map(l => segMap[l].profit);

  if (chartInstances['segmentBar']) chartInstances['segmentBar'].destroy();

  chartInstances['segmentBar'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Sales ($)',
          data: sales,
          backgroundColor: COLORS.indigo,
          borderRadius: 6
        },
        {
          label: 'Profit ($)',
          data: profits,
          backgroundColor: COLORS.emerald,
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => formatCurrency(v) }
        }
      }
    }
  });
}

// Chart 4: Market Hub Performance (Tab 2)
function renderMarketBarChart() {
  const ctx = document.getElementById('marketBarChart');
  if (!ctx) return;

  const marketMap = {};
  filteredCube.forEach(r => {
    if (!marketMap[r.Market]) marketMap[r.Market] = { sales: 0, profit: 0 };
    marketMap[r.Market].sales += r.Sales;
    marketMap[r.Market].profit += r.Profit;
  });

  const labels = Object.keys(marketMap).sort((a, b) => marketMap[b].sales - marketMap[a].sales);
  const sales = labels.map(l => marketMap[l].sales);
  const margins = labels.map(l => (marketMap[l].sales > 0 ? (marketMap[l].profit / marketMap[l].sales) * 100 : 0));

  if (chartInstances['marketBar']) chartInstances['marketBar'].destroy();

  chartInstances['marketBar'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Gross Sales ($)',
          data: sales,
          backgroundColor: COLORS.indigo,
          borderRadius: 6,
          yAxisID: 'y'
        },
        {
          label: 'Profit Margin %',
          data: margins,
          type: 'line',
          borderColor: COLORS.amber,
          backgroundColor: COLORS.amber,
          borderWidth: 3,
          pointRadius: 5,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => formatCurrency(v) }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { callback: (v) => v.toFixed(1) + '%' }
        }
      }
    }
  });
}

// Tables: Top 10 Profitable vs Bottom 10 Loss-Making Countries (Tab 2)
function renderCountryTables() {
  const topBody = document.getElementById('topCountryBody');
  const bottomBody = document.getElementById('bottomCountryBody');
  if (!topBody || !bottomBody || !rawData) return;

  topBody.innerHTML = rawData.top_10_countries.map(c => `
    <tr>
      <td><strong>${c.Country}</strong></td>
      <td><span class="badge-pill bg-cyan">${c.Market}</span></td>
      <td>${formatCurrency(c.Sales)}</td>
      <td class="text-emerald"><strong>${formatCurrency(c.Profit)}</strong></td>
      <td><span class="badge-pill bg-emerald">${c.Margin_Pct.toFixed(1)}%</span></td>
    </tr>
  `).join('');

  bottomBody.innerHTML = rawData.bottom_10_countries.map(c => `
    <tr>
      <td><strong>${c.Country}</strong></td>
      <td><span class="badge-pill bg-rose">${c.Market}</span></td>
      <td>${formatCurrency(c.Sales)}</td>
      <td class="text-rose"><strong>${formatCurrency(c.Profit)}</strong></td>
      <td><span class="badge-pill bg-rose">${(c.Avg_Discount * 100).toFixed(0)}% Disc</span></td>
    </tr>
  `).join('');
}

// Chart 5: Sub-Category Profitability Spectrum (Tab 3)
function renderSubCategoryChart() {
  const ctx = document.getElementById('subCategoryChart');
  if (!ctx) return;

  const subMap = {};
  filteredCube.forEach(r => {
    if (!subMap[r.Sub_Category]) subMap[r.Sub_Category] = { sales: 0, profit: 0 };
    subMap[r.Sub_Category].sales += r.Sales;
    subMap[r.Sub_Category].profit += r.Profit;
  });

  const labels = Object.keys(subMap).sort((a, b) => subMap[b].sales - subMap[a].sales);
  const profits = labels.map(l => subMap[l].profit);
  const bgColors = profits.map(p => (p >= 0 ? COLORS.emerald : COLORS.rose));

  if (chartInstances['subCatBar']) chartInstances['subCatBar'].destroy();

  chartInstances['subCatBar'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Net Profit ($)',
        data: profits,
        backgroundColor: bgColors,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => formatCurrency(v) }
        },
        y: { grid: { display: false } }
      }
    }
  });
}

// Chart 6: Discount % vs Margin % Scatter Plot (Tab 3)
function renderDiscountMarginChart() {
  const ctx = document.getElementById('discountMarginChart');
  if (!ctx) return;

  if (!rawData || !rawData.category_summary) return;

  const scatterData = rawData.category_summary.map(c => ({
    x: c.Avg_Discount * 100,
    y: c.Margin_Pct,
    label: c.Sub_Category
  }));

  if (chartInstances['discountScatter']) chartInstances['discountScatter'].destroy();

  chartInstances['discountScatter'] = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Sub-Categories',
        data: scatterData,
        backgroundColor: (ctx) => {
          const raw = ctx.raw;
          return raw && raw.y < 0 ? COLORS.rose : COLORS.indigo;
        },
        pointRadius: 8,
        pointHoverRadius: 11
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: 'Average Discount (%)', color: COLORS.textSecondary },
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => v + '%' }
        },
        y: {
          title: { display: true, text: 'Profit Margin (%)', color: COLORS.textSecondary },
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => v + '%' }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.raw.label}: ${ctx.raw.x.toFixed(1)}% Disc -> ${ctx.raw.y.toFixed(1)}% Margin`
          }
        }
      }
    }
  });
}

// Table: Sub-Category Matrix (Tab 3)
function renderSubCategoryMatrixTable() {
  const tbody = document.getElementById('subCatMatrixBody');
  if (!tbody || !rawData || !rawData.category_summary) return;

  tbody.innerHTML = rawData.category_summary.map(item => {
    const isLoss = item.Profit < 0;
    return `
      <tr>
        <td>${item.Category}</td>
        <td><strong>${item.Sub_Category}</strong></td>
        <td>${formatNumber(item.Quantity)}</td>
        <td>${formatCurrency(item.Sales)}</td>
        <td>${(item.Avg_Discount * 100).toFixed(1)}%</td>
        <td class="${isLoss ? 'text-rose' : 'text-emerald'}"><strong>${formatCurrency(item.Profit)}</strong></td>
        <td>${item.Margin_Pct.toFixed(2)}%</td>
        <td>
          <span class="badge-pill ${isLoss ? 'bg-rose' : 'bg-emerald'}">
            ${isLoss ? 'Loss Maker' : 'Profitable'}
          </span>
        </td>
      </tr>
    `;
  }).join('');
}

// Charts: Ship Mode Volume & Cost (Tab 4)
function renderShipModeCharts() {
  const ctxMode = document.getElementById('shipModeChart');
  const ctxCost = document.getElementById('shipCostChart');
  if (!ctxMode || !ctxCost || !rawData || !rawData.ship_mode_summary) return;

  const summary = rawData.ship_mode_summary;
  const labels = summary.map(s => s['Ship Mode']);
  const volumes = summary.map(s => s.Orders);
  const avgCosts = summary.map(s => s.Avg_Cost);

  if (chartInstances['shipMode']) chartInstances['shipMode'].destroy();
  chartInstances['shipMode'] = new Chart(ctxMode, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Order Volume',
        data: volumes,
        backgroundColor: [COLORS.indigo, COLORS.cyan, COLORS.amber, COLORS.rose],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => formatNumber(v) }
        }
      }
    }
  });

  if (chartInstances['shipCost']) chartInstances['shipCost'].destroy();
  chartInstances['shipCost'] = new Chart(ctxCost, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Avg Shipping Cost ($)',
        data: avgCosts,
        backgroundColor: [COLORS.emerald, COLORS.cyan, COLORS.amber, COLORS.rose],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: COLORS.gridColor },
          ticks: { callback: (v) => '$' + v.toFixed(2) }
        }
      }
    }
  });
}
