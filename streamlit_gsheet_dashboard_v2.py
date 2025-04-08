
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="📊 AY2025 Live Dashboard", layout="wide")
st.title("📈 Tuition Centre Enrollment Dashboard – AY2025 (Google Sheets Live)")

# Google Sheet URL with encoded sheet name
sheet_url = 'https://docs.google.com/spreadsheets/d/1JlYsQdyKyvUgq3Cv-KwZxW3O-Lktzy4p30L7WFk5W1M/gviz/tq?tqx=out:csv&sheet=ay2025%20daily%20tracking'

# Try loading the data
try:
    df_raw = pd.read_csv(sheet_url)

    # Clean and parse structure
    df_raw.columns = df_raw.columns.str.strip()
    date_col = df_raw.columns[0]
    df = df_raw.copy()
    df = df[df[date_col].notna() & ~df[date_col].str.contains("Date", case=False, na=False)]
    df = df.rename(columns={date_col: "Date"})
    df = df[['Date'] + [col for col in df.columns if any(x in col.upper() for x in ["PR1", "PR2", "TP", "WD", "CCK", "JW", "OL"])]]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    # Totals
    last_row = df.iloc[-1]
    ay2025_total = last_row[1:]
    ay2024_total = pd.Series({
        'PR1': 361, 'PR2': 157, 'TP': 406, 'WD': 97,
        'CCK': 196, 'JW': 297, 'OL': 498, 'SN': 82
    })
    ay2025_with_sn = pd.concat([ay2025_total, pd.Series({'SN': None})])
    compare_df = pd.DataFrame({'AY2024': ay2024_total, 'AY2025': ay2025_with_sn}).reset_index().rename(columns={'index': 'Centre'})
    compare_df['Percent Change'] = ((compare_df['AY2025'] - compare_df['AY2024']) / compare_df['AY2024'] * 100).round(2)

    # Growth rates
    growth = df.copy()
    for col in growth.columns[1:]:
        growth[col] = growth[col].pct_change() * 100

    st.success("✅ Live data loaded successfully from Google Sheets!")

    # Visuals
    st.subheader("📈 Weekly Enrollment Trends")
    st.plotly_chart(px.line(df, x='Date', y=df.columns[1:], markers=True), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Total Enrollments AY2024 vs AY2025")
        st.plotly_chart(px.bar(compare_df, x='Centre', y=['AY2024', 'AY2025'], barmode='group'), use_container_width=True)
    with col2:
        st.subheader("📉 % Change in Enrollments")
        st.plotly_chart(px.bar(compare_df.dropna(), x='Centre', y='Percent Change'), use_container_width=True)

    st.subheader("📈 Weekly Growth Rate Trends by Centre")
    st.plotly_chart(px.line(growth, x='Date', y=growth.columns[1:]), use_container_width=True)

except Exception as e:
    st.error(f"Failed to load or parse Google Sheet: {e}")
