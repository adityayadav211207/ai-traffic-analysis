// ==========================================================================
// TRAFFICVISION AI - EXECUTIVE DASHBOARD INTERACTIVE ENGINE (LIGHT MODE)
// ==========================================================================

document.addEventListener("DOMContentLoaded", function () {
    initLiveClock();
    initGlobalHotkeys();
    initSearchFilter();
    renderAllCharts();
    initDynamicInsightsStream();
});

// ==========================================================================
// 1. LIVE DIGITAL TELEMETRY CLOCK
// ==========================================================================
function initLiveClock() {
    const clockEl = document.getElementById("live-clock");
    if (!clockEl) return;

    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        clockEl.textContent = `${hours}:${minutes}:${seconds} UTC`;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

// ==========================================================================
// 2. GLOBAL KEYBOARD HOTKEYS (Ctrl + K / Cmd + K)
// ==========================================================================
function initGlobalHotkeys() {
    const searchInput = document.getElementById("dashboardSearch");
    if (!searchInput) return;

    document.addEventListener("keydown", function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
            e.preventDefault();
            searchInput.focus();
            showToast("Search mode activated", "info");
        }
    });
}

// ==========================================================================
// 3. SEARCH & CLIENT-SIDE FILTERING
// ==========================================================================
function initSearchFilter() {
    const searchInput = document.getElementById("dashboardSearch");
    if (!searchInput) return;

    searchInput.addEventListener("input", function (e) {
        const query = e.target.value.toLowerCase().trim();
        const alertItems = document.querySelectorAll(".alert-feed-item");

        alertItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query)) {
                item.style.display = "flex";
            } else {
                item.style.display = "none";
            }
        });
    });
}

// ==========================================================================
// 4. CHART.JS VISUALIZATION ENGINE FOR EXECUTIVE LIGHT MODE
// ==========================================================================

const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1000,
        easing: 'easeOutQuart'
    },
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                color: '#475569',
                font: {
                    family: 'Plus Jakarta Sans',
                    size: 12,
                    weight: '600'
                },
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle'
            }
        },
        tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#334155',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#CBD5E1',
            titleFont: { family: 'Plus Jakarta Sans', size: 13, weight: '700' },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
            displayColors: true
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#64748B',
                font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }
            },
            grid: {
                color: '#F1F5F9',
                drawBorder: false
            }
        },
        y: {
            beginAtZero: true,
            ticks: {
                color: '#64748B',
                font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
                color: '#E2E8F0',
                drawBorder: false
            }
        }
    }
};

function renderAllCharts() {
    const data = window.dashboardData || {};

    // -------------------------------------------------------------
    // Chart 1: Monthly Incident Velocity (Royal Blue Area)
    // -------------------------------------------------------------
    const lineCtx = document.getElementById("lineChart");
    if (lineCtx && data.monthLabels && data.monthLabels.length > 0) {
        const ctx = lineCtx.getContext("2d");
        
        const lineGradient = ctx.createLinearGradient(0, 0, 0, 300);
        lineGradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
        lineGradient.addColorStop(1, 'rgba(37, 99, 235, 0.01)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.monthLabels,
                datasets: [{
                    label: 'Accidents Recorded',
                    data: data.monthValues,
                    borderColor: '#2563EB',
                    borderWidth: 3,
                    backgroundColor: lineGradient,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#2563EB',
                    pointBorderColor: '#FFFFFF',
                    pointHoverRadius: 6,
                    pointRadius: 4
                }]
            },
            options: chartDefaults
        });
    }

    // -------------------------------------------------------------
    // Chart 2: Vehicle Class Distribution (Doughnut)
    // -------------------------------------------------------------
    const pieCtx = document.getElementById("pieChart");
    if (pieCtx && data.vehicleLabels && data.vehicleLabels.length > 0) {
        const ctx = pieCtx.getContext("2d");

        const doughnutOptions = JSON.parse(JSON.stringify(chartDefaults));
        delete doughnutOptions.scales;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.vehicleLabels,
                datasets: [{
                    data: data.vehicleValues,
                    backgroundColor: [
                        '#2563EB',
                        '#0284C7',
                        '#059669',
                        '#D97706',
                        '#6366F1',
                        '#DC2626',
                        '#DB2777'
                    ],
                    borderColor: '#FFFFFF',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                ...doughnutOptions,
                cutout: '68%'
            }
        });
    }

    // -------------------------------------------------------------
    // Chart 3: High Risk Hotspot Corridors (Crimson Bar)
    // -------------------------------------------------------------
    const barCtx = document.getElementById("barChart");
    if (barCtx && data.roadLabels && data.roadLabels.length > 0) {
        const ctx = barCtx.getContext("2d");

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.roadLabels,
                datasets: [{
                    label: 'Accidents',
                    data: data.roadValues,
                    backgroundColor: '#DC2626',
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: chartDefaults
        });
    }

    // -------------------------------------------------------------
    // Chart 4: Weather & Condition Impact (Amber Bar)
    // -------------------------------------------------------------
    const weatherCtx = document.getElementById("weatherChart");
    if (weatherCtx && data.weatherLabels && data.weatherLabels.length > 0) {
        const ctx = weatherCtx.getContext("2d");

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.weatherLabels,
                datasets: [{
                    label: 'Incidents',
                    data: data.weatherValues,
                    backgroundColor: '#D97706',
                    borderRadius: 6
                }]
            },
            options: chartDefaults
        });
    }
}

// ==========================================================================
// 5. ALERT FEED FILTER TABS & ACKNOWLEDGE ACTIONS
// ==========================================================================
function filterAlerts(severity, btn) {
    const tabs = document.querySelectorAll(".alert-tab");
    tabs.forEach(t => t.classList.remove("active"));
    btn.classList.add("active");

    const items = document.querySelectorAll(".alert-feed-item");
    items.forEach(item => {
        const itemSeverity = item.getAttribute("data-severity");
        if (severity === "all" || itemSeverity === severity) {
            item.style.display = "flex";
        } else {
            item.style.display = "none";
        }
    });
}

function acknowledgeAlert(btn) {
    const alertItem = btn.closest(".alert-feed-item");
    if (!alertItem) return;

    alertItem.style.opacity = "0";
    alertItem.style.transform = "translateX(20px)";
    setTimeout(() => {
        alertItem.remove();
        showToast("Alert acknowledged & archived", "success");
    }, 250);
}

// ==========================================================================
// 6. REFRESH FEED SIMULATION & TOAST NOTIFICATION UTILITY
// ==========================================================================
function refreshDashboardData() {
    const refreshIcon = document.getElementById("refreshIcon");
    if (refreshIcon) {
        refreshIcon.classList.add("fa-spin");
    }

    showToast("Synchronizing real-time telemetry feed...", "info");

    setTimeout(() => {
        if (refreshIcon) {
            refreshIcon.classList.remove("fa-spin");
        }
        showToast("Telemetry synced successfully with Neural Engine ✅", "success");
    }, 800);
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check text-emerald";
    if (type === "warning") icon = "fa-triangle-exclamation text-amber";
    if (type === "error") icon = "fa-circle-exclamation text-rose";

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(20px)";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ==========================================================================
// 7. REAL-TIME LIVE NEURAL STACKING MESSAGE FEED
// ==========================================================================

let feedStreamTimer = null;
let feedInsightIndex = 0;
let feedMessageCount = 0;
let isFeedActive = true;
const MAX_FEED_MESSAGES = 50; // Keep up to 50 before trimming oldest

const feedCategoryMap = {
    CRITICAL:  { label: "CRITICAL",    icon: "fa-triangle-exclamation", color: "#EF4444", bg: "rgba(239,68,68,0.10)" },
    HOTSPOT:   { label: "HOTSPOT",     icon: "fa-fire",                 color: "#F59E0B", bg: "rgba(245,158,11,0.10)" },
    WEATHER:   { label: "WEATHER",     icon: "fa-cloud-bolt",           color: "#38BDF8", bg: "rgba(56,189,248,0.10)" },
    VEHICLE:   { label: "VEHICLE",     icon: "fa-car-side",             color: "#8B5CF6", bg: "rgba(139,92,246,0.10)" },
    SAFETY:    { label: "SAFETY AI",   icon: "fa-shield-halved",        color: "#10B981", bg: "rgba(16,185,129,0.10)" },
    DATASET:   { label: "TELEMETRY",   icon: "fa-chart-line",           color: "#3B82F6", bg: "rgba(59,130,246,0.10)" },
};

function detectFeedCategory(text) {
    const l = text.toLowerCase();
    if (l.includes("fatal") || l.includes("danger") || l.includes("urgent") || l.includes("high-risk"))
        return feedCategoryMap.CRITICAL;
    if (l.includes("road") || l.includes("ring road") || l.includes("hotspot") || l.includes("corridor"))
        return feedCategoryMap.HOTSPOT;
    if (l.includes("weather") || l.includes("rain") || l.includes("fog") || l.includes("clear"))
        return feedCategoryMap.WEATHER;
    if (l.includes("car") || l.includes("vehicle") || l.includes("truck") || l.includes("bike"))
        return feedCategoryMap.VEHICLE;
    if (l.includes("safety") || l.includes("score") || l.includes("index") || l.includes("mitigation"))
        return feedCategoryMap.SAFETY;
    return feedCategoryMap.DATASET;
}

function initDynamicInsightsStream() {
    const feedEl    = document.getElementById("neuralLiveFeed");
    const emptyEl   = document.getElementById("feedEmptyState");
    const countBadge = document.getElementById("feedCountBadge");
    const toggleBtn = document.getElementById("toggleInsightStream");
    const clearBtn  = document.getElementById("clearFeedBtn");

    if (!feedEl) return;

    // Build insight pool
    let insights = (window.dashboardData && window.dashboardData.insights && window.dashboardData.insights.length > 0)
        ? [...window.dashboardData.insights]
        : [
            "Real-time Neural Model actively tracking 150 incident vectors across regional grids.",
            "Faridabad shows peak collision concentration during morning commute windows.",
            "Ring Road identified as primary risk corridor with elevated impact probability.",
            "Weather correlation engine flags 68% of incidents in clear daylight conditions.",
            "Commercial freight & passenger cars account for 84% of urban incidents.",
            "AI predictive safety index calculated at 90/100 across 4 monitored zones.",
            "Automated alert dispatcher queued 5 priority mitigation countermeasures.",
            "Neural anomaly scan detected unusual accident cluster on NH-58 northbound.",
            "Speed-related incidents rose 12% — enforcement camera deployment recommended.",
            "Night-time fatality rate is 2.3× higher — street lighting audit initiated.",
        ];

    if (insights.length < 5 && window.dashboardData && window.dashboardData.kpis) {
        const k = window.dashboardData.kpis;
        insights.push(`Telemetry records ${k.total_accidents || 150} incident points in current cycle.`);
        insights.push(`Safety index at ${k.traffic_score || 90}% — ${k.high_risk_roads || 2} hotspots monitored.`);
    }

    function getLiveTime() {
        const n = new Date();
        return `${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}:${String(n.getSeconds()).padStart(2,'0')}`;
    }

    function prependMessage(text, isFirst = false) {
        const cat = detectFeedCategory(text);
        const confidence = (97.5 + ((feedInsightIndex * 7) % 20) * 0.1).toFixed(1);

        // Remove empty state if still showing
        if (emptyEl && emptyEl.parentNode === feedEl) {
            emptyEl.remove();
        }

        // Remove "NEW" badge from previous top message
        const prevNew = feedEl.querySelector(".feed-new-badge");
        if (prevNew) prevNew.remove();

        // Trim oldest messages if over MAX
        const rows = feedEl.querySelectorAll(".feed-msg-row");
        if (rows.length >= MAX_FEED_MESSAGES) {
            rows[rows.length - 1].remove();
        }

        // Build message row HTML
        const row = document.createElement("div");
        row.className = "feed-msg-row";
        row.innerHTML = `
            <div class="feed-msg-accent" style="background:${cat.color};"></div>
            <div class="feed-msg-icon" style="background:${cat.bg}; color:${cat.color};">
                <i class="fa-solid ${cat.icon}"></i>
            </div>
            <div class="feed-msg-body">
                <div class="feed-msg-text">${text}</div>
                <div class="feed-msg-meta">
                    <span class="feed-msg-tag" style="color:${cat.color}; border-color:${cat.color};">
                        ${cat.label}
                    </span>
                    <span class="feed-msg-time">
                        <i class="fa-regular fa-clock" style="font-size:0.6rem;"></i> ${getLiveTime()} UTC
                    </span>
                    <span class="feed-msg-time" style="margin-left:auto;">
                        <i class="fa-solid fa-brain" style="color:${cat.color};font-size:0.6rem;"></i> ${confidence}%
                    </span>
                </div>
            </div>
            <span class="feed-new-badge">NEW</span>
        `;

        // Prepend so newest is always at top
        feedEl.prepend(row);

        feedMessageCount++;
        if (countBadge) countBadge.textContent = feedMessageCount;
    }

    function startStream() {
        if (feedStreamTimer) clearInterval(feedStreamTimer);
        isFeedActive = true;
        updateStreamButtonUI();

        // Immediately show first message
        prependMessage(insights[feedInsightIndex % insights.length], true);
        feedInsightIndex++;

        feedStreamTimer = setInterval(() => {
            prependMessage(insights[feedInsightIndex % insights.length]);
            feedInsightIndex++;
        }, 1200);
    }

    function pauseStream() {
        if (feedStreamTimer) clearInterval(feedStreamTimer);
        feedStreamTimer = null;
        isFeedActive = false;
        updateStreamButtonUI();
    }

    function updateStreamButtonUI() {
        if (!toggleBtn) return;
        const icon = document.getElementById("streamPauseIcon");
        const text = document.getElementById("streamStatusText");
        if (isFeedActive) {
            if (icon) icon.className = "fa-solid fa-pause";
            if (text) text.textContent = "Live";
            toggleBtn.style.background = "#FFFFFF";
            toggleBtn.style.color = "var(--primary)";
        } else {
            if (icon) icon.className = "fa-solid fa-play";
            if (text) text.textContent = "Paused";
            toggleBtn.style.background = "var(--amber-light)";
            toggleBtn.style.color = "var(--amber)";
        }
    }

    // Toggle button
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            isFeedActive ? pauseStream() : startStream();
        });
    }

    // Clear feed button
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            feedEl.innerHTML = `<div class="feed-empty-state" id="feedEmptyState">
                <i class="fa-solid fa-satellite-dish"></i>
                <span>Feed cleared — resuming neural stream...</span>
            </div>`;
            feedMessageCount = 0;
            if (countBadge) countBadge.textContent = "0";
        });
    }

    // Kick off
    startStream();
}