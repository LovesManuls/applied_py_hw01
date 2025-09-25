import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression

from plots import *

def get_data_subset(df, city):
    df = df[df.city == city]
    return df

def heavy_analysis_func(df: pd.DataFrame, city_option: str, window_size=30):

    df = df[df.city == city_option]
    main_stats = df['temperature'].agg(['mean', 'max', 'min'])

    df[['mean_30ws', 'std_30ws']] = df['temperature'].rolling(
        window=window_size, center=True,
        closed='neither', min_periods=1,
    ).agg(['mean', 'std'])

    cond01 = df.temperature > df.mean_30ws + 2 * df.std_30ws
    cond02 = df.temperature < df.mean_30ws - 2 * df.std_30ws
    # anomalies = df[cond01 | cond02].index
    df["anomaly"] = np.where(cond01 | cond02, 1, 0)

    season_profile = df.groupby('season').agg(
        temp_mean=('temperature', 'mean'),
        temp_std=('temperature', 'std'),
    )

    temp = df['temperature']
    trend = int(LinearRegression().fit(np.arange(len(temp)).reshape(-1, 1), temp).coef_[0] >= 0)
    trend = "Up" if trend == 1 else "Down"

    return df, main_stats, season_profile, trend  # , anomalies

def perform_analysis(df: pd.DataFrame, city_option: str, curr_city_temp):
    st.markdown(f"## Weather Analysis on :red-background[{city_option}]")

    df, stats, s_profile, trend = heavy_analysis_func(df, city_option)

    # текущая погода из запроса аномалия ли
    aa, bb = st.columns(2)
    mean_a = s_profile["temp_mean"]["autumn"]
    std_a = s_profile["temp_std"]["autumn"]
    curr_anomaly = "Норма"
    if curr_city_temp >= mean_a + 3 * std_a:
        if curr_city_temp <= mean_a - 3 * std_a:
            curr_anomaly = "Аномалия"
    aa.metric("Temp now", f"{curr_city_temp} °C", border=True)
    bb.metric("Anomality", f"{curr_anomaly}", border=True)

    st.markdown(" ")
    st.markdown("**Main statistics:**")
    a, b, c, d = st.columns(4)
    a.metric("Trend in years", trend, border=True)
    b.metric("Mean in a year", f"{stats["mean"].round(1)} °C", border=True)
    c.metric("Min in a year", f"{stats["min"].round(1)} °C", border=True)
    d.metric("Max in a year",f"{stats["max"].round(1)} °C", border=True)

    st.markdown(" ")
    st.markdown("**Temperatures across the years:**")
    plot_whether(df)

    st.markdown("")