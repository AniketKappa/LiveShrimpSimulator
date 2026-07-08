import streamlit as st
import pandas as pd
import plotly.express as px


# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Live Shrimp Cost Simulator",
    page_icon="🦐",
    layout="wide"
)

st.title("🦐 Live Shrimp Cost Simulator")
st.markdown("---")


# ----------------------------
# MODEL
# ----------------------------

def cost_per_kg(
    fa_overhead,
    loading_labour,
    rm_charges,
    transportation_charges,
    ice_charges,
    smbs_charges,
    harvest_quantity,
    rejection,
    processing_charges,
    outward_charges
):

    cost_at_factory = (
        (fa_overhead + loading_labour + rm_charges)
        + (
            transportation_charges
            + ice_charges
            + smbs_charges
        ) / harvest_quantity
    )

    cost_of_factory = (
        cost_at_factory
        + processing_charges
    )

    total_cost = (
        cost_of_factory
        + outward_charges
    )

    rejection_cost = (
        cost_at_factory
        - (8 + rm_charges)
    ) * (
        rejection
        /
        (100 - rejection)
    ) if rejection < 100 else 0

    final_cost = total_cost + rejection_cost

    return (
        cost_at_factory,
        rejection_cost,
        final_cost
    )


# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.header("Input Parameters")

fao = st.sidebar.number_input(
    "Farmer & Agent Premium",
    value=0.0
)

ll = st.sidebar.number_input(
    "Loading Labour",
    value=1.0
)

rm = st.sidebar.number_input(
    "RM Rate",
    value=290.0
)

trans = st.sidebar.number_input(
    "Transportation",
    value=7990.0
)

ice = st.sidebar.number_input(
    "Ice Charges",
    value=402.0
)

smbs = st.sidebar.number_input(
    "SMBS Charges",
    value=288.0
)

harvest = st.sidebar.number_input(
    "Harvest Quantity",
    value=200.0
)

rejection = st.sidebar.slider(
    "Mortality (%)",
    0.0,
    95.0,
    25.0
)

processing = st.sidebar.number_input(
    "Processing + Packaging",
    value=69.0
)

outward = st.sidebar.number_input(
    "Outward Logistics",
    value=61.0
)


# ----------------------------
# CALCULATIONS
# ----------------------------

factory_cost, rejection_cost, final_cost = cost_per_kg(
    fao,
    ll,
    rm,
    trans,
    ice,
    smbs,
    harvest,
    rejection,
    processing,
    outward
)


# ----------------------------
# KPI CARDS
# ----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Final Cost",
        f"₹{final_cost:.2f}/kg"
    )

with col2:
    st.metric(
        "🏭 Factory Cost",
        f"₹{factory_cost:.2f}/kg"
    )

with col3:
    st.metric(
        "⚠️ Rejection Cost",
        f"₹{rejection_cost:.2f}/kg"
    )

st.markdown("---")


# ----------------------------
# CHARTS
# ----------------------------

left, right = st.columns([1.3, 1])



# -------- Mortality graph --------

mortality = list(range(0,95))

costs = []

for m in mortality:

    _, _, c = cost_per_kg(
        fao,
        ll,
        rm,
        trans,
        ice,
        smbs,
        harvest,
        m,
        processing,
        outward
    )

    costs.append(c)

df = pd.DataFrame({
    "Mortality (%)": mortality,
    "Cost": costs
})

fig = px.line(
    df,
    x="Mortality (%)",
    y="Cost",
    title="Cost vs Mortality"
)

left.plotly_chart(
    fig,
    use_container_width=True
)



# -------- Pie Chart --------

pie = pd.DataFrame({

    "Component":[

        "RM",

        "Transportation",

        "Ice",

        "SMBS",

        "Loading",

        "Processing",

        "Outward"

    ],

    "Value":[

        rm,

        trans/harvest,

        ice/harvest,

        smbs/harvest,

        ll,

        processing,

        outward

    ]

})

piefig = px.pie(
    pie,
    values="Value",
    names="Component",
    hole=.55,
    title="Cost Breakdown"
)

right.plotly_chart(
    piefig,
    use_container_width=True
)


st.markdown("---")


# ----------------------------
# DETAILS
# ----------------------------

with st.expander("📋 View Calculation Details"):

    st.write(f"Factory Cost : ₹{factory_cost:.2f}")

    st.write(f"Rejection Cost : ₹{rejection_cost:.2f}")

    st.write(f"Final Cost : ₹{final_cost:.2f}")

    st.dataframe(
        pie,
        use_container_width=True
    )