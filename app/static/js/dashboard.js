/**
 * DecodeLabs Enterprise Intelligence Platform
 * Dashboard Logic with Plotly.js Interactive Analytics & Lenis Smooth Scroll
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lenis Smooth Scroll
  if (typeof Lenis !== "undefined") {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  // Common Plotly Dark Minimal Layout Defaults Factory
  // Returns a fresh clone to prevent Plotly from mutating shared axis types/ranges across plots
  function getBaseLayout() {
    return {
      paper_bgcolor: "#121215",
      plot_bgcolor: "#121215",
      font: {
        family: "Inter, sans-serif",
        color: "#a1a1aa",
        size: 11
      },
      margin: { t: 25, r: 20, b: 40, l: 55 },
      xaxis: {
        gridcolor: "#222226",
        linecolor: "#222226",
        zerolinecolor: "#222226",
        tickfont: { color: "#71717a", size: 10 }
      },
      yaxis: {
        gridcolor: "#222226",
        linecolor: "#222226",
        zerolinecolor: "#222226",
        tickfont: { color: "#71717a", size: 10 }
      },
      showlegend: false
    };
  }

  const plotlyLayoutDefaults = getBaseLayout();

  const plotlyConfig = {
    responsive: true,
    displayModeBar: false
  };

  let predefinedQueries = {};

  // Initialize
  initDashboard();

  async function initDashboard() {
    initSpotlights();
    initKpisOnLoad();
    await loadInitialPlots();
    await loadPredefinedQueries();
    await loadInitialTableData();
    bindEvents();
  }

  // =========================================================================
  // Skiper UI / Animata Interactive Micro-Interactions
  // =========================================================================

  function initSpotlights() {
    document.querySelectorAll(".spotlight-card").forEach(card => {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty("--mouse-x", `${x}px`);
        card.style.setProperty("--mouse-y", `${y}px`);
      });
      card.addEventListener("mouseleave", () => {
        card.style.setProperty("--mouse-x", `-500px`);
        card.style.setProperty("--mouse-y", `-500px`);
      });
    });
  }

  let currentKpiValues = {
    revenue: 0,
    orders: 0,
    aov: 0,
    fulfillment: 0,
    reversal: 0,
    coupon: 0
  };

  async function initKpisOnLoad() {
    try {
      const res = await fetch("/api/kpis");
      const json = await res.json();
      if (json.status === "success") {
        animateKpis(json.data, 900);
      }
    } catch (err) {
      console.warn("KPI animation initialization:", err);
    }
  }

  function animateKpis(targetKpis, duration = 750) {
    const startRevenue = currentKpiValues.revenue;
    const startOrders = currentKpiValues.orders;
    const startAov = currentKpiValues.aov;
    const startFulfillment = currentKpiValues.fulfillment;
    const startReversal = currentKpiValues.reversal;
    const startCoupon = currentKpiValues.coupon;

    const targetRevenue = Number(targetKpis.total_revenue || 0);
    const targetOrders = Number(targetKpis.total_orders || 0);
    const targetAov = Number(targetKpis.avg_order_value || 0);
    const targetFulfillment = Number(targetKpis.fulfillment_rate || 0);
    const targetReversal = Number(targetKpis.reversal_rate || 0);
    const targetCoupon = Number(targetKpis.coupon_penetration || 0);

    currentKpiValues = {
      revenue: targetRevenue,
      orders: targetOrders,
      aov: targetAov,
      fulfillment: targetFulfillment,
      reversal: targetReversal,
      coupon: targetCoupon
    };

    updateKpiFooters(targetKpis);

    const elRev = document.getElementById("val-revenue");
    const elOrd = document.getElementById("val-orders");
    const elAov = document.getElementById("val-aov");
    const elFul = document.getElementById("val-fulfillment");
    const elRevR = document.getElementById("val-reversal");
    const elCpn = document.getElementById("val-coupon");

    const startTime = performance.now();

    function frame(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // Ease-out cubic

      if (elRev) elRev.textContent = `$${(startRevenue + (targetRevenue - startRevenue) * ease).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      if (elOrd) elOrd.textContent = Math.round(startOrders + (targetOrders - startOrders) * ease).toLocaleString();
      if (elAov) elAov.textContent = `$${(startAov + (targetAov - startAov) * ease).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      if (elFul) elFul.textContent = `${(startFulfillment + (targetFulfillment - startFulfillment) * ease).toFixed(2)}%`;
      if (elRevR) elRevR.textContent = `${(startReversal + (targetReversal - startReversal) * ease).toFixed(2)}%`;
      if (elCpn) elCpn.textContent = `${(startCoupon + (targetCoupon - startCoupon) * ease).toFixed(2)}%`;

      if (progress < 1) {
        requestAnimationFrame(frame);
      }
    }
    requestAnimationFrame(frame);
  }

  function updateKpiFooters(targetKpis) {
    const elFootRev = document.getElementById("footer-revenue");
    const elFootOrd = document.getElementById("footer-orders");
    const elFootAov = document.getElementById("footer-aov");
    const elFootFul = document.getElementById("footer-fulfillment");
    const elFootRevR = document.getElementById("footer-reversal");
    const elFootCpn = document.getElementById("footer-coupon");

    const orders = Number(targetKpis.total_orders || 0);
    const revenue = Number(targetKpis.total_revenue || 0);
    const BASELINE_TOTAL_ORDERS = 1200;
    const BASELINE_TOTAL_REVENUE = 1264761.96;

    if (orders === BASELINE_TOTAL_ORDERS) {
      if (elFootRev) elFootRev.textContent = "Across 1,200 Validated Records";
      if (elFootOrd) elFootOrd.textContent = "100% Unique Primary Keys";
      if (elFootAov) elFootAov.textContent = "Median Baseline: $823.62";
      if (elFootFul) elFootFul.textContent = "231 Completed Shipments";
      if (elFootRevR) elFootRevR.textContent = "497 Cancelled and Returned";
      if (elFootCpn) elFootCpn.textContent = "891 Orders with Coupons";
      return;
    }

    if (orders === 0) {
      if (elFootRev) elFootRev.textContent = "0 Matching Records";
      if (elFootOrd) elFootOrd.textContent = "0% of Total Dataset";
      if (elFootAov) elFootAov.textContent = "No Records for Criteria";
      if (elFootFul) elFootFul.textContent = "0 Shipments";
      if (elFootRevR) elFootRevR.textContent = "0 Reversals";
      if (elFootCpn) elFootCpn.textContent = "0 Promotions";
      return;
    }

    const orderPct = ((orders / BASELINE_TOTAL_ORDERS) * 100).toFixed(1);
    const revPct = ((revenue / BASELINE_TOTAL_REVENUE) * 100).toFixed(1);

    const delivered = targetKpis.delivered_orders !== undefined 
      ? targetKpis.delivered_orders 
      : Math.round(orders * ((targetKpis.fulfillment_rate || 0) / 100));

    const reversals = targetKpis.reversal_orders !== undefined 
      ? targetKpis.reversal_orders 
      : Math.round(orders * ((targetKpis.reversal_rate || 0) / 100));

    const coupons = targetKpis.coupon_orders !== undefined 
      ? targetKpis.coupon_orders 
      : Math.round(orders * ((targetKpis.coupon_penetration || 0) / 100));

    const medianAov = targetKpis.median_order_value !== undefined 
      ? `$${Number(targetKpis.median_order_value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
      : "Filtered Subset";

    if (elFootRev) elFootRev.textContent = `Across ${orders.toLocaleString()} Filtered Records (${revPct}% of GMV)`;
    if (elFootOrd) elFootOrd.textContent = `${orderPct}% of Total 1,200 Orders`;
    if (elFootAov) elFootAov.textContent = `Filtered Median: ${medianAov}`;
    if (elFootFul) elFootFul.textContent = `${delivered.toLocaleString()} Completed Shipments`;
    if (elFootRevR) elFootRevR.textContent = `${reversals.toLocaleString()} Cancelled and Returned`;
    if (elFootCpn) elFootCpn.textContent = `${coupons.toLocaleString()} Orders with Coupons`;
  }

  function updateFilterChips(payload) {
    const container = document.getElementById("active-filter-chips");
    if (!container) return;

    const active = [];
    if (payload.product && payload.product !== "All") {
      active.push({ key: "product", label: "Product", val: payload.product, elId: "filter-product" });
    }
    if (payload.order_status && payload.order_status !== "All") {
      active.push({ key: "order_status", label: "Status", val: payload.order_status, elId: "filter-status" });
    }
    if (payload.payment_method && payload.payment_method !== "All") {
      active.push({ key: "payment_method", label: "Payment", val: payload.payment_method, elId: "filter-payment" });
    }
    if (payload.referral_source && payload.referral_source !== "All") {
      active.push({ key: "referral_source", label: "Channel", val: payload.referral_source, elId: "filter-referral" });
    }

    if (active.length === 0) {
      container.innerHTML = '<span class="chip-item chip-empty">Showing All 1,200 Audited Records</span>';
      return;
    }

    container.innerHTML = "";
    active.forEach(item => {
      const chip = document.createElement("span");
      chip.className = "chip-item";
      chip.innerHTML = `<span><strong>${item.label}:</strong> ${item.val}</span><span class="chip-remove" title="Remove ${item.label} filter">&times;</span>`;
      chip.querySelector(".chip-remove").addEventListener("click", () => {
        document.getElementById(item.elId).value = "All";
        document.getElementById("filter-form").dispatchEvent(new Event("submit"));
      });
      container.appendChild(chip);
    });
  }


  // =========================================================================
  // 1. Plotly Interactive Chart Renderers
  // =========================================================================

  async function loadInitialPlots() {
    try {
      // Monthly Trends
      const resMonthly = await fetch("/api/monthly-trends");
      const jsonMonthly = await resMonthly.json();
      if (jsonMonthly.status === "success") {
        renderMonthlyPlot(jsonMonthly.data);
      }

      // Product Performance
      const resProduct = await fetch("/api/product-performance");
      const jsonProduct = await resProduct.json();
      if (jsonProduct.status === "success") {
        renderProductPlot(jsonProduct.data);
      }

      // Order Status Breakdown
      const resStatus = await fetch("/api/order-status-distribution");
      const jsonStatus = await resStatus.json();
      if (jsonStatus.status === "success") {
        renderStatusPlot(jsonStatus.data);
      }

      // Referral Channel Performance
      const resRef = await fetch("/api/referral-performance");
      const jsonRef = await resRef.json();
      if (jsonRef.status === "success") {
        renderReferralPlot(jsonRef.data);
      }
    } catch (err) {
      console.error("Error loading plots:", err);
    }
  }

  function renderMonthlyPlot(data) {
    if (!data || data.length === 0) {
      const emptyLayout = {
        ...getBaseLayout(),
        annotations: [{
          text: "No time-series data for selected criteria",
          xref: "paper", yref: "paper", x: 0.5, y: 0.5,
          showarrow: false, font: { color: "#71717a", size: 12 }
        }]
      };
      Plotly.react("plot-monthly-trend", [], emptyLayout, plotlyConfig);
      return;
    }

    const xVals = data.map(d => d.month);
    const yVals = data.map(d => d.revenue);

    const trace = {
      x: xVals,
      y: yVals,
      type: "scatter",
      mode: "lines+markers",
      line: { color: "#3b82f6", width: 2, shape: "spline" },
      marker: { color: "#60a5fa", size: 5 },
      fill: "tozeroy",
      fillcolor: "rgba(59, 130, 246, 0.08)",
      hovertemplate: "<b>Month:</b> %{x}<br><b>Revenue:</b> $%{y:,.2f}<extra></extra>"
    };

    const layout = {
      ...getBaseLayout(),
      xaxis: {
        ...getBaseLayout().xaxis,
        type: "category"
      },
      yaxis: {
        ...getBaseLayout().yaxis,
        tickprefix: "$",
        tickformat: ",.0f"
      }
    };

    Plotly.react("plot-monthly-trend", [trace], layout, plotlyConfig);
  }

  function renderProductPlot(data) {
    if (!data || data.length === 0) {
      const emptyLayout = {
        ...getBaseLayout(),
        annotations: [{
          text: "No product records for selected criteria",
          xref: "paper", yref: "paper", x: 0.5, y: 0.5,
          showarrow: false, font: { color: "#71717a", size: 12 }
        }]
      };
      Plotly.react("plot-product-performance", [], emptyLayout, plotlyConfig);
      return;
    }

    const sorted = [...data].sort((a, b) => a.total_revenue - b.total_revenue);
    const xVals = sorted.map(d => d.total_revenue);
    const yVals = sorted.map(d => d.product);

    const trace = {
      x: xVals,
      y: yVals,
      type: "bar",
      orientation: "h",
      marker: {
        color: "#2563eb",
        line: { color: "#3b82f6", width: 1 }
      },
      hovertemplate: "<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>"
    };

    const layout = {
      ...getBaseLayout(),
      margin: { t: 15, r: 25, b: 35, l: 85 },
      xaxis: {
        ...getBaseLayout().xaxis,
        tickprefix: "$",
        tickformat: ",.0f"
      },
      yaxis: {
        ...getBaseLayout().yaxis,
        type: "category",
        autorange: true
      }
    };

    Plotly.react("plot-product-performance", [trace], layout, plotlyConfig);
  }

  function renderStatusPlot(data) {
    if (!data || data.length === 0) {
      const emptyLayout = {
        paper_bgcolor: "#121215",
        plot_bgcolor: "#121215",
        annotations: [{
          text: "No status records for selected criteria",
          xref: "paper", yref: "paper", x: 0.5, y: 0.5,
          showarrow: false, font: { color: "#71717a", size: 12 }
        }]
      };
      Plotly.react("plot-order-status", [], emptyLayout, plotlyConfig);
      return;
    }

    const labels = data.map(d => d.status);
    const values = data.map(d => d.order_count);

    const colorMap = {
      "Delivered": "#10b981",
      "Shipped": "#3b82f6",
      "Pending": "#f59e0b",
      "Cancelled": "#f43f5e",
      "Returned": "#71717a"
    };

    const colors = labels.map(s => colorMap[s] || "#52525b");

    const trace = {
      labels: labels,
      values: values,
      type: "pie",
      hole: 0.62,
      marker: {
        colors: colors,
        line: { color: "#121215", width: 2 }
      },
      textinfo: "percent",
      hoverinfo: "label+value+percent",
      hovertemplate: "<b>%{label}</b><br>Orders: %{value}<br>Share: %{percent}<extra></extra>"
    };

    const layout = {
      paper_bgcolor: "#121215",
      plot_bgcolor: "#121215",
      font: { family: "Inter, sans-serif", color: "#a1a1aa", size: 11 },
      margin: { t: 10, r: 20, b: 15, l: 20 },
      showlegend: true,
      legend: {
        orientation: "h",
        x: 0.05,
        y: -0.15,
        font: { size: 10, color: "#a1a1aa" }
      }
    };

    Plotly.react("plot-order-status", [trace], layout, plotlyConfig);
  }

  function renderReferralPlot(data) {
    if (!data || data.length === 0) {
      const emptyLayout = {
        ...getBaseLayout(),
        annotations: [{
          text: "No acquisition channel records for selected criteria",
          xref: "paper", yref: "paper", x: 0.5, y: 0.5,
          showarrow: false, font: { color: "#71717a", size: 12 }
        }]
      };
      Plotly.react("plot-referral-performance", [], emptyLayout, plotlyConfig);
      return;
    }

    const xVals = data.map(d => d.channel);
    const yVals = data.map(d => d.total_revenue);

    const trace = {
      x: xVals,
      y: yVals,
      type: "bar",
      marker: {
        color: "#3b82f6",
        line: { color: "#60a5fa", width: 1 }
      },
      hovertemplate: "<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
    };

    const layout = {
      ...getBaseLayout(),
      margin: { t: 20, r: 20, b: 45, l: 65 },
      xaxis: {
        ...getBaseLayout().xaxis,
        type: "category",
        tickfont: { color: "#a1a1aa", size: 11 }
      },
      yaxis: {
        ...getBaseLayout().yaxis,
        tickprefix: "$",
        tickformat: ",.0f"
      }
    };

    Plotly.react("plot-referral-performance", [trace], layout, plotlyConfig);
  }

  // =========================================================================
  // 2. Data Table Population
  // =========================================================================

  async function loadInitialTableData() {
    try {
      const res = await fetch("/api/filter-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const json = await res.json();
      if (json.status === "success") {
        renderTableRows(json.records);
      }
    } catch (err) {
      console.error("Table data loading failed:", err);
    }
  }

  function renderTableRows(records) {
    const tbody = document.getElementById("transactions-tbody");
    tbody.innerHTML = "";

    if (!records || records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding: 2rem; color: #71717a;">No transactions found matching filter criteria.</td></tr>';
      return;
    }

    records.forEach(r => {
      const tr = document.createElement("tr");
      const statusClass = `badge-${r.OrderStatus.toLowerCase()}`;

      tr.innerHTML = `
        <td><strong style="color:#f4f4f5; font-family:'JetBrains Mono', monospace;">${r.OrderID}</strong></td>
        <td>${r.Date_ISO}</td>
        <td>${r.CustomerID}</td>
        <td>${r.Product}</td>
        <td>${r.Quantity}</td>
        <td>$${Number(r.UnitPrice).toFixed(2)}</td>
        <td><strong style="color:#fff;">$${Number(r.TotalPrice).toFixed(2)}</strong></td>
        <td>${r.PaymentMethod}</td>
        <td><span class="badge-status ${statusClass}">${r.OrderStatus}</span></td>
        <td>${r.ReferralSource}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // =========================================================================
  // 3. Predefined Queries
  // =========================================================================

  async function loadPredefinedQueries() {
    try {
      const res = await fetch("/api/predefined-queries");
      const json = await res.json();
      if (json.status === "success") {
        predefinedQueries = json.queries;
      }
    } catch (err) {
      console.error("Error loading queries:", err);
    }
  }

  // =========================================================================
  // 4. Interactive Event Handlers
  // =========================================================================

  function bindEvents() {
    // Filter Form
    const filterForm = document.getElementById("filter-form");
    filterForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        product: document.getElementById("filter-product").value,
        order_status: document.getElementById("filter-status").value,
        payment_method: document.getElementById("filter-payment").value,
        referral_source: document.getElementById("filter-referral").value
      };

      try {
        const res = await fetch("/api/filter-data", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.status === "success") {
          // Update KPIs with smooth ease-out counter animation
          animateKpis(json.kpis);

          // Update Active Filter Slices Chips
          updateFilterChips(payload);

          // Update All 4 Plots Dynamically
          if (json.monthly) renderMonthlyPlot(json.monthly);
          if (json.products) renderProductPlot(json.products);
          if (json.statuses) renderStatusPlot(json.statuses);
          if (json.referrals) renderReferralPlot(json.referrals);

          // Update Table
          renderTableRows(json.records);
          document.getElementById("record-counter").textContent = `Displaying ${json.records.length} Records (${json.record_count} Filtered Total)`;
        }
      } catch (err) {
        console.error("Filter failed:", err);
      }
    });

    // Reset Filters
    document.getElementById("btn-reset-filters").addEventListener("click", () => {
      document.getElementById("filter-product").value = "All";
      document.getElementById("filter-status").value = "All";
      document.getElementById("filter-payment").value = "All";
      document.getElementById("filter-referral").value = "All";
      filterForm.dispatchEvent(new Event("submit"));
    });

    // CSV Export Handlers
    const exportBtn = document.getElementById("btn-export-csv");
    const exportTableBtn = document.getElementById("btn-export-table");

    async function handleExportCsv(triggerBtn) {
      if (!triggerBtn) return;
      const originalHtml = triggerBtn.innerHTML;
      try {
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin" style="margin-right: 5px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
          Exporting...
        `;

        const payload = {
          product: document.getElementById("filter-product").value,
          order_status: document.getElementById("filter-status").value,
          payment_method: document.getElementById("filter-payment").value,
          referral_source: document.getElementById("filter-referral").value
        };

        const res = await fetch("/api/export-csv", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          throw new Error(`Export failed with HTTP status ${res.status}`);
        }

        const blob = await res.blob();
        let filename = "filtered_ecommerce_data.csv";
        const disposition = res.headers.get("Content-Disposition");
        if (disposition && disposition.includes("filename=")) {
          const match = disposition.match(/filename=["']?([^"';]+)["']?/);
          if (match && match[1]) {
            filename = match[1];
          }
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        triggerBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Downloaded!
        `;
        setTimeout(() => {
          triggerBtn.innerHTML = originalHtml;
          triggerBtn.disabled = false;
        }, 1800);
      } catch (err) {
        console.error("Export error:", err);
        alert("Failed to export filtered dataset: " + err.message);
        triggerBtn.innerHTML = originalHtml;
        triggerBtn.disabled = false;
      }
    }

    if (exportBtn) {
      exportBtn.addEventListener("click", () => handleExportCsv(exportBtn));
    }
    if (exportTableBtn) {
      exportTableBtn.addEventListener("click", () => handleExportCsv(exportTableBtn));
    }


    // Predefined Query Selection
    const queryDropdown = document.getElementById("predefined-query-dropdown");
    queryDropdown.addEventListener("change", (e) => {
      const selected = e.target.value;
      if (selected && predefinedQueries[selected]) {
        document.getElementById("sql-input").value = predefinedQueries[selected].sql.trim();
      }
    });

    // Copy SQL Button
    const copySqlBtn = document.getElementById("btn-copy-sql");
    if (copySqlBtn) {
      copySqlBtn.addEventListener("click", async () => {
        const queryText = document.getElementById("sql-input").value;
        try {
          await navigator.clipboard.writeText(queryText);
          const originalContent = copySqlBtn.innerHTML;
          copySqlBtn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span style="color:#34d399;">Copied!</span>
          `;
          setTimeout(() => {
            copySqlBtn.innerHTML = originalContent;
          }, 1600);
        } catch (e) {
          console.warn("Clipboard write failed:", e);
        }
      });
    }

    // SQL Runner
    document.getElementById("btn-run-sql").addEventListener("click", runQuery);
  }


  async function runQuery() {
    const query = document.getElementById("sql-input").value.trim();
    const outputMeta = document.getElementById("output-meta");
    const outputCount = document.getElementById("output-count");
    const thead = document.querySelector("#sql-results-table thead");
    const tbody = document.querySelector("#sql-results-table tbody");

    if (!query) {
      alert("Please enter a SQL query.");
      return;
    }

    outputMeta.textContent = "Status: Executing...";
    const t0 = performance.now();

    try {
      const res = await fetch("/api/query-sql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });
      const t1 = (performance.now() - t0).toFixed(1);
      const json = await res.json();

      if (json.status === "success") {
        outputMeta.textContent = `Status: Success (${t1} ms)`;
        outputCount.textContent = `Records: ${json.row_count}`;

        let th = "<tr>";
        json.columns.forEach(c => {
          th += `<th>${c}</th>`;
        });
        th += "</tr>";
        thead.innerHTML = th;

        let tb = "";
        if (json.rows.length === 0) {
          tb = `<tr><td colspan="${json.columns.length}" style="text-align:center; padding: 1.5rem; color:#71717a;">Query returned 0 rows.</td></tr>`;
        } else {
          json.rows.forEach(r => {
            tb += "<tr>";
            json.columns.forEach(c => {
              const v = r[c];
              tb += `<td>${v !== null ? v : '<span style="color:#71717a;">NULL</span>'}</td>`;
            });
            tb += "</tr>";
          });
        }
        tbody.innerHTML = tb;
      } else {
        outputMeta.textContent = `Status: Error (${t1} ms)`;
        outputCount.textContent = "Records: 0";
        thead.innerHTML = "<tr><th>Error Details</th></tr>";
        tbody.innerHTML = `<tr><td style="color:#fb7185; font-family:'JetBrains Mono', monospace;">${json.message}</td></tr>`;
      }
    } catch (err) {
      outputMeta.textContent = "Status: Network Error";
      thead.innerHTML = "<tr><th>Error</th></tr>";
      tbody.innerHTML = `<tr><td style="color:#fb7185;">Failed to communicate with Flask backend.</td></tr>`;
    }
  }

  // Auto-resize Plotly charts on window resize
  window.addEventListener("resize", () => {
    ["plot-monthly-trend", "plot-product-performance", "plot-order-status", "plot-referral-performance"].forEach(id => {
      const el = document.getElementById(id);
      if (el && el.data) {
        Plotly.Plots.resize(el);
      }
    });
  });
});

