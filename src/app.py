import streamlit as st
from main import CallCenterModel
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Call Center Investment Calculator", layout="wide")

def main():
    st.title("📞 Call Center Investment Calculator")
    
    # Basic Settings
    st.sidebar.header("Basic Settings")
    base_leads = st.sidebar.number_input("Current Monthly Leads", value=7300)
    base_salespeople = st.sidebar.number_input("Current Number of Agents", value=5)
    salesperson_cost = st.sidebar.number_input("Monthly Cost per Agent ($)", value=11000)
    max_cac = st.sidebar.number_input("Maximum Acceptable CAC ($)", value=400)
    max_leads_per_agent = st.sidebar.number_input("Maximum Leads per Agent", value=600)

    # Lead Quality Distribution
    st.sidebar.header("Lead Quality Distribution")
    cols = st.sidebar.columns(3)
    
    # Headers
    cols[0].markdown("**Tier**")
    cols[1].markdown("**Conv %**")
    cols[2].markdown("**Dist %**")
    
    # Values (divide by 100 to convert percentage to decimal)
    a_conv = cols[1].number_input("A", value=20, key="a_conv") / 100
    b_conv = cols[1].number_input("B", value=4, key="b_conv") / 100
    c_conv = cols[1].number_input("C", value=2, key="c_conv") / 100
    
    a_dist = cols[2].number_input("A", value=20, key="a_dist") / 100
    b_dist = cols[2].number_input("B", value=30, key="b_dist") / 100
    c_dist = cols[2].number_input("C", value=50, key="c_dist") / 100
    
    # Display tiers in first column (static)
    cols[0].markdown("A (High)")
    cols[0].markdown("B (Med)")
    cols[0].markdown("C (Low)")

    # Lead Cost Tiers
    st.sidebar.header("Lead Cost Tiers")
    st.sidebar.markdown("📊 Enter total volume thresholds and costs per lead")
    
    cost_tiers = []
    for i in range(4):
        col1, col2 = st.sidebar.columns(2)
        volume = col1.number_input(
            f"Up to leads", 
            value=7300*(2**i), 
            key=f"v{i}"
        )
        cost = col2.number_input(
            f"Cost/lead ($)", 
            value=7+(3*i), 
            key=f"c{i}"
        )
        
        # Simple range display
        if i > 0:
            prev_volume = cost_tiers[i-1]['volume']
            st.sidebar.caption(f"${cost} per lead from {prev_volume:,} to {volume:,}")
        else:
            st.sidebar.caption(f"${cost} per lead from 0 to {volume:,}")
            
        cost_tiers.append({'volume': volume, 'cost': cost})

    # Investment Analysis
    st.header("Investment Analysis")
    investment_amount = st.number_input("Investment Amount ($)", value=12000)

    # Create model with decimal values
    model = CallCenterModel(
        base_leads=base_leads,
        base_salespeople=base_salespeople,
        max_leads_per_salesperson=max_leads_per_agent,
        salesperson_cost=salesperson_cost,
        max_cac=max_cac,
        lead_quality_distribution={
            'A': {'conversion_rate': a_conv, 'distribution': a_dist},  # Now in decimals
            'B': {'conversion_rate': b_conv, 'distribution': b_dist},  # e.g., 0.06 instead of 6
            'C': {'conversion_rate': c_conv, 'distribution': c_dist}
        },
        lead_cost_tiers=cost_tiers
    )

    recommendation = model.get_investment_recommendation(investment_amount)
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incremental Sales Comparison")
        comparison_df = pd.DataFrame({
            'Investment Type': ['More Leads', 'More Agents'],
            'Additional Sales': [
                recommendation['leads_incremental'],
                recommendation['people_incremental']
            ]
        })
        
        fig = px.bar(comparison_df, 
                    x='Investment Type', 
                    y='Additional Sales',
                    text=comparison_df['Additional Sales'].apply(lambda x: f'{x:.0f}'))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig)

    with col2:
        st.subheader("Recommendation")
        st.markdown(f"""
        💡 **Recommendation: {recommendation['recommendation'].upper().replace('_', ' ')}**
        
        Reason: {recommendation['reason']}
        
        Current metrics:
        - CAC: ${recommendation['current_cac']:.2f}
        - Sales: {recommendation['base_metrics']['sales']:.0f}
        
        Potential outcomes:
        - Leads scenario CAC: ${recommendation['leads_cac']:.2f}
        - People scenario CAC: ${recommendation['people_cac']:.2f}
        """)

    if st.checkbox("Show detailed metrics"):
        metrics_df = model.calculate_metrics(investment_amount=investment_amount)
        
        # Define columns for detailed view
        columns = [
            'scenario', 
            'sales',
            'total_cac',     # Total CAC
            'lead_cac',      # Lead portion of CAC
            'agent_cac',     # Agent portion of CAC
            'handled_leads', 
            'total_leads', 
            'total_cost', 
            'lead_cost', 
            'agent_cost'
        ]
        
        number_format = {
            'sales': '{:.0f}',
            'total_cac': '${:.2f}',
            'lead_cac': '${:.2f}',
            'agent_cac': '${:.2f}',
            'handled_leads': '{:.0f}',
            'total_leads': '{:.0f}',
            'total_cost': '${:.0f}',
            'lead_cost': '${:.0f}',
            'agent_cost': '${:.0f}'
        }
        
        # Split and display scenarios
        lead_scenarios = metrics_df[metrics_df['scenario'].str.contains('leads')]
        agent_scenarios = metrics_df[metrics_df['scenario'].str.contains('agent')]
        
        st.subheader("Lead Scenarios")
        st.dataframe(lead_scenarios[columns].style.format(number_format))
        
        st.subheader("Agent Scenarios")
        st.dataframe(agent_scenarios[columns].style.format(number_format))

if __name__ == "__main__":
    main() 