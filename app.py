import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from decision_engine import PolicyDecisionEngine
from grid_impact_calculator import GridImpactCalculator
from rwanda_context import RwandaEVContext
import json
from datetime import datetime

# Helper Funnction for Data & Partnerships Tab


def get_update_impact(frequency):
    """Calculate impact based on update frequency"""
    impacts = {
        "Monthly": 30,
        "Weekly": 70,
        "Daily": 90,
        "Real-time": 95
    }
    return impacts.get(frequency, 0)


# Page Configuration
st.set_page_config(
    page_title="Rwanda EV Policy Simulator",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "https://raw.githubusercontent.com/MutuaNdunda/smartdash_mvp/refs/heads/main/data"


@st.cache_data
def load(name):
    url = f"{BASE_URL}/{name}"
    return pd.read_csv(url)


# Load all datasets from GitHub raw URLs
ev = load("ev_adoption.csv")
stations = load("charging_stations.csv")
tariffs = load("tariffs.csv")
grid = load("grid_load_week.csv")
sessions = load("charging_sessions.csv")
policies = load("policy_timeline.csv")
investment = load("charging_investment.csv")
imports = load("ev_imports.csv")
sectors = load("sector_consumption.csv")
districts = load("districts.csv")
feedback = load("user_feedback.csv")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #0066CC;
        padding-bottom: 10px;
        border-bottom: 2px solid #0066CC;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #0066CC;
        margin-bottom: 10px;
    }
    .policy-recommendation {
        background-color: #e6f7e6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00cc00;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Context and Engines
rwanda_context = RwandaEVContext()
decision_engine = PolicyDecisionEngine(rwanda_context)
grid_calculator = GridImpactCalculator()

# App Title
st.title("Rwanda Electric Mobility Policy Decision Support System")
st.markdown("""
*Supporting evidence-based policy decisions for Rwanda's electric vehicle transition aligned with national climate goals*
""")

# Sidebar for Navigation
# Sidebar for Navigation
with st.sidebar:
    st.markdown("## Navigation")
    selected_tab = st.radio(
        "Select Module:",
        ["Overview", "Scenario Simulator", "Grid Impact Analysis",
         "Financial Modeling", "Data & Partnerships"]
    )

    year_selected = st.selectbox(
        "Select Year",
        sorted(ev["Year"].unique())
    )

    district_selected = st.multiselect(
        "Select Districts",
        stations["District"].unique(),
        default=list(stations["District"].unique())
    )

    st.markdown("---")
    st.markdown("### National Targets")
    st.progress(0.35, text="2030 EV Target: 30% penetration")
    st.caption("Current EV Penetration: ~5%")
    st.markdown("**2050 Goal:** 150,000+ EVs")
    st.markdown("**Grid Capacity:** 230 MW (2023)")


# Main Content
if selected_tab == "Scenario Simulator":
    st.header("Policy Decisions & Scenario Simulator")

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Stakeholder Selection
        stakeholder = st.selectbox(
            "**Primary Stakeholder**",
            [
                "National Government / MININFRA",
                "Rwanda Energy Group (REG)",
                "Rwanda Utilities Regulatory Authority (RURA)",
                "City of Kigali",
                "Rwanda Development Board (RDB)",
                "Rwanda Environment Management Authority (REMA)",
                "Private Investor / Developer",
                "Development Partner (World Bank, AfDB)",
                "EV Manufacturer/Importer",
                "Research Institution"
            ],
            help="Select your institutional perspective for tailored recommendations"
        )

        # Scenario Parameters
        st.subheader("Scenario Parameters")

        param_col1, param_col2, param_col3 = st.columns(3)

        with param_col1:
            st.markdown("#### Fleet Parameters")
            total_evs = st.number_input(
                "**Registered EVs**",
                min_value=1000,
                max_value=300000,
                value=50000,
                step=5000,
                help="Current projection: 150,000 by 2050"
            )

            ev_growth = st.slider(
                "**Annual EV Growth Rate (%)**",
                5, 40, 20, 5,
                help="Rwanda's target: 25% annual growth"
            )

            two_wheeler_share = st.slider(
                "**Two-Wheeler Share (%)**",
                10, 80, 50, 5,
                help="Current share: 52%. Critical for urban mobility"
            )

            fleet_mix = st.multiselect(
                "**Priority Fleet Segments**",
                ["Private Cars", "E-Motos", "Buses", "Taxis",
                    "Government Fleets", "Goods Delivery"],
                default=["E-Motos", "Buses", "Taxis"],
                help="Focus infrastructure planning on these segments"
            )

        with param_col2:
            st.markdown("#### Infrastructure Parameters")
            public_chargers = st.number_input(
                "**Public Charging Stations**",
                10, 5000, 300, 50,
                help="Current: 156. Target: 500 by 2025"
            )

            charger_types = st.select_slider(
                "**Charger Power Mix**",
                options=["10kW Focus", "Balanced",
                         "20kW Focus", "Fast-Charge Heavy"],
                value="Balanced",
                help="10kW for e-motos, 20kW+ for vehicles"
            )

            urban_rural_split = st.slider(
                "**Urban vs Rural Charging Split (%)**",
                0, 100, (70, 30),
                help="Kigali focus vs nationwide coverage"
            )

            solar_integration = st.slider(
                "**Solar-Powered Chargers (%)**",
                0, 100, 30, 10,
                help="Align with Rwanda's solar potential"
            )

        with param_col3:
            st.markdown("#### Policy & Grid Parameters")
            policy_priority = st.selectbox(
                "**Primary Policy Objective**",
                [
                    "Balanced Growth",
                    "Infrastructure Access & Equity",
                    "Grid Stability & Resilience",
                    "Private Investment Attraction",
                    "Climate Impact Maximization",
                    "Urban Air Quality",
                    "Energy Security",
                    "Job Creation & Local Industry"
                ],
                index=0
            )

            investment_appetite = st.select_slider(
                "**Public Investment Appetite**",
                ["Conservative", "Moderate", "Aggressive", "Transformative"],
                value="Moderate"
            )

            regulatory_flexibility = st.select_slider(
                "**Regulatory Flexibility**",
                ["Traditional", "Adaptive", "Innovation-Friendly", "Sandbox Approach"],
                value="Adaptive"
            )

            peak_charging_share = st.slider(
                "**Peak-Hour Charging Share (%)**",
                10, 90, 50, 5,
                help="Simulation shows 23:00-03:00 is critical period"
            )

            v2g_adoption = st.slider(
                "**V2G Readiness Level**",
                0, 100, 20, 10,
                help="Vehicle-to-Grid technology adoption"
            )

    with col2:
        st.subheader("Quick Impact Assessment")

        # Calculate metrics
        ev_to_charger_ratio = round(total_evs / max(public_chargers, 1), 1)

        # Use decision engine for assessment
        scenario_data = {
            'total_evs': total_evs,
            'public_chargers': public_chargers,
            'ev_growth': ev_growth,
            'two_wheeler_share': two_wheeler_share,
            'peak_charging_share': peak_charging_share,
            'policy_priority': policy_priority,
            'investment_appetite': investment_appetite,
            'regulatory_flexibility': regulatory_flexibility,
            'stakeholder': stakeholder,
            'charger_types': charger_types,
            'solar_integration': solar_integration,
            'v2g_adoption': v2g_adoption,
            'fleet_mix': fleet_mix
        }

        assessment = decision_engine.assess_scenario(scenario_data)
        grid_analysis = grid_calculator.calculate_grid_impact(scenario_data)

        # Display assessment
        st.markdown("### Assessment Results")

        st.metric("EV-to-Charger Ratio", f"{ev_to_charger_ratio}:1",
                  delta="Target: 50:1" if ev_to_charger_ratio > 50 else None,
                  delta_color="inverse")

        # Risk Indicators
        st.markdown("#### Risk Indicators")

        risk_col1, risk_col2, risk_col3 = st.columns(3)
        with risk_col1:
            risk_level = assessment['infrastructure_pressure']
            color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
            st.markdown(f'<span style="color:{color}; font-weight:bold;">Infrastructure: {risk_level}</span>',
                        unsafe_allow_html=True)

        with risk_col2:
            risk_level = assessment['grid_risk']
            color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
            st.markdown(f'<span style="color:{color}; font-weight:bold;">Grid Risk: {risk_level}</span>',
                        unsafe_allow_html=True)

        with risk_col3:
            risk_level = assessment['financial_viability']
            color = "red" if risk_level == "Low" else "orange" if risk_level == "Medium" else "green"
            st.markdown(f'<span style="color:{color}; font-weight:bold;">Finances: {risk_level}</span>',
                        unsafe_allow_html=True)

        # Grid Impact Summary
        st.markdown("#### Grid Impact")
        st.write(
            f"**Additional Demand:** {grid_analysis['additional_demand_mw']:.1f} MW")
        st.write(
            f"**DG Required:** {grid_analysis['dg_capacity_needed']:.1f} MW")

        # FIXED: Safe progress bar with cap at 1.0
        grid_utilization = grid_analysis['grid_capacity_utilization']
        progress_value = min(grid_utilization / 100, 1.0)

        if grid_utilization > 100:
            st.error(f"⚠️ Grid Overload: {grid_utilization:.1f}%")
            st.progress(1.0, text="CRITICAL: Grid overloaded")
        else:
            st.progress(progress_value,
                        text=f"Grid Capacity: {grid_utilization:.1f}%")

        # Save Scenario
        if st.button("💾 Save Current Scenario", use_container_width=True):
            scenario_name = st.text_input(
                "Scenario Name:", value=f"Scenario_{datetime.now().strftime('%Y%m%d_%H%M')}")
            if st.button("Confirm Save"):
                decision_engine.save_scenario(
                    scenario_name, scenario_data, assessment)
                st.success(f"Scenario '{scenario_name}' saved!")

    # Main Results Area
    st.markdown("---")

    # Policy Recommendations Section
    st.subheader("Tailored Policy Recommendations")

    recommendations = decision_engine.generate_recommendations(
        scenario_data, assessment)

    # Categorize recommendations
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Priority Actions", "⚡ Grid Management", "🏗️ Infrastructure", "💰 Financial"])

    with tab1:
        st.markdown("#### Immediate Priority Actions")
        priority_recs = [r for r in recommendations if r.get(
            'priority') == 'High'][:5]

        if priority_recs:
            for rec in priority_recs:
                with st.expander(f"📍 {rec.get('title', 'Untitled')} ({rec.get('timeframe', 'N/A')})"):
                    st.write(rec.get('description', 'No description available'))

                    # Safely get impact and stakeholders
                    impact = rec.get('impact', 'Medium')
                    stakeholders = rec.get('stakeholders', ['Various'])

                    # Handle stakeholders as string or list
                    if isinstance(stakeholders, list):
                        stakeholders_str = ', '.join(stakeholders)
                    else:
                        stakeholders_str = str(stakeholders)

                    st.caption(
                        f"**Impact:** {impact} | **Stakeholders:** {stakeholders_str}")

                    if rec.get('kpi'):
                        st.metric("Target KPI", rec['kpi'])

                    if rec.get('estimated_cost'):
                        st.metric("Estimated Cost", rec['estimated_cost'])

                    # Show actions if available
                    if rec.get('actions'):
                        st.markdown("**Actions:**")
                        for action in rec['actions']:
                            st.write(f"• {action}")
        else:
            st.info("No high-priority actions identified for current scenario.")

    with tab2:
        st.markdown("#### Grid & Energy Management")
        grid_recs = [r for r in recommendations if any(keyword in r.get('category', '').lower()
                                                       for keyword in ['grid', 'energy'])]

        if grid_recs:
            for rec in grid_recs:
                with st.expander(f"⚡ {rec.get('title', 'Grid Action')}"):
                    st.write(rec.get('description', ''))

                    # Show progress for implementation level
                    if rec.get('implementation_level'):
                        st.write(f"**Implementation Readiness:**")
                        st.progress(rec['implementation_level'])

                    if rec.get('estimated_cost'):
                        st.metric("Cost Estimate", rec['estimated_cost'])
        else:
            st.info(
                "No specific grid management recommendations for current scenario.")

    with tab3:
        st.markdown("#### Infrastructure Development")
        infra_recs = [r for r in recommendations if 'infrastructure' in r.get(
            'category', '').lower()]

        if infra_recs:
            for rec in infra_recs:
                st.markdown(
                    f"**{rec.get('title', 'Infrastructure Project')}**")
                st.write(rec.get('description', ''))
                st.caption(
                    f"Category: {rec.get('category', 'Infrastructure')}")

                if rec.get('estimated_cost'):
                    st.metric("Estimated Cost", rec['estimated_cost'])

                st.markdown("---")
        else:
            st.info(
                "No infrastructure-specific recommendations for current scenario.")

    with tab4:
        st.markdown("#### Financial & Incentive Measures")
        financial_recs = [r for r in recommendations if any(keyword in r.get('category', '').lower()
                                                            for keyword in ['financial', 'incentive', 'investment'])]

        if financial_recs:
            for rec in financial_recs:
                st.markdown(f"**{rec.get('title', 'Financial Measure')}**")
                st.write(rec.get('description', ''))

                if rec.get('roi'):
                    st.metric("Projected ROI", rec['roi'])

                if rec.get('budget_estimate'):
                    st.metric("Budget Estimate", rec['budget_estimate'])

                st.markdown("---")
        else:
            st.info("No financial-specific recommendations for current scenario.")

    # Implementation Roadmap
    st.subheader("Implementation Roadmap")

    roadmap_data = decision_engine.generate_roadmap(scenario_data, stakeholder)

    # Gantt Chart Visualization
    roadmap_df = pd.DataFrame(roadmap_data)
    if not roadmap_df.empty:
        fig = px.timeline(roadmap_df, x_start="Start", x_end="End", y="Phase",
                          color="Priority", title="Policy Implementation Timeline",
                          hover_data=["Tasks", "Responsible", "Budget"])
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)

    # Comparative Analysis
    st.subheader("Scenario Comparison")

    if st.button("Compare with Baseline Scenario"):
        baseline = decision_engine.get_baseline_scenario()
        comparison = decision_engine.compare_scenarios(scenario_data, baseline)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Current Scenario")
            st.dataframe(pd.DataFrame(
                [scenario_data]).T.rename(columns={0: 'Value'}))

        with col2:
            st.markdown("##### Baseline (Current Policy)")
            st.dataframe(pd.DataFrame(
                [baseline]).T.rename(columns={0: 'Value'}))

        # Show differences
        st.markdown("##### Key Differences")
        for diff in comparison['differences']:
            st.write(f"- {diff}")

elif selected_tab == "Grid Impact Analysis":
    st.header("Grid Impact Analysis")

    # Technical parameters from research
    st.markdown("### Technical Grid Analysis Based on IPSA+ Simulations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Maximum Safe Penetration Rates")
        penetration_data = {
            "Vehicle Type": ["Private Cars", "Buses", "Taxis"],
            "10kW Chargers": ["1.5%", "10%", "10%"],
            "20kW Chargers": ["1%", "8%", "8%"],
            "With V2G": ["3%", "15%", "15%"]
        }
        st.table(pd.DataFrame(penetration_data))

        st.markdown("#### Transformer Loading Impact")
        st.write("**Scenario 1 (10kW):** 2/18 transformers >80% load")
        st.write("**Scenario 2 (20kW):** 7/18 transformers >80% load")
        st.write("**Critical Period:** 23:00-03:00")

    with col2:
        st.markdown("#### Mitigation Strategies")

        strategy = st.selectbox(
            "Select Mitigation Strategy:",
            ["Distributed Generation", "Smart Charging",
                "V2G Implementation", "Solar Microgrids"]
        )

        if strategy == "Distributed Generation":
            st.markdown("""
            **Recommended DG Capacity:**
            - 6.5 MW for 10kW charger scenario
            - 24.5 MW for 20kW charger scenario
            
            **Optimal Placement:** Near critical substations
            **Tool:** Continuation Power Flow (CPF) analysis
            """)

        elif strategy == "Solar Microgrids":
            st.markdown("""
            **Economic Analysis (HOMER Grid):**
            - LCOE reduction: 139.7%
            - New LCOE: -$0.103/kWh
            - Annual savings: $1.73M
            
            **System Components:**
            - Solar PV: 500 kW
            - Battery Storage: 1 MWh
            - Grid connection
            """)

        elif strategy == "V2G Implementation":
            st.markdown("""
            **Transformer Loading Regulation Framework:**
            - Additional capacity: Up to 6 MW
            - Critical substation support
            - Aggregator-based management
            
            **Benefits:**
            - Improved grid reliability
            - Revenue stream for EV owners
            - Peak shaving capability
            """)

    # Interactive Grid Simulation
    st.markdown("### Interactive Grid Simulation")

    # FIXED: Define total_evs here (it's not defined from Scenario Simulator tab)
    total_evs = st.number_input(
        "Total EVs", 1000, 300000, 50000, 5000, key="grid_total_evs")

    ev_penetration = st.slider(
        "EV Penetration Rate (%)", 1, 30, 10, key="grid_penetration")
    charger_power = st.select_slider("Average Charger Power (kW)", [
                                     10, 15, 20, 50], value=20, key="grid_charger_power")
    dg_capacity = st.slider("DG Capacity Added (MW)", 0,
                            50, 10, key="grid_dg_capacity")
    peak_charging_share = st.slider(
        "Peak Charging Share (%)", 10, 90, 50, key="grid_peak_share")

    # Calculate impacts
    base_demand = 100  # MW
    additional_demand = (total_evs * charger_power *
                         peak_charging_share/100) / 1000
    total_demand = base_demand + additional_demand
    grid_capacity = 230  # Rwanda's current grid capacity
    utilization = (total_demand / grid_capacity) * 100

    # Visualization
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=utilization,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Grid Capacity Utilization"},
        delta={'reference': 85, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 120]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 70], 'color': "green"},
                {'range': [70, 90], 'color': "yellow"},
                {'range': [90, 120], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    # Recommendations based on simulation
    if utilization > 90:
        st.error("⚠️ Grid overload risk! Implement immediate mitigation measures:")
        st.write("1. Deploy additional DG capacity")
        st.write("2. Implement Time-of-Use tariffs")
        st.write("3. Accelerate V2G pilot programs")
    elif utilization > 70:
        st.warning("⚠️ Grid approaching capacity. Consider proactive measures.")
    else:
        st.success("✓ Grid within safe operating limits")

elif selected_tab == "Financial Modeling":
    st.header("Financial Modeling & Investment Analysis")

    tab1, tab2, tab3 = st.tabs(
        ["Cost-Benefit Analysis", "Incentive Optimization", "PPP Structures"])

    with tab1:
        st.subheader("Cost-Benefit Analysis for Different Stakeholders")

        stakeholder_type = st.selectbox(
            "Analyze for:",
            ["Government", "Private Investor", "EV Owner", "Utility Company"]
        )

        if stakeholder_type == "Government":
            st.markdown("""
            **Government Perspective:**
            
            | Metric | Value | Notes |
            |--------|-------|-------|
            | Fuel Import Savings | $50M/year | At 50,000 EVs |
            | Health Cost Savings | $15M/year | Reduced air pollution |
            | Carbon Credit Value | $8M/year | At $50/ton CO2 |
            | Infrastructure Cost | $120M | 500 charging stations |
            | Subsidy Cost | $40M | 5-year program |
          ƒ  | **Net Present Value** | **$180M** | 10-year horizon |
            """)

            # ROI Calculator
            st.markdown("#### Public Investment ROI Calculator")
            public_investment = st.number_input(
                "Public Investment ($M)", 10, 500, 100, key="pub_investment")
            private_leverage = st.slider(
                "Private Capital Leverage", 1.0, 5.0, 2.5, key="private_leverage")
            job_creation = st.slider(
                "Jobs Created per $1M", 5, 50, 20, key="job_creation")

            total_investment = public_investment * (1 + private_leverage)
            total_jobs = public_investment * job_creation

            st.metric("Total Investment Mobilized",
                      f"${total_investment:.1f}M")
            st.metric("Direct Jobs Created", f"{int(total_jobs)}")
            st.metric("Leverage Ratio", f"{private_leverage}:1")

        elif stakeholder_type == "EV Owner":
            st.markdown("#### E-Moto Operator Economics")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Traditional Motorbike**")
                st.write("Fuel Cost: $7/day")
                st.write("Maintenance: $3/day")
                st.write("Total: $10/day")
                st.write("Monthly: $300")

            with col2:
                st.markdown("**Electric Motorbike**")
                st.write("Electricity: $1.5/day")
                st.write("Maintenance: $0.5/day")
                st.write("Total: $2/day")
                st.write("Monthly: $60")

            st.success(f"**Monthly Savings: $240** (80% reduction)")
            st.write("**Payback Period:** 18-24 months")

    with tab2:
        st.subheader("Incentive Effectiveness Analysis")

        # Based on regression analysis from literature
        st.markdown("#### Regression Analysis Results (Odds Ratios)")

        incentives_data = {
            "Incentive Type": ["Financial Subsidies", "Tax Exemptions", "Charging Infrastructure",
                               "Public Awareness", "Maintenance Training", "Priority Lanes"],
            "Effectiveness (OR)": [3.39, 2.41, 1.77, 1.63, 1.93, 1.45],
            "Cost Efficiency": ["High", "Very High", "Medium", "Low", "Medium", "Low"],
            "Implementation Time": ["Medium", "Fast", "Slow", "Fast", "Medium", "Fast"]
        }

        df_incentives = pd.DataFrame(incentives_data)
        st.dataframe(df_incentives, use_container_width=True)

        # Interactive incentive builder
        st.markdown("#### Build Your Incentive Package")

        budget = st.slider("Annual Budget ($M)", 5, 100,
                           20, key="incentive_budget")

        incentive_options = st.multiselect(
            "Select Incentives to Include:",
            options=incentives_data["Incentive Type"],
            default=["Financial Subsidies", "Tax Exemptions"],
            key="incentive_options"
        )

        if incentive_options:
            total_effectiveness = sum([incentives_data["Effectiveness (OR)"][i]
                                      for i, inc in enumerate(incentives_data["Incentive Type"])
                                      if inc in incentive_options])
            estimated_ev_increase = int(
                total_effectiveness * 5000)  # Base effect

            st.metric("Combined Effectiveness Score",
                      f"{total_effectiveness:.2f}")
            st.metric("Estimated Additional EV Adoption",
                      f"{estimated_ev_increase:,}")
            st.metric("Cost per Additional EV",
                      f"${budget*1e6/estimated_ev_increase:,.0f}")

    with tab3:
        st.subheader("PPP Structures")
        st.markdown("""
        ### Public-Private Partnership Models for EV Infrastructure
        
        **Available PPP Models:**
        
        1. **Build-Operate-Transfer (BOT)**
           - Private sector builds, operates for 15-20 years, then transfers to government
           - Suitable for: Highway charging corridors, major urban hubs
        
        2. **Design-Build-Finance-Operate-Maintain (DBFOM)**
           - Private sector handles entire lifecycle
           - Suitable for: Integrated charging networks, smart grid integration
        
        3. **Concession Model**
           - Private operator pays concession fee, retains revenue
           - Suitable for: Existing infrastructure upgrades
        
        4. **Joint Venture (JV)**
           - Public-private equity partnership
           - Suitable for: New technology pilots, innovation centers
        
        5. **Management Contract**
           - Private operator manages publicly-owned assets
           - Suitable for: Government fleet charging, public transport charging
        """)

        # PPP Calculator
        st.markdown("#### PPP Financial Calculator")

        col1, col2 = st.columns(2)
        with col1:
            project_cost = st.number_input(
                "Project Cost ($M)", 1, 500, 50, key="ppp_cost")
            concession_years = st.slider(
                "Concession Period (years)", 5, 30, 15, key="concession_years")

        with col2:
            public_share = st.slider(
                "Public Share (%)", 0, 100, 30, key="public_share")
            expected_roi = st.slider(
                "Expected Private ROI (%)", 5, 25, 12, key="expected_roi")

        public_investment = project_cost * (public_share / 100)
        private_investment = project_cost - public_investment
        annual_revenue_needed = private_investment * (expected_roi / 100)

        st.metric("Public Investment", f"${public_investment:.1f}M")
        st.metric("Private Investment", f"${private_investment:.1f}M")
        st.metric("Required Annual Revenue", f"${annual_revenue_needed:.1f}M")

elif selected_tab == "Overview":
    st.header("Rwanda EV Transition Overview")

    # Add some context
    st.markdown("""
    *Real-time dashboard tracking Rwanda's electric vehicle transition progress and policy impacts*
    """)

    # Key Metrics with better formatting
    col1, col2, col3, col4 = st.columns(4)
    selected_row = ev[ev["Year"] == year_selected].iloc[0]

    col1.metric(
        "Total EVs",
        f"{int(selected_row['EV_Total']):,}",
        delta=f"+{int(selected_row['EV_Growth']):,} YoY" if 'EV_Growth' in selected_row else None,
        delta_color="normal"
    )
    col2.metric(
        "EV 2-Wheelers",
        f"{int(selected_row['EV_2W']):,}",
        f"{int(selected_row['EV_2W']/selected_row['EV_Total']*100)}%" if selected_row['EV_Total'] > 0 else "0%"
    )
    col3.metric(
        "Charging Stations",
        len(stations),
        f"Target: 500 by 2025"  # Add target context
    )
    col4.metric(
        "EV Tariff",
        f"{int(tariffs[tariffs['Tariff_Type'] == 'EV_Tariff']['Price_RWF_per_kWh'].values[0]):,} RWF/kWh",
        "Time-of-Use available" if len(
            tariffs[tariffs['Tariff_Type'] == 'EV_Tariff']) > 1 else "Flat rate"
    )

    # EV Adoption Trend with more detail
    st.subheader("EV Adoption Trend")

    col1, col2 = st.columns([3, 1])
    with col1:
        # Create multi-line chart showing different vehicle types
        fig = go.Figure()

        # Total EVs
        fig.add_trace(go.Scatter(
            x=ev["Year"],
            y=ev["EV_Total"],
            mode='lines+markers',
            name='Total EVs',
            line=dict(color='#0066CC', width=3)
        ))

        # 2-Wheelers if available
        if 'EV_2W' in ev.columns:
            fig.add_trace(go.Scatter(
                x=ev["Year"],
                y=ev["EV_2W"],
                mode='lines+markers',
                name='2-Wheelers',
                line=dict(color='#00CC96', width=2, dash='dash')
            ))

        # Add 2030 target line
        fig.add_hline(
            y=30000,  # Rwanda's 2030 target
            line_dash="dash",
            line_color="red",
            annotation_text="2030 Target",
            annotation_position="bottom right"
        )

        fig.update_layout(
            title="EV Growth Projection",
            xaxis_title="Year",
            yaxis_title="Number of EVs",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Quick stats box
        st.markdown("### 📊 Quick Stats")

        # Calculate some metrics
        if len(ev) > 1:
            growth_rate = ((ev.iloc[-1]['EV_Total'] - ev.iloc[-2]
                           ['EV_Total']) / ev.iloc[-2]['EV_Total']) * 100
            st.metric("Annual Growth", f"{growth_rate:.1f}%")

        if 'EV_Total' in selected_row and 'public_chargers' in selected_row:
            ev_to_charger = selected_row['EV_Total'] / \
                max(selected_row['public_chargers'], 1)
            st.metric("EV-to-Charger", f"{ev_to_charger:.0f}:1")

        st.metric("Districts Covered", len(stations['District'].unique()))

    # Charging Station Map with better visualization
    st.subheader("Charging Infrastructure Map")

    map_col1, map_col2 = st.columns([3, 1])

    with map_col1:
        filtered_map = stations[stations["District"].isin(
            district_selected)].copy()
        if not filtered_map.empty:
            filtered_map = filtered_map.rename(
                columns={"Latitude": "latitude", "Longitude": "longitude"}
            )
            st.map(filtered_map[["latitude", "longitude"]])
        else:
            st.info("No charging stations in selected districts")

    with map_col2:
        st.markdown("### 📍 District Coverage")

        # Get ACTUALLY SELECTED districts with stations
        selected_stations = stations[stations["District"].isin(
            district_selected)]

        if not selected_stations.empty:
            # Count unique districts in selection
            covered_districts = selected_stations['District'].unique()
            total_covered = len(covered_districts)
            total_selected = len(district_selected)

            # Calculate coverage percentage
            coverage_pct = (total_covered / max(total_selected, 1)) * 100

            st.metric("Districts Covered", f"{total_covered}/{total_selected}")
            st.progress(coverage_pct / 100)

            # List covered districts
            st.markdown("**With Stations:**")
            for district in covered_districts:
                count = len(
                    selected_stations[selected_stations['District'] == district])
                st.write(f"✓ {district} ({count} stations)")

            # Show missing districts if any
            missing = set(district_selected) - set(covered_districts)
            if missing:
                st.markdown("**No Stations In:**")
                for district in missing:
                    st.write(f"✗ {district}")
        else:
            st.warning("No stations in selected districts")

    # ====== IMPROVED POLICY SUMMARY BOX ======
    st.subheader("Policy Insights & Recommendations")

    # Create tabs for different policy aspects
    insight_tab1, insight_tab2, insight_tab3, insight_tab4 = st.tabs([
        "📊 Infrastructure", "⚡ Grid Impact", "💰 Economics", "🌍 Climate"
    ])

    with insight_tab1:
        # Infrastructure insights
        st.markdown("### Infrastructure Gap Analysis")

        # Calculate key metrics
        ev_total = selected_row['EV_Total']
        chargers_total = len(stations)
        ev_to_charger = ev_total / max(chargers_total, 1)

        insights = []

        if ev_to_charger > 150:
            insights.append(
                "🚨 **CRITICAL**: EV-to-charger ratio exceeds 150:1")
            insights.append(
                f"• Current ratio: **{ev_to_charger:.0f}:1** vs target 50:1")
            insights.append(
                f"• Additional stations needed: **{ev_total//50 - chargers_total:,}**")
            insights.append(
                "• **Immediate action required**: Accelerate deployment")
        elif ev_to_charger > 100:
            insights.append("⚠️ **HIGH**: Infrastructure pressure increasing")
            insights.append(f"• Current ratio: **{ev_to_charger:.0f}:1**")
            insights.append(
                f"• Planning needed for: **{ev_total//80:,}** more stations")
            insights.append("• **Action**: Fast-track approval processes")
        else:
            insights.append("✅ **MANAGEABLE**: Infrastructure keeping pace")
            insights.append(f"• Current ratio: **{ev_to_charger:.0f}:1**")
            insights.append("• **Continue** planned expansion")

        # District concentration analysis
        if 'District' in stations.columns:
            kigali_stations = len(stations[stations['District'] == 'Kigali'])
            kigali_share = (kigali_stations / max(chargers_total, 1)) * 100

            if kigali_share > 70:
                insights.append(
                    f"\n📍 **Geographic Concentration**: {kigali_share:.0f}% in Kigali")
                insights.append(
                    "• **Recommendation**: Incentivize rural deployment")

        for insight in insights:
            st.write(insight)

    with insight_tab2:
        # Grid impact insights
        st.markdown("### Grid Integration Status")

        grid_insights = []

        # Peak charging analysis (simplified)
        peak_hours = ["18:00", "19:00", "20:00", "21:00"]
        if 'peak_charging_share' in selected_row:
            peak_share = selected_row['peak_charging_share']

            if peak_share > 60:
                grid_insights.append(
                    "⚠️ **HIGH GRID RISK**: Peak charging >60%")
                grid_insights.append(
                    f"• {peak_share:.0f}% charging during peak hours")
                grid_insights.append(
                    "• **Recommendation**: Implement Time-of-Use tariffs")
                grid_insights.append(
                    "• **Action**: Launch smart charging pilot")
            elif peak_share > 40:
                grid_insights.append(
                    "📈 **MODERATE LOAD**: Manage peak charging")
                grid_insights.append(f"• {peak_share:.0f}% during peak hours")
                grid_insights.append(
                    "• **Recommendation**: Promote off-peak charging")
            else:
                grid_insights.append(
                    "✅ **BALANCED**: Healthy charging patterns")
                grid_insights.append("• **Continue**: Monitor and maintain")

        # DG needs
        if 'EV_Total' in selected_row and selected_row['EV_Total'] > 50000:
            grid_insights.append("\n⚡ **Grid Reinforcement Needed**")
            grid_insights.append(
                f"• {selected_row['EV_Total']//10000:.0f} MW DG capacity recommended")
            grid_insights.append("• Priority: Critical substations")

        for insight in grid_insights:
            st.write(insight)

    with insight_tab3:
        # Economic insights
        st.markdown("### Economic Indicators")

        economic_insights = []

        # Tariff analysis
        ev_tariff = tariffs[tariffs["Tariff_Type"] ==
                            "EV_Tariff"]["Price_RWF_per_kWh"].values[0]
        residential_tariff = tariffs[tariffs["Tariff_Type"] ==
                                     "Residential"]["Price_RWF_per_kWh"].values[0] if "Residential" in tariffs["Tariff_Type"].values else None

        economic_insights.append(
            f"📊 **Tariff Structure**: {ev_tariff:,.0f} RWF/kWh")

        if residential_tariff:
            if ev_tariff < residential_tariff:
                economic_insights.append(
                    f"• **Incentive**: {((residential_tariff - ev_tariff)/residential_tariff*100):.0f}% cheaper than residential")
                economic_insights.append(
                    "• **Impact**: Encourages EV adoption")
            else:
                economic_insights.append(
                    "• **Review**: Consider tariff adjustments")

        # Cost savings estimate
        if 'EV_Total' in selected_row:
            # Simplified: $1000 per EV per year
            annual_savings = selected_row['EV_Total'] * 1000
            economic_insights.append(
                f"\n💰 **Annual Savings Estimate**: ${annual_savings:,.0f}")
            economic_insights.append("• Fuel import reduction")
            economic_insights.append("• Maintenance cost savings")
            economic_insights.append("• Health benefit savings")

        for insight in economic_insights:
            st.write(insight)

    with insight_tab4:
        # Climate insights
        st.markdown("### Climate Impact")

        climate_insights = []

        if 'EV_Total' in selected_row:
            # Tons CO2 per EV per year
            co2_reduction = selected_row['EV_Total'] * 2.5
            climate_insights.append(
                f"🌿 **CO₂ Reduction**: {co2_reduction:,.0f} tons/year")
            climate_insights.append(
                f"• Equivalent to {co2_reduction*50:,.0f} trees planted")

            # Progress toward Rwanda's NDC
            ndc_target = 3800000  # Rwanda's NDC target in tons
            progress = (co2_reduction / ndc_target) * 100
            climate_insights.append(
                f"\n🎯 **NDC Contribution**: {progress:.1f}% of national target")

            if progress < 5:
                climate_insights.append(
                    "• **Opportunity**: Scale up for greater impact")
            elif progress < 15:
                climate_insights.append(
                    "• **Progress**: On track with moderate contribution")
            else:
                climate_insights.append(
                    "• **Leadership**: Significant climate contribution")

        for insight in climate_insights:
            st.write(insight)

    # Quick action items
    st.markdown("---")
    st.markdown("### Recommended Actions")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        st.markdown("**Short-term (0-6 months):**")
        st.write("• Launch Time-of-Use tariff pilot")
        st.write("• Fast-track 100 new charging stations")
        st.write("• Public awareness campaign on off-peak charging")

    with action_col2:
        st.markdown("**Medium-term (6-24 months):**")
        st.write("• Implement smart charging standards")
        st.write("• Deploy 50 MW distributed generation")
        st.write("• Expand charging to 5 new districts")

    # Demo Video (optional - keep if relevant)
    st.subheader("📹 Overview Video")
    st.video("https://youtu.be/TdP2X5-MQ08")

elif selected_tab == "Data & Partnerships":
    # Helper Function for this tab

    st.header("Data & Partnerships")
    st.markdown(
        "*Transparent data ecosystem for evidence-based EV policy decisions*")

    # Introduction
    st.markdown("""
    ### Purpose
    This section addresses data acquisition, ownership, and scalability concerns while demonstrating
    how the dashboard can evolve from simulated data to real-time operational data.
    """)

    # Dataset Overview Table
    st.subheader(" Dataset Overview")

    datasets = pd.DataFrame({
        'Dataset Name': [
            'EV Registration & Fleet Data',
            'Charging Infrastructure Registry',
            'Grid Capacity & Load Profiles',
            'Electricity Tariff Structures',
            'Vehicle Import & Duty Records',
            'Renewable Energy Integration Data',
            'Public Transport EV Adoption',
            'E-Moto Operator Economics',
            'Air Quality & Emissions Data',
            'Consumer Adoption Survey Data'
        ],
        'Institutional Owner': [
            'Rwanda National Police / RURA',
            'MININFRA / RURA',
            'Rwanda Energy Group (REG)',
            'Rwanda Utilities Regulatory Authority (RURA)',
            'Rwanda Revenue Authority (RRA)',
            'Rwanda Energy Group (REG)',
            'Rwanda Utilities Regulatory Authority (RURA)',
            'Private Operators (Ampersand, Spiro)',
            'Rwanda Environment Management Authority (REMA)',
            'University of Rwanda / Research Partners'
        ],
        'Current Status': [
            '🔴 Simulated (MVP)',
            '🟡 Pending Access',
            '🟢 Available (Partial)',
            '🟢 Available',
            '🟡 Negotiation Phase',
            '🟡 In Development',
            '🔴 Simulated (MVP)',
            '🟡 Data Sharing Agreement',
            '🟢 Available',
            '🔴 Research Phase'
        ],
        'Update Frequency': [
            'Monthly',
            'Quarterly',
            'Real-time (Grid)',
            'Annually',
            'Monthly',
            'Real-time',
            'Quarterly',
            'Monthly',
            'Quarterly',
            'Annual Survey'
        ],
        'Sensitivity Level': [
            'Medium',
            'Low',
            'High',
            'Low',
            'High',
            'Medium',
            'Medium',
            'High (Commercial)',
            'Low',
            'Low'
        ]
    })

    # Add color coding
    def color_status(val):
        if 'Simulated' in val:
            color = '#FF6B6B'  # Red
        elif 'Pending' in val:
            color = '#FFD166'  # Yellow
        elif 'Negotiation' in val:
            color = '#FFD166'  # Yellow
        elif 'Available' in val:
            color = '#06D6A0'  # Green
        elif 'Research' in val:
            color = '#118AB2'  # Blue
        else:
            color = 'white'
        return f'background-color: {color}'

    styled_df = datasets.style.applymap(
        color_status, subset=['Current Status'])
    st.dataframe(styled_df, use_container_width=True, height=400)

    # Data Readiness Statement
    st.subheader("Data Readiness Statement")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Current MVP Status
        ⚠️ **Key Limitation:**
        - **70% of data is simulated** for demonstration purposes
        - Based on published research and reasonable assumptions
        - Validated against available public statistics
        
        ✅ **Data Quality:**
        - Grid impact calculations use **actual IPSA+ simulation results**
        - Economic analysis based on **HOMER Grid modeling**
        - Adoption barriers from **published regression studies (n=385)**
        """)

    with col2:
        st.markdown("""
        ### Architecture Design
        🔧 **Modular Data Pipeline:**
        ```
        Real Data Sources → API/ETL → Dashboard
        (Replace simulated)    │        │
                               ↓        ↓
                        Simulated → MVP Dashboard
        ```
        
         **Ready for Real Data:**
        - All calculations accept real-time inputs
        - Schema aligns with institutional formats
        - Authentication framework for sensitive data
        """)

    # Scalability Roadmap
    st.subheader("Scalability Roadmap: Kigali → National")

    # Create timeline visualization
    timeline_data = pd.DataFrame({
        'Phase': ['Phase 1: Kigali MVP', 'Phase 2: Urban Corridors', 'Phase 3: National Scale'],
        'Timeline': ['Q1-Q2 2024', 'Q3-Q4 2024', '2025'],
        'Data Coverage': ['Kigali + 3 districts', '8 urban districts', 'All 30 districts'],
        'Data Sources': ['Simulated + Available', 'Partial real-time', 'Full real-time integration'],
        'Stakeholders': ['MININFRA, REG, RURA', '+ Private sector', '+ All districts']
    })

    st.dataframe(timeline_data, use_container_width=True)

    # Visual timeline
    st.markdown("####Implementation Timeline")

    fig = go.Figure()

    phases = ['Kigali MVP', 'Urban Corridors', 'National Scale']
    districts = [4, 8, 30]
    data_coverage = ['40%', '70%', '100%']

    fig.add_trace(go.Scatter(
        x=phases,
        y=districts,
        mode='lines+markers+text',
        name='Districts Covered',
        text=[f'{d} districts' for d in districts],
        textposition='top center',
        line=dict(color='#0066CC', width=3),
        marker=dict(size=12)
    ))

    fig.update_layout(
        title='National Scaling Plan',
        xaxis_title='Implementation Phase',
        yaxis_title='Number of Districts',
        template='plotly_white',
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

    # Partnership Framework
    st.subheader("Partnership Framework")

    partner_col1, partner_col2 = st.columns(2)

    with partner_col1:
        st.markdown("""
        ### Government Partners
        **MININFRA** (Lead)
        - Policy data
        - Infrastructure deployment
        - National targets
        
        **RURA** (Regulator)
        - EV registration
        - Tariff structures
        - Charging standards
        
        **REG** (Utility)
        - Grid capacity data
        - Load profiles
        - Renewable integration
        """)

    with partner_col2:
        st.markdown("""
        ### Private & Research Partners
        **Private Sector**
        - Ampersand/Spiro: E-moto data
        - Charging operators: Usage patterns
        - Financial institutions: Green financing
        
        **Research Institutions**
        - University of Rwanda: Validation studies
        - ACE-ESD: Technical research
        - International: Best practices
        """)

    # Data Simulation Details
    st.subheader("Research-Based Simulation Methodology")

    with st.expander("View Simulation Parameters", expanded=False):
        st.markdown("""
        ### How We Simulate Data
        
        #### 1. EV Adoption Curve
        ```python
        # Based on Rwanda's NDC and transport sector targets
        base_year_evs = 12,500 (2023 actual)
        growth_rate = 20-30% annually (aligned with national targets)
        2030_target = 30,000 EVs (conservative)
        2050_target = 150,000 EVs (research projection)
        ```
        
        #### 2. Grid Impact Calculations
        ```python
        # From IPSA+ Power Simulation Studies
        max_penetration_10kW = 1.5% private, 10% buses/taxis
        transformer_loading = 2-7/18 transformers >80% capacity
        critical_period = 23:00-03:00 (night charging peak)
        DG_requirement = 6.5-24.5 MW based on charger power
        ```
        
        #### 3. Economic Parameters
        ```python
        # From HOMER Grid Analysis
        solar_LCOE_reduction = 139.7%
        negative_LCOE_possible = -$0.103/kWh
        e_moto_savings = $700/year per operator
        infrastructure_cost = $50,000/station average
        ```
        
        #### 4. Adoption Barriers (Regression Analysis)
        ```python
        # Odds Ratios from survey (n=385)
        high_initial_cost = 1.98
        limited_charging = 1.77
        low_awareness = 1.63
        subsidy_effectiveness = 3.39
        tax_exemption_effect = 2.41
        ```
        """)

    # Interactive Data Simulation Demo
    st.subheader("Interactive Data Simulation")

    sim_col1, sim_col2, sim_col3 = st.columns(3)

    with sim_col1:
        data_quality = st.slider(
            "Data Quality Level",
            0, 100, 30,
            help="Percentage of real vs simulated data"
        )

    with sim_col2:
        update_freq = st.selectbox(
            "Update Frequency",
            ["Monthly", "Weekly", "Daily", "Real-time"],
            index=0
        )

    with sim_col3:
        geographic_cover = st.slider(
            "Geographic Coverage",
            1, 30, 4,
            help="Number of districts covered"
        )

    # Show simulation impact
    st.markdown("#### Impact of Improved Data")

    impact_col1, impact_col2, impact_col3 = st.columns(3)

    with impact_col1:
        st.metric(
            "Policy Accuracy",
            f"+{min(data_quality * 0.8, 80):.0f}%",
            "With real data"
        )

    with impact_col2:
        reduction = min(get_update_impact(update_freq), 90)
        st.metric(
            "Response Time",
            f"-{reduction:.0f}%",
            "Faster decisions"
        )

    with impact_col3:
        st.metric(
            "National Relevance",
            f"{geographic_cover}/30",
            "Districts covered"
        )

    # Partnership Engagement Form
    st.subheader("Partnership Interest")

    with st.form("partnership_form"):
        st.markdown("Interested in contributing data or partnering?")

        col1, col2 = st.columns(2)
        with col1:
            org_name = st.text_input("Organization Name")
            org_type = st.selectbox(
                "Organization Type",
                ["Government", "Private Sector", "Research",
                    "Development Partner", "Other"]
            )

        with col2:
            contact_email = st.text_input("Contact Email")
            data_type = st.multiselect(
                "Data Interest/Contribution",
                ["EV Registration", "Charging Infrastructure", "Grid Data",
                 "Economic Data", "Research Findings", "Policy Data"]
            )

        interest_level = st.slider("Interest Level", 1, 10, 5)
        comments = st.text_area("Additional Comments")

        submitted = st.form_submit_button("Express Interest")

        if submitted:
            st.success("Thank you for your interest! We'll contact you soon.")
            # In production, this would connect to a database
            st.info("*This is a demo. In production, this would trigger a workflow.*")

    # API & Integration Information
    st.subheader("Technical Integration")

    st.markdown("""
    ### Available Integration Methods
    
    #### 1. REST API (Preferred)
    ```python
    # Example: Submit charging station data
    POST /api/v1/charging-stations
    {
        "district": "Kigali",
        "latitude": -1.950,
        "longitude": 30.058,
        "type": "fast",
        "operator": "Private"
    }
    ```
    
    #### 2. File Upload
    - CSV/Excel templates provided
    - Automated validation
    - Batch processing
    
    #### 3. Database Connection
    - Secure VPN tunnel
    - Read-only access
    - Scheduled synchronization
    
    #### 4. Manual Entry Portal
    - Web interface for districts
    - Mobile data collection
    - Offline capability
    ```
    """)

    # Footer note
    st.markdown("---")
    st.info("""
    **Note on Data Privacy & Security:**
    - All sensitive data handled per Rwanda Data Protection Law
    - Aggregate/anonymized reporting only
    - Individual entity data never disclosed
    - Multi-level access controls implemented
    """)

# Add helper variable for update frequency factor
update_freq_factor = {
    "Monthly": 30,
    "Weekly": 70,
    "Daily": 90,
    "Real-time": 95
}

# Footer
st.markdown("---")

compact_footer = """
<div style="text-align: center; color: #888; font-size: 0.85em; padding: 0.8em 0; line-height: 1.4;">
    <strong>Evidence Base:</strong> Structured literature review... 
    (<a href="https://drive.google.com/file/d/119mnfhIQhNBXDodi6APYXlLK_oZXNVwb/view?usp=sharing" 
        style="color: #555; text-decoration: none;">full review PDF</a>) 
    • <strong>Data:</strong> Simulated (API-ready...) 
    • <strong>Methodology:</strong> 
      <a href="https://drive.google.com/file/d/1T8by63SyFyfnQiNiMGrr-GYpT1fd5R4n/view?usp=sharing" 
         style="color: #555; text-decoration: none;">Detailed methodology PDF</a> 
    • <strong>Version:</strong> 3.1 
    • <strong>Updated:</strong> December 2025 
    • <strong>Contact:</strong> 
      <a href="mailto:mutua@ndunda.com" style="color: #555; text-decoration: none;">mutua@ndunda.com</a>
    <style>
        div a { color: #555 !important; }
        div a:hover { text-decoration: underline !important; color: #0066cc !important; }
    </style>
</div>
"""

st.markdown(compact_footer, unsafe_allow_html=True)
