import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")
st.title("AIRBNB DATA ANALYSIS")
st.write("")

# ---------------- LOAD DATA ----------------
@st.cache_data
def datafr():
    return pd.read_csv("cleaned_airbnb_listings.csv")

df = datafr()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Data Exploration", "About"])

# ---------------- HOME ----------------
if select == "Home":

    try:
        image1 = Image.open("Airbnb-Logo.webp")
        st.image(image1)
    except:
        st.warning("Image not found")

    st.header("About Airbnb")
    st.write("")

    st.write('''Airbnb is an online marketplace that connects people who want to rent out
    their property with people who are looking for accommodations, typically for short stays.
    Airbnb offers hosts a relatively easy way to earn income from their property.
    Guests often find Airbnb rentals cheaper and more homely than hotels.''')

    st.write("")

    st.write('''Airbnb Inc operates an online platform for hospitality services.
    The company provides an app that enables users to list and book accommodations worldwide.
    Airbnb includes vacation rentals, apartments, homestays, castles, and hotel rooms.
    It operates in multiple countries including India, USA, UK, and more.
    Headquarters: San Francisco, USA.''')

    st.header("Background of Airbnb")
    st.write("")

    st.write('''Airbnb started in 2007 when two hosts welcomed three guests.
    Today, it has over 4 million hosts and 1.5 billion guest arrivals globally.''')

# ---------------- DATA EXPLORATION ----------------
if select == "Data Exploration":

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Price Insights",
        "📅 Availability",
        "📍 Location Intelligence",
        "🌍 Geo View",
        "🏆 Premium Listings"
    ])

    # ---------------- TAB 1 ----------------
    with tab1:
        st.subheader("💰 Price Drivers")

        # Business Question
        st.caption("Which property types command higher prices in each country and room segment?")

        country = st.selectbox("Country", df["country"].unique(), key="tab1_country")
        df1 = df[df["country"] == country]

        room_type = st.selectbox("Room Type", df1["room_type"].unique())
        df2 = df1[df1["room_type"] == room_type]

        price_df = df2.groupby("property_type")["price"].mean().reset_index()

        fig = px.bar(
            price_df,
            x="property_type",
            y="price",
            color="price",
            title="Avg Price by Property Type"
        )

        st.plotly_chart(fig, width='stretch')

    # ---------------- TAB 2 ----------------
    with tab2:
        st.subheader("📅 Availability Trends")

        # Business Question
        st.caption("How is listing availability distributed across room and bed types?")

        country = st.selectbox("Country", df["country"].unique(), key="tab2_country")
        df1 = df[df["country"] == country]

        property_type = st.selectbox("Property Type", df1["property_type"].unique())
        df2 = df1[df1["property_type"] == property_type]

        # ✅ Donut Chart (Replaced Sunburst)
        donut_df = df2.groupby("room_type")["availability_365"].sum().reset_index()

        fig = px.pie(
            donut_df,
            names="room_type",
            values="availability_365",
            hole=0.5,
            title="Availability Share by Room Type"
        )

        st.plotly_chart(fig, width='stretch')

        # Bar Chart
        df_bar = df2.groupby("room_type")["availability_365"].mean().reset_index()

        fig2 = px.bar(
            df_bar,
            x="room_type",
            y="availability_365",
            color="availability_365",
            title="Avg Availability"
        )

        st.plotly_chart(fig2, width='stretch')

    # ---------------- TAB 3 ----------------
    with tab3:
        st.subheader("📍 Pricing Intelligence")

        st.caption("Explore listings within the selected price range and compare key features")
        # ---------------- FILTER ----------------
        
        country = st.selectbox("Country", df["country"].unique(), key="tab3_country")
        df1 = df[df["country"] == country]

        price_min = int(df1["price"].min())
        price_max = int(df1["price"].max())

        price_range = st.slider("Price Range", price_min, price_max, (price_min, price_max))

        df_filtered = df1[
            (df1["price"] >= price_range[0]) &
            (df1["price"] <= price_range[1])
        ].copy()
        
        
        # ---------------- KPI ----------------
        st.metric("Total Listings", len(df_filtered))

        # ---------------- CAPACITY GROUP ----------------
        df_filtered["capacity_group"] = pd.cut(
            df_filtered["accommodates"],
            bins=[0, 2, 4, 6, 10, 20],
            labels=["1-2", "3-4", "5-6", "7-10", "10+"]
        )

        # ---------------- PRICE BAR CHART ----------------
        st.subheader("📊 Average Price by Capacity")

        bar_df = df_filtered.groupby("capacity_group")["price"].mean().reset_index()

        fig1 = px.bar(
            bar_df,
            x="capacity_group",
            y="price",
            color="price",
            title="Average Price by Capacity Group"
        )

        st.plotly_chart(fig1, width='stretch')

        # ---------------- VALUE ANALYSIS ----------------
        df_filtered = df_filtered[df_filtered["accommodates"] > 0]

        df_filtered["price_per_person"] = df_filtered["price"] / df_filtered["accommodates"]

        st.subheader("📊 Value Analysis (Price per Person)")

        value_df = df_filtered.groupby("capacity_group")["price_per_person"].mean().reset_index()

        fig2 = px.bar(
            value_df,
            x="capacity_group",
            y="price_per_person",
            color="price_per_person",
            title="Average Price per Person"
        )

        st.plotly_chart(fig2, width='stretch')

        # ---------------- BEST DEAL LISTINGS ----------------
        st.subheader("🏆 Best Value Listings")

        top_deals = df_filtered.sort_values(by="price_per_person").head(10)

        st.metric("Best Deal Price/Person", round(top_deals["price_per_person"].min(), 2))

        st.dataframe(
            top_deals[[
                "name",
                "price",
                "accommodates",
                "price_per_person",
                "bedrooms",
                "beds",
                "bathrooms"
            ]],
            width='stretch'
        )

        # ---------------- BEST DEAL CHART ----------------
        fig3 = px.bar(
            top_deals,
            x="name",
            y="price_per_person",
            color="price_per_person",
            title="Top 10 Best Value Listings (Lower is Better)"
        )

        st.plotly_chart(fig3, width='stretch')

        # ---------------- FULL TABLE ----------------
        st.subheader("📋 Listing Details")

        st.dataframe(df_filtered.head(50), width='stretch')

        # ---------------- CORRELATION ----------------
        st.subheader("🔗 Correlation Insights")

        corr = df_filtered.select_dtypes(include="number").corr()

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="Feature Correlation Heatmap"
        )

        st.plotly_chart(fig_corr, width='stretch')


        # ---------------- TAB 4 ----------------
        with tab4:
            st.subheader("🌍 Geo Distribution")

            # Business Question
            st.caption("Where are high-value listings concentrated geographically?")

            fig = px.scatter_map(
                df,
                lat="latitude",
                lon="longitude",
                color="price",
                size="accommodates",
                hover_name="name",
                zoom=1
            )

            st.plotly_chart(fig, width='stretch')

        # ---------------- TAB 5 ----------------
        with tab5:
            st.subheader("🏆 Premium Listings")

            # Business Question
            st.caption("Which listings generate the highest price and what are their characteristics?")

            country = st.selectbox("Country", df["country"].unique(), key="tab5_country")
            df1 = df[df["country"] == country]

            df_sorted = df1.sort_values(by="price", ascending=False).head(20)

            fig = px.bar(
                df_sorted,
                x="name",
                y="price",
                color="price",
                title="Top 20 Expensive Listings",
                hover_data=["accommodates", "bedrooms", "beds"]
            )

            st.plotly_chart(fig, width='stretch')

# ---------------- ABOUT ----------------
elif select == "About":
    st.header("Project Information")

    st.write("""
    This project analyzes Airbnb data using:
    - Python (Pandas)
    - Streamlit
    - Data Visualization
    
    Key Areas:
    - Price Analysis
    - Availability Trends
    - Location Insights
    """)