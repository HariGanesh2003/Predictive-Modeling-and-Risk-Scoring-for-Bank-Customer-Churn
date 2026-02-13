import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. PAGE CONFIGURATION & PROFESSIONAL LIGHT THEME CSS
# ==============================================================================
st.set_page_config(page_title="Bank Customer Churn Analysis", layout="wide")

st.markdown("""
    <style>
    /* 1. Main Background - Pure White */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }

    /* 2. Professional Card Styling - Light with Soft Shadow */
    .chart-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 25px;
        border: 1px solid #f0f0f0;
    }

    /* 3. KPI Card Styling - Rounded & Defined */
    .kpi-card {
        background-color: #f8fafc;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    .kpi-value {
        font-size: 34px;
        font-weight: 900;
        color: #0f172a;
    }
    .kpi-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }

    /* 4. Global Text and Header Colors - Pure Black */
    h1, h2, h3, .stMarkdown, p, span, label {
        color: #000000 !important;
    }

    /* 5. Interpretation Box - Soft Blue Professional */
    .insight-box {
        background-color: #f1f5ff;
        border-left: 5px solid #2563eb;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        font-size: 14px;
        color: #1e3a8a;
        margin-top: 15px;
        line-height: 1.6;
    }

    /* 6. Strategic Conclusion Block - Professional Light Gray/Blue */
    .findings-block {
        background-color: #f8fafc;
        color: #0f172a;
        padding: 35px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        margin-top: 30px;
    }
    .finding-line {
        margin-bottom: 12px;
        font-size: 16px;
        display: flex;
        align-items: center;
        color: #0f172a;
    }
    
    /* Sidebar Styling - Light Gray */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Ensure Sidebar text is black */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOADING
# ==============================================================================
@st.cache_data
def load_bank_data():
    # Path updated to standard local filename
    df = pd.read_csv(r"d:\MyFiles\Downloads\European_Bank - European_Bank.csv")
    return df

df = load_bank_data()

# ==============================================================================
# 3. INTERACTIVE SLICERS (SIDEBAR)
# ==============================================================================
st.sidebar.title("🔍 Filter Panel")
st.sidebar.markdown("Adjust parameters to update dashboard:")

geo_list = df["Geography"].unique()
selected_geo = st.sidebar.multiselect("Geography", geo_list, default=geo_list)

gender_list = df["Gender"].unique()
selected_gender = st.sidebar.multiselect("Gender", gender_list, default=gender_list)

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Customer Age Range", age_min, age_max, (age_min, age_max))

mask = (df["Geography"].isin(selected_geo)) & \
       (df["Gender"].isin(selected_gender)) & \
       (df["Age"].between(age_range[0], age_range[1]))
f_df = df[mask]

# ==============================================================================
# 4. DASHBOARD HEADER & KPI SECTION
# ==============================================================================
st.title("🏦 European Bank | Retention Analytics")
# st.markdown("#### High-Resolution Operational Dashboard")

k1, k2, k3, k4 = st.columns(4)

total_n = len(f_df)
churned_n = f_df["Exited"].sum()
c_rate = (churned_n / total_n * 100) if total_n > 0 else 0
avg_bal = f_df["Balance"].mean() if total_n > 0 else 0

with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Customers</div><div class="kpi-value">{total_n:,}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Exited (Count)</div><div class="kpi-value" style="color:#dc2626;">{churned_n:,}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Churn Rate</div><div class="kpi-value">{c_rate:.1f}%</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Balance</div><div class="kpi-value">${avg_bal/1000:.1f}k</div></div>', unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 5. DYNAMIC CHARTS SECTION
# ==============================================================================

# FIXED: Custom layout update for all charts to correctly set black font
def update_axis_colors(fig):
    fig.update_layout(
        font=dict(color="black"),
        xaxis=dict(
            tickfont=dict(color="black"), 
            title=dict(font=dict(color="black")) # Corrected syntax
        ),
        yaxis=dict(
            tickfont=dict(color="black"), 
            title=dict(font=dict(color="black")) # Corrected syntax
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

c_bar1, c_bar2 = st.columns(2)

with c_bar1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("🛑 Exited vs Retained Status")
    exit_counts = f_df["Exited"].value_counts().reset_index()
    exit_counts.columns = ["Status", "Count"]
    exit_counts["Status Label"] = exit_counts["Status"].map({0: "Retained", 1: "Exited"})
    
    fig1 = px.bar(exit_counts, x="Status Label", y="Count", 
                  color="Status Label", text_auto=True,
                  color_discrete_map={"Retained": "#10b926", "Exited": "#ef4444"},
                  template="plotly_white")
    update_axis_colors(fig1)
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>Interpretation:</b> Compares active customer volume against those who have left. High 'Exited' volume 
    relative to history signals a need for segment-based outreach.
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_bar2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("📦 Churn Rate by Product Count")
    prod_churn = f_df.groupby("NumOfProducts")["Exited"].mean().reset_index()
    prod_churn["Churn %"] = prod_churn["Exited"] * 100
    
    fig2 = px.bar(prod_churn, x="NumOfProducts", y="Churn %",
                  color="Churn %", color_continuous_scale="Reds",
                  template="plotly_white")
    update_axis_colors(fig2)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>Interpretation:</b> Customers with 3 or 4 products are highly unstable. This implies that 
    increasing product density beyond 2 requires a different customer management approach.
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

c_geo, c_gender = st.columns(2)

with c_geo:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("🌍 Regional Churn Impact")
    geo_df = f_df.groupby("Geography")["Exited"].mean().reset_index()
    geo_df["Churn %"] = geo_df["Exited"] * 100
    
    fig3 = px.bar(geo_df, x="Geography", y="Churn %", text_auto=".1f",
                  color="Geography", color_discrete_sequence=px.colors.qualitative.Pastel,
                  template="plotly_white")
    update_axis_colors(fig3)
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>Interpretation:</b> Germany consistently shows elevated churn levels. Retention teams should 
    audit regional pricing and competitor offerings in the German market.
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_gender:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("🚻 Gender Distribution")
    gen_df = f_df["Gender"].value_counts().reset_index()
    gen_df.columns = ["Gender", "Total"]
    
    fig4 = px.pie(gen_df, names="Gender", values="Total", hole=0.6,
                  color_discrete_sequence=["#1c65db", "#e53791"],
                  template="plotly_white")
    fig4.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig4.update_layout(font=dict(color="black"), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>Interpretation:</b> This distribution helps confirm if our current retention strategies are 
    appropriately balanced across our demographic split.
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. STRATEGIC CONCLUSION BLOCK
# ==============================================================================
st.write("---")
st.markdown('<div class="findings-block">', unsafe_allow_html=True)
st.markdown("## Main reasons customers leave:")

reasons = [
    "Low engagement",
    "Inactive members churn more",
    "Fewer bank products",
    "Weak relationship with the bank",
    "Short tenure",
    "New customers are more vulnerable",
    "Age + tenure imbalance",
    "Older customers with weak engagement leave faster"
]

for r in reasons:
    st.markdown(f'<div class="finding-line">✅ &nbsp; {r}</div>', unsafe_allow_html=True)

st.markdown("<br>---<br>", unsafe_allow_html=True)
st.markdown("### 🏁 Final Conclusion")
st.write("""
Based on the dashboard analytics, the primary drivers of churn are **Geography (Germany)** and **Customer Inactivity**. 
High-value customers with multiple products are surprisingly the most vulnerable, suggesting that 
account complexity is not translating into loyalty. 

- Improve customer engagement through personalized offers, rewards, and regular communication.
- Identify inactive customers early using churn prediction and trigger retention campaigns.
- Increase product adoption through cross-selling (credit cards, loans, insurance bundles).
- Strengthen onboarding experience for new customers during the first 3–6 months.
- Implement segment-based strategies for older customers with low engagement.
- Monitor churn rate through a real-time dashboard and take proactive action.
""")
st.markdown('</div>', unsafe_allow_html=True)

