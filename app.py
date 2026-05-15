import streamlit as st
import requests
import json

API = "http://localhost:8001"

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinAnalyst AI",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #F8F9FA; }
.metric-card {
    background: #fff;
    border: 1px solid #E9ECEF;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.metric-value { font-size: 24px; font-weight: 600; color: #1a1a2e; }
.metric-label { font-size: 13px; color: #6c757d; margin-bottom: 4px; }
.metric-delta-up   { font-size: 13px; color: #2d6a4f; }
.metric-delta-down { font-size: 13px; color: #c0392b; }
.variance-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px;
}
.badge-over  { background:#FCEBEB; color:#A32D2D; padding:2px 8px; border-radius:12px; font-size:12px; }
.badge-under { background:#EAF3DE; color:#3B6D11; padding:2px 8px; border-radius:12px; font-size:12px; }
.badge-on    { background:#E6F1FB; color:#185FA5; padding:2px 8px; border-radius:12px; font-size:12px; }
.exec-block {
    background: #fff; border-left: 4px solid #185FA5;
    padding: 14px 18px; border-radius: 0 8px 8px 0;
    margin-bottom: 12px; font-size: 14px; line-height: 1.7; color: #333;
}
.risk-item   { background:#FCEBEB; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:13px; color:#501313; }
.action-item { background:#EAF3DE; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:13px; color:#173404; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 FinAnalyst AI")
    st.caption("Powered by Claude + RAG")
    st.divider()

    uploaded = st.file_uploader(
        "Upload financial report",
        type=["pdf", "xlsx", "xls", "csv", "txt"],
        help="Upload your P&L, variance report, or transaction summary"
    )

    if uploaded:
        with st.spinner("Ingesting document…"):
            res = requests.post(
                f"{API}/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
            )
            if res.status_code == 200:
                st.success(f"✓ {uploaded.name} loaded ({res.json()['chunks']} chunks)")
            else:
                st.error("Upload failed — is the backend running?")

    st.divider()
    period = st.selectbox("Reporting period", [
        "April 2025 (MTD)", "Q1 2025", "FY 2024", "March 2025"
    ])

    st.divider()
    st.caption("Quick prompts")
    if st.button("📈 Revenue vs budget"):
        st.session_state.query = "Summarize revenue performance vs budget"
    if st.button("⚠️ OPEX variance"):
        st.session_state.query = "Explain the OPEX variance this month"
    if st.button("📝 Board commentary"):
        st.session_state.query = "Write executive commentary for the board pack"

# ── Main area ─────────────────────────────────────────────────
st.title("Financial Analysis Assistant")

query = st.text_input(
    "Ask about this report",
    value=st.session_state.get("query", ""),
    placeholder="e.g. What drove the gross margin decline?",
    key="query"
)

col_btn, col_clear = st.columns([1, 5])
with col_btn:
    analyze = st.button("✦ Analyze", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear results"):
        st.session_state.pop("result", None)
        st.rerun()

# ── Run analysis ──────────────────────────────────────────────
if analyze and query:
    with st.spinner("Analyzing with Claude…"):
        try:
            res = requests.post(f"{API}/analyze", json={
                "query": query, "period": period
            })
            data = res.json()
            raw = data.get("result", "{}")
            clean = raw.replace("```json", "").replace("```", "").strip()
            st.session_state.result = json.loads(clean)
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ── Display results ───────────────────────────────────────────
if "result" in st.session_state:
    r = st.session_state.result
    tab1, tab2, tab3 = st.tabs(["📋 Summary", "📊 Variance analysis", "✍️ Executive commentary"])

    # ── Tab 1: Summary ────────────────────────────────────────
    with tab1:
        s = r.get("summary", {})

        if s.get("headline"):
            st.info(f"**{s.get('period', period)}** — {s['headline']}")

        metrics = s.get("metrics", [])
        if metrics:
            cols = st.columns(len(metrics))
            for col, m in zip(cols, metrics):
                icon = "↑" if m.get("trend") == "up" else "↓" if m.get("trend") == "down" else "→"
                delta_class = "metric-delta-up" if m.get("trend") == "up" else "metric-delta-down"
                col.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{m.get('label','')}</div>
                    <div class="metric-value">{m.get('value','')}</div>
                    <div class="{delta_class}">{icon} {m.get('delta','')}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### Key findings")
        for bullet in s.get("bullets", []):
            st.markdown(f"- {bullet}")

    # ── Tab 2: Variance ───────────────────────────────────────
    with tab2:
        v = r.get("variance", {})

        if v.get("explanation"):
            st.markdown(v["explanation"])

        items = v.get("items", [])
        if items:
            st.markdown("#### Line-by-line breakdown")

            header = st.columns([3, 2, 2, 2, 2])
            for col, label in zip(header, ["Line item", "Budget", "Actual", "Variance", "Status"]):
                col.markdown(f"**{label}**")
            st.divider()

            for item in items:
                direction = item.get("direction", "on-track")
                badge_class = "badge-over" if direction == "over" else \
                              "badge-under" if direction == "under" else "badge-on"
                badge_label = direction.replace("-", " ").title()

                cols = st.columns([3, 2, 2, 2, 2])
                cols[0].markdown(item.get("name", ""))
                cols[1].markdown(item.get("budget", ""))
                cols[2].markdown(f"**{item.get('actual', '')}**")
                delta_color = "red" if direction == "over" else "green" if direction == "under" else "blue"
                cols[3].markdown(f":{delta_color}[{item.get('delta', '')}]")
                cols[4].markdown(
                    f'<span class="{badge_class}">{badge_label}</span>',
                    unsafe_allow_html=True
                )

                if item.get("reason"):
                    with st.expander(f"↳ Root cause: {item['name']}", expanded=False):
                        st.caption(item["reason"])

                pct = min(abs(item.get("deltaPct", 0)), 100) / 100
                st.progress(pct)

    # ── Tab 3: Executive commentary ───────────────────────────
    with tab3:
        e = r.get("exec", {})

        st.markdown("### Board commentary")
        for para in e.get("paragraphs", []):
            st.markdown(f'<div class="exec-block">{para}</div>', unsafe_allow_html=True)

        col_r, col_a = st.columns(2)

        with col_r:
            st.markdown("#### ⚠️ Key risks")
            for risk in e.get("risks", []):
                st.markdown(f'<div class="risk-item">• {risk}</div>', unsafe_allow_html=True)

        with col_a:
            st.markdown("#### ✅ Recommended actions")
            for i, action in enumerate(e.get("actions", []), 1):
                st.markdown(f'<div class="action-item">{i}. {action}</div>', unsafe_allow_html=True)

        st.divider()
        commentary_text = "\n\n".join(e.get("paragraphs", []))
        st.download_button(
            "⬇️ Download commentary (.txt)",
            data=commentary_text,
            file_name=f"exec_commentary_{period.replace(' ','_')}.txt",
            mime="text/plain"
        )

else:
    st.markdown("---")
    st.markdown("#### Getting started")
    cols = st.columns(3)
    cols[0].info("**Step 1**\nUpload your PDF, Excel, or CSV report using the sidebar")
    cols[1].info("**Step 2**\nType a question or pick a quick prompt")
    cols[2].info("**Step 3**\nClick Analyze to get AI-powered insights")
