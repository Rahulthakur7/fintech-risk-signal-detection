import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go




st.set_page_config(
    page_title="Fintech Risk Signal Dashboard",
    page_icon="📊",
    layout="wide"
)

#loading Data

@st.cache_data
def load_data():

    # Price data
    prices = pd.read_csv(
        "data/raw_prices.csv",
        index_col=0,
        parse_dates=True
    )

    prices.index.name = "Date"

    prices = prices.apply(pd.to_numeric, errors="coerce")

    # Anomaly backtest results
    backtest = pd.read_csv(
        "data/anomaly_backtest_results.csv"
    )

    # Convert date column
    if "Date" in backtest.columns:
        backtest["Date"] = pd.to_datetime(backtest["Date"])

    elif "date" in backtest.columns:
        backtest["date"] = pd.to_datetime(backtest["date"])
        backtest.rename(columns={"date": "Date"}, inplace=True)

    # Standardize ticker column
    if "ticker" in backtest.columns:
        backtest.rename(columns={"ticker": "Ticker"}, inplace=True)

    # Standardize future return column
    if "future_5d_return" in backtest.columns:
        backtest.rename(
            columns={"future_5d_return": "Future_5D_Return"},
            inplace=True
        )

    # Anomaly stock summary
    summary = pd.read_csv(
        "data/anomaly_stock_summary.csv"
    )

    # Standardize ticker column
    if "ticker" in summary.columns:
        summary.rename(columns={"ticker": "Ticker"}, inplace=True)

    return prices, backtest, summary


#loading Data

try:

    prices, backtest_df, stock_summary = load_data()

except FileNotFoundError as e:

    st.error(
        "A required CSV file could not be found.\n\n"
        "Make sure these files exist inside your project's data folder:\n\n"
        "• raw_prices.csv\n"
        "• anomaly_backtest_results.csv\n"
        "• anomaly_stock_summary.csv"
    )

    st.stop()


#preparing Data

# Remove completely empty columns
prices = prices.dropna(axis=1, how="all")

# Remove completely empty rows
prices = prices.dropna(axis=0, how="all")

# Calculate daily returns
returns = prices.pct_change()




st.sidebar.title("Dashboard Controls")

tickers = list(prices.columns)

selected_stock = st.sidebar.selectbox(
    "Select Stock",
    tickers
)


# Date range
min_date = prices.index.min().date()
max_date = prices.index.max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# Handle date range selection safely
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

else:

    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date)


# Filter price data
filtered_prices = prices.loc[
    (prices.index >= start_date)
    & (prices.index <= end_date)
]




st.title("📊 Fintech Risk Signal Dashboard")

st.subheader(
    "Market anomaly detection and forward-return analysis"
)

st.caption(
    "Signals are based on historical price behavior "
    "and are not investment advice."
)



#summary

stock_row = stock_summary[
    stock_summary["Ticker"] == selected_stock
]


# Default values
anomaly_events = 0
large_moves = 0
hit_rate = 0.0
avg_return = 0.0
avg_abs_return = 0.0


if not stock_row.empty:

    row = stock_row.iloc[0]

    anomaly_events = int(
        row.get("Anomaly_Events", 0)
    )

    large_moves = int(
        row.get("Large_Moves", 0)
    )

    hit_rate = float(
        row.get("Hit_Rate", 0)
    )

    avg_return = float(
        row.get("Average_5D_Return", 0)
    )

    avg_abs_return = float(
        row.get("Average_Absolute_5D_Return", 0)
    )


#risk overview

st.header(
    f"📌 {selected_stock} Risk Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Anomaly Events",
        anomaly_events
    )

with col2:

    st.metric(
        "Large Moves",
        large_moves
    )

with col3:

    st.metric(
        "Hit Rate",
        f"{hit_rate:.1%}"
    )

with col4:

    st.metric(
        "Avg Absolute 5D Return",
        f"{avg_abs_return:.2%}"
    )


#price history anamoly

st.header(
    f"📈 {selected_stock} Price History"
)


# Get anomaly dates for selected stock
stock_backtest = backtest_df[
    backtest_df["Ticker"] == selected_stock
].copy()


# Restrict anomalies to selected date range
stock_backtest = stock_backtest[
    (stock_backtest["Date"] >= start_date)
    & (stock_backtest["Date"] <= end_date)
]


# Create chart
fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=filtered_prices.index,
        y=filtered_prices[selected_stock],
        mode="lines",
        name=selected_stock
    )
)


# Add anomaly markers
if not stock_backtest.empty:

    anomaly_dates = stock_backtest["Date"]

    # Match dates to price index
    valid_anomaly_dates = [
        d for d in anomaly_dates
        if d in filtered_prices.index
    ]

    if valid_anomaly_dates:

        anomaly_prices = filtered_prices.loc[
            valid_anomaly_dates,
            selected_stock
        ]

        fig.add_trace(
            go.Scatter(
                x=valid_anomaly_dates,
                y=anomaly_prices.values,
                mode="markers",
                name="Anomaly",
                marker=dict(
                    size=10,
                    symbol="x"
                )
            )
        )


fig.update_layout(
    height=500,
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    width="stretch"
)




st.header("🚨 Anomaly Summary")

summary_display = stock_summary.copy()

# Format percentages for display
if "Hit_Rate" in summary_display.columns:

    summary_display["Hit_Rate"] = (
        summary_display["Hit_Rate"] * 100
    ).round(2)


if "Average_5D_Return" in summary_display.columns:

    summary_display["Average_5D_Return"] = (
        summary_display["Average_5D_Return"] * 100
    ).round(2)


if "Average_Absolute_5D_Return" in summary_display.columns:

    summary_display["Average_Absolute_5D_Return"] = (
        summary_display["Average_Absolute_5D_Return"] * 100
    ).round(2)


st.dataframe(
    summary_display,
    use_container_width=True,
    hide_index=False
)


# 5 day forward return analysis


st.header("📊 5-Day Forward Return Analysis")


stock_returns = stock_backtest["Future_5D_Return"].dropna()


col1, col2 = st.columns(2)


with col1:

    if not stock_returns.empty:

        st.metric(
            "Average 5-Day Return",
            f"{stock_returns.mean():.2%}"
        )

    else:

        st.metric(
            "Average 5-Day Return",
            "N/A"
        )


with col2:

    if not stock_returns.empty:

        st.metric(
            "Average Absolute 5-Day Return",
            f"{stock_returns.abs().mean():.2%}"
        )

    else:

        st.metric(
            "Average Absolute 5-Day Return",
            "N/A"
        )


# Histogram
if not stock_returns.empty:

    hist_fig = go.Figure()

    hist_fig.add_trace(
        go.Histogram(
            x=stock_returns,
            nbinsx=20,
            name="5-Day Returns"
        )
    )

    # Zero line
    hist_fig.add_vline(
        x=0,
        line_dash="dash",
        annotation_text="0%"
    )

    # +5% threshold
    hist_fig.add_vline(
        x=0.05,
        line_dash="dash",
        annotation_text="+5%"
    )

    # -5% threshold
    hist_fig.add_vline(
        x=-0.05,
        line_dash="dash",
        annotation_text="-5%"
    )

    hist_fig.update_layout(
        height=450,
        xaxis_title="5-Day Return",
        yaxis_title="Number of Events",
        bargap=0.05
    )

    st.plotly_chart(
        hist_fig,
        width="stretch"
    )

else:

    st.info(
        "No backtest observations are available "
        "for this stock in the selected date range."
    )


#stock risk signal ranking

st.header("🏆 Stock Risk Signal Ranking")


ranking = stock_summary.copy()

if "Hit_Rate" in ranking.columns:

    ranking["Hit_Rate"] = (
        ranking["Hit_Rate"] * 100
    ).round(2)


if "Average_5D_Return" in ranking.columns:

    ranking["Average_5D_Return"] = (
        ranking["Average_5D_Return"] * 100
    ).round(2)


if "Average_Absolute_5D_Return" in ranking.columns:

    ranking["Average_Absolute_5D_Return"] = (
        ranking["Average_Absolute_5D_Return"] * 100
    ).round(2)


# Sort by hit rate
if "Hit_Rate" in ranking.columns:

    ranking = ranking.sort_values(
        "Hit_Rate",
        ascending=False
    )


st.dataframe(
    ranking,
    width="stretch",
    hide_index=False
)


#large moves following anomalies

st.header("⚠️ Large Moves Following Anomalies")


if "Large_Move" in stock_backtest.columns:

    large_move_df = stock_backtest[
        stock_backtest["Large_Move"] == True
    ].copy()

else:

    # Calculate it if the CSV does not contain the column
    stock_backtest["Large_Move"] = (
        stock_backtest["Future_5D_Return"].abs() >= 0.05
    )

    large_move_df = stock_backtest[
        stock_backtest["Large_Move"] == True
    ].copy()


if not large_move_df.empty:

    display_large_moves = large_move_df[
        [
            "Ticker",
            "Date",
            "Future_5D_Return",
            "Large_Move"
        ]
    ].copy()

    display_large_moves["Future_5D_Return"] = (
        display_large_moves["Future_5D_Return"] * 100
    ).round(2)


    st.dataframe(
        display_large_moves,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No large moves following anomalies were found "
        "for this stock in the selected date range."
    )


#corelation breakdown with JPM

st.header("📉 Correlation Breakdown with JPM")


if "JPM" in returns.columns and selected_stock != "JPM":

    # Calculate 60-day rolling correlation with JPM
    stock_corr = (
        returns[selected_stock]
        .rolling(window=60)
        .corr(returns["JPM"])
    )

    corr_df = pd.DataFrame(
        {
            "Date": stock_corr.index,
            "Rolling_Correlation": stock_corr.values
        }
    ).dropna()


    # Restrict to selected date range
    corr_df = corr_df[
        (corr_df["Date"] >= start_date)
        & (corr_df["Date"] <= end_date)
    ]


    if not corr_df.empty:

        latest_corr = corr_df[
            "Rolling_Correlation"
        ].iloc[-1]


        st.metric(
            "Current 60-Day Correlation with JPM",
            f"{latest_corr:.2f}"
        )


        
        # Correlation chart
        

        corr_fig = go.Figure()


        corr_fig.add_trace(
            go.Scatter(
                x=corr_df["Date"],
                y=corr_df["Rolling_Correlation"],
                mode="lines",
                name="60-Day Correlation"
            )
        )


        # Zero correlation line
        corr_fig.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="0"
        )


        corr_fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Correlation",
            yaxis=dict(
                range=[-1, 1]
            ),
            hovermode="x unified"
        )


        st.plotly_chart(
            corr_fig,
            width="stretch"
        )


        
        
#correlation breakdown detection

        correlation_drop = (
            corr_df["Rolling_Correlation"].shift(60)
            - corr_df["Rolling_Correlation"]
        )


        corr_df["Correlation_Breakdown"] = (
            correlation_drop > 0.40
        )


        breakdown_df = corr_df[
            corr_df["Correlation_Breakdown"]
        ].copy()


        st.write(
            "Correlation breakdown observations:",
            f"**{len(breakdown_df)}**"
        )


        # Show latest breakdown events
        if not breakdown_df.empty:

            st.subheader(
                "🚨 Recent Correlation Breakdown Signals"
            )


            recent_breakdowns = breakdown_df[
                [
                    "Date",
                    "Rolling_Correlation"
                ]
            ].tail(10).copy()


            recent_breakdowns[
                "Rolling_Correlation"
            ] = recent_breakdowns[
                "Rolling_Correlation"
            ].round(3)


            st.dataframe(
                recent_breakdowns,
                width="stretch",
                hide_index=True
            )

        else:

            st.success(
                "No correlation breakdown signals "
                "were detected in the selected period."
            )


    else:

        st.info(
            "Not enough data to calculate the 60-day "
            "rolling correlation."
        )


else:

    st.info(
        "JPM is the reference stock, so correlation "
        "with itself is not displayed."
    )



#footer

st.divider()

st.caption(
    "Fintech Market Anomaly & Risk Signal Detection System | "
    "Historical analysis only | Not investment advice"
)