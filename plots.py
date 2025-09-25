import plotly.express as px
import streamlit as st

def plot_whether(df):
    df["anomaly"] = df["anomaly"].astype(str)
    fig = px.scatter(
        df, x='timestamp', y='temperature', color='anomaly',
        color_discrete_sequence=['#FFC7D5', '#C32349']
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            rangeslider_visible=True,
        ),
    )

    st.plotly_chart(fig)
