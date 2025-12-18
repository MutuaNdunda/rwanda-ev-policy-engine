import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from decision_engine import PolicyDecisionEngine
from grid_impact_calculator import GridImpactCalculator
from rwanda_context import RwandaEVContext
import json
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Rwanda EV Policy Simulator",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.title("Rwanda EV Policy Decision Engine & Scenario Simulator - Inspired by Mary Wa Strathmore")
st.markdown("""
*Supporting evidence-based policy decisions for Rwanda's electric vehicle transition aligned with national climate goals*
""")

# Sidebar for Navigation
with st.sidebar:
    st.markdown("## Navigation")
    selected_tab = st.radio(
        "Select Module:",
        ["Scenario Simulator", "Grid Impact Analysis", "Financial Modeling"]
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
                ["Private Cars", "E-Motos", "Buses", "Taxis", "Government Fleets", "Goods Delivery"],
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
                options=["10kW Focus", "Balanced", "20kW Focus", "Fast-Charge Heavy"],
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
        st.write(f"**Additional Demand:** {grid_analysis['additional_demand_mw']:.1f} MW")
        st.write(f"**DG Required:** {grid_analysis['dg_capacity_needed']:.1f} MW")
        
        # FIXED: Safe progress bar with cap at 1.0
        grid_utilization = grid_analysis['grid_capacity_utilization']
        progress_value = min(grid_utilization / 100, 1.0)
        
        if grid_utilization > 100:
            st.error(f"⚠️ Grid Overload: {grid_utilization:.1f}%")
            st.progress(1.0, text="CRITICAL: Grid overloaded")
        else:
            st.progress(progress_value, text=f"Grid Capacity: {grid_utilization:.1f}%")
        
        # Save Scenario
        if st.button("💾 Save Current Scenario", use_container_width=True):
            scenario_name = st.text_input("Scenario Name:", value=f"Scenario_{datetime.now().strftime('%Y%m%d_%H%M')}")
            if st.button("Confirm Save"):
                decision_engine.save_scenario(scenario_name, scenario_data, assessment)
                st.success(f"Scenario '{scenario_name}' saved!")
    
    # Main Results Area
    st.markdown("---")
    
    # Policy Recommendations Section
    st.subheader("Tailored Policy Recommendations")
    
    recommendations = decision_engine.generate_recommendations(scenario_data, assessment)
    
    # Categorize recommendations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Priority Actions", "⚡ Grid Management", "🏗️ Infrastructure", "💰 Financial"])
    
    with tab1:
        st.markdown("#### Immediate Priority Actions")
        priority_recs = [r for r in recommendations if r.get('priority') == 'High'][:5]
        
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
                    
                    st.caption(f"**Impact:** {impact} | **Stakeholders:** {stakeholders_str}")
                    
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
            st.info("No specific grid management recommendations for current scenario.")
    
    with tab3:
        st.markdown("#### Infrastructure Development")
        infra_recs = [r for r in recommendations if 'infrastructure' in r.get('category', '').lower()]
        
        if infra_recs:
            for rec in infra_recs:
                st.markdown(f"**{rec.get('title', 'Infrastructure Project')}**")
                st.write(rec.get('description', ''))
                st.caption(f"Category: {rec.get('category', 'Infrastructure')}")
                
                if rec.get('estimated_cost'):
                    st.metric("Estimated Cost", rec['estimated_cost'])
                
                st.markdown("---")
        else:
            st.info("No infrastructure-specific recommendations for current scenario.")
    
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
            st.dataframe(pd.DataFrame([scenario_data]).T.rename(columns={0: 'Value'}))
        
        with col2:
            st.markdown("##### Baseline (Current Policy)")
            st.dataframe(pd.DataFrame([baseline]).T.rename(columns={0: 'Value'}))
        
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
            ["Distributed Generation", "Smart Charging", "V2G Implementation", "Solar Microgrids"]
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
    total_evs = st.number_input("Total EVs", 1000, 300000, 50000, 5000, key="grid_total_evs")
    
    ev_penetration = st.slider("EV Penetration Rate (%)", 1, 30, 10, key="grid_penetration")
    charger_power = st.select_slider("Average Charger Power (kW)", [10, 15, 20, 50], value=20, key="grid_charger_power")
    dg_capacity = st.slider("DG Capacity Added (MW)", 0, 50, 10, key="grid_dg_capacity")
    peak_charging_share = st.slider("Peak Charging Share (%)", 10, 90, 50, key="grid_peak_share")
    
    # Calculate impacts
    base_demand = 100  # MW
    additional_demand = (total_evs * charger_power * peak_charging_share/100) / 1000
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
    
    tab1, tab2, tab3 = st.tabs(["Cost-Benefit Analysis", "Incentive Optimization", "PPP Structures"])
    
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
            | **Net Present Value** | **$180M** | 10-year horizon |
            """)
            
            # ROI Calculator
            st.markdown("#### Public Investment ROI Calculator")
            public_investment = st.number_input("Public Investment ($M)", 10, 500, 100, key="pub_investment")
            private_leverage = st.slider("Private Capital Leverage", 1.0, 5.0, 2.5, key="private_leverage")
            job_creation = st.slider("Jobs Created per $1M", 5, 50, 20, key="job_creation")
            
            total_investment = public_investment * (1 + private_leverage)
            total_jobs = public_investment * job_creation
            
            st.metric("Total Investment Mobilized", f"${total_investment:.1f}M")
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
        
        budget = st.slider("Annual Budget ($M)", 5, 100, 20, key="incentive_budget")
        
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
            estimated_ev_increase = int(total_effectiveness * 5000)  # Base effect
            
            st.metric("Combined Effectiveness Score", f"{total_effectiveness:.2f}")
            st.metric("Estimated Additional EV Adoption", f"{estimated_ev_increase:,}")
            st.metric("Cost per Additional EV", f"${budget*1e6/estimated_ev_increase:,.0f}")
    
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
            project_cost = st.number_input("Project Cost ($M)", 1, 500, 50, key="ppp_cost")
            concession_years = st.slider("Concession Period (years)", 5, 30, 15, key="concession_years")
        
        with col2:
            public_share = st.slider("Public Share (%)", 0, 100, 30, key="public_share")
            expected_roi = st.slider("Expected Private ROI (%)", 5, 25, 12, key="expected_roi")
        
        public_investment = project_cost * (public_share / 100)
        private_investment = project_cost - public_investment
        annual_revenue_needed = private_investment * (expected_roi / 100)
        
        st.metric("Public Investment", f"${public_investment:.1f}M")
        st.metric("Private Investment", f"${private_investment:.1f}M")
        st.metric("Required Annual Revenue", f"${annual_revenue_needed:.1f}M")

# Footer
st.markdown("---")
st.markdown("""
**Data Sources:** MININFRA, RURA, REG, National Institute of Statistics Rwanda, World Bank  
**Research Basis:** IPSA+ Grid Simulations, HOMER Economic Analysis, Regression Studies  
**Last Updated:** December 2023 | **Version:** 3.0 | **Contact:** mutua@ndunda.com""")