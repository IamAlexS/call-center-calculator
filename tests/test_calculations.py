import os
import sys

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import the model
from src.main import CallCenterModel  # Make sure main.py is lowercase

def test_basic_capacity():
    """Test that agents can't handle more than their capacity"""
    model = CallCenterModel(
        base_leads=1000,
        base_salespeople=1,
        max_leads_per_salesperson=100
    )
    
    results = model.calculate_metrics([2.0]).iloc[0]  # Use .iloc[0] instead of [0]
    assert results['handled_leads'] <= 100, "Agent shouldn't handle more than capacity"

def test_lead_prioritization():
    """Test that A leads are prioritized over B and C"""
    model = CallCenterModel(
        base_leads=1000,
        base_salespeople=1,
        max_leads_per_salesperson=100,
        lead_quality_distribution={
            'A': {'conversion_rate': 0.15, 'distribution': 0.20},
            'B': {'conversion_rate': 0.10, 'distribution': 0.30},
            'C': {'conversion_rate': 0.05, 'distribution': 0.50}
        }
    )
    
    # With limited capacity, should handle A leads first
    results = model.calculate_metrics([1.0]).iloc[0]  # Use .iloc[0]
    expected_a_leads = min(100, 1000 * 0.20)
    assert results['handled_leads'] == expected_a_leads, "Should prioritize A leads"

def test_tiered_pricing():
    """Test that lead costs increase correctly with volume"""
    model = CallCenterModel(
        base_leads=1000,
        lead_cost_tiers=[
            {'volume': 1000, 'cost': 40},
            {'volume': 2000, 'cost': 60}
        ]
    )
    
    # Test first tier
    cost_1000 = model.calculate_lead_cost(1000)
    assert cost_1000 == 1000 * 40, "First tier cost calculation incorrect"
    
    # Test mixed tiers
    cost_1500 = model.calculate_lead_cost(1500)
    expected_cost = (1000 * 40) + (500 * 60)
    assert cost_1500 == expected_cost, "Mixed tier cost calculation incorrect"

def test_investment_recommendation():
    """Test investment recommendation logic"""
    model = CallCenterModel(
        base_leads=1000,
        base_salespeople=5,
        max_leads_per_salesperson=100,  # Intentionally constrained
        salesperson_cost=4000,
        lead_cost_tiers=[{'volume': float('inf'), 'cost': 40}]  # Simple pricing
    )
    
    # When at capacity, should recommend more people
    recommendation = model.get_investment_recommendation(50000)
    assert recommendation['recommendation'] == 'people', "Should recommend people when at capacity"
    
    # With few leads, should recommend more leads
    model.base_leads = 100
    recommendation = model.get_investment_recommendation(50000)
    assert recommendation['recommendation'] == 'leads', "Should recommend leads when under capacity"

def test_edge_cases():
    """Test edge cases and potential issues"""
    model = CallCenterModel()
    
    # Test zero leads
    results = model.calculate_metrics([0]).iloc[0]  # Use .iloc[0]
    assert results['sales'] == 0, "Zero leads should result in zero sales"
    
    # Test very large numbers
    results = model.calculate_metrics([1000]).iloc[0]  # Use .iloc[0]
    assert results['sales'] >= 0, "Sales should not be negative"
    assert results['cost_per_sale'] > 0, "Cost per sale should be positive"

def test_step_by_step_calculations():
    """Test each step of the calculation process with simple numbers"""
    model = CallCenterModel(
        base_leads=100,              
        base_salespeople=1,          
        max_leads_per_salesperson=50,
        salesperson_cost=4000,       
        lead_quality_distribution={
            'A': {'conversion_rate': 0.20, 'distribution': 0.50},
            'B': {'conversion_rate': 0.10, 'distribution': 0.50}
        },
        lead_cost_tiers=[
            {'volume': float('inf'), 'cost': 40}
        ]
    )

    # Step 1: Test lead distribution
    total_leads = 100
    leads_by_quality = {
        tier: total_leads * dist['distribution']
        for tier, dist in model.lead_quality_distribution.items()
    }
    assert leads_by_quality['A'] == 50, "Should have 50 A leads"
    assert leads_by_quality['B'] == 50, "Should have 50 B leads"

    # Step 2: Test capacity calculation
    total_capacity = model.base_salespeople * model.max_leads_per_salesperson
    assert total_capacity == 50, "One agent should handle 50 leads"

    # Step 3: Test lead handling prioritization
    handled_a_leads = min(leads_by_quality['A'], total_capacity)
    assert handled_a_leads == 50, "Should handle all A leads up to capacity"
    
    remaining_capacity = total_capacity - handled_a_leads
    assert remaining_capacity == 0, "No capacity left for B leads"

    # Step 4: Test conversion calculations
    a_conversions = handled_a_leads * model.lead_quality_distribution['A']['conversion_rate']
    assert a_conversions == 10, "50 A leads * 20% conversion = 10 sales"

    # Step 5: Test cost calculations
    lead_cost = model.calculate_lead_cost(total_leads)
    assert lead_cost == 100 * 40, "100 leads at $40 each = $4000"
    
    total_cost = lead_cost + (model.salesperson_cost * model.base_salespeople)
    assert total_cost == 4000 + 4000, "Lead cost + 1 agent cost"

    # Step 6: Test investment scenarios
    investment = 4000
    
    # Scenario A: More Leads
    additional_leads_possible = investment // 40  # $4000 / $40 per lead
    assert additional_leads_possible == 100, "Should be able to buy 100 more leads"
    
    # But still limited by capacity
    new_handled_leads = min(total_capacity, total_leads + additional_leads_possible)
    assert new_handled_leads == 50, "Still limited by agent capacity"

    # Scenario B: More Agents
    additional_agents = investment // model.salesperson_cost
    assert additional_agents == 1, "Should be able to hire 1 more agent"
    
    new_capacity = (model.base_salespeople + additional_agents) * model.max_leads_per_salesperson
    assert new_capacity == 100, "Two agents should handle 100 leads"

    # Step 7: Test ROI calculations with clearer math
    # Current state (base case):
    # - Can handle 50 leads (capacity limited)
    # - All 50 are A leads (prioritized)
    # - 50 * 20% conversion = 10 sales
    base_sales = a_conversions  # 10 sales
    
    # Scenario A - More Leads ($4000 investment):
    # - Still capacity limited at 50 leads
    # - Still 10 sales
    # - ROI = (10 - 10) / 4000 = 0
    leads_roi = (base_sales - base_sales) / investment
    assert leads_roi == 0, "No improvement when capacity limited"
    
    # Scenario B - More Agents ($4000 investment):
    # - New capacity = 100 leads
    # - Can handle all leads: 50 A leads and 50 B leads
    # - A leads: 50 * 20% = 10 sales
    # - B leads: 50 * 10% = 5 sales
    # - Total sales = 15
    # - ROI = (15 - 10) / 4000 = 0.00125
    agent_sales = (50 * 0.20) + (50 * 0.10)  # 15 sales total
    agent_roi = (agent_sales - base_sales) / investment
    expected_roi = (15 - 10) / 4000  # 5 additional sales for $4000 = 0.00125
    
    assert abs(agent_roi - expected_roi) < 0.0001, "Agent ROI calculation incorrect"

    # Final recommendation
    recommendation = model.get_investment_recommendation(investment)
    assert recommendation['recommendation'] == 'people', "Should recommend people when at capacity"
    
def test_cac_limits():
    """Test that CAC limits affect recommendations"""
    model = CallCenterModel(
        base_leads=1000,
        base_salespeople=10,
        max_leads_per_salesperson=150,
        salesperson_cost=4000,
        max_cac=500,  # Set strict CAC limit
        lead_cost_tiers=[{'volume': float('inf'), 'cost': 40}]
    )
    
    # Test when current CAC is too high
    recommendation = model.get_investment_recommendation(50000)
    assert recommendation['recommendation'] == 'optimize_costs', "Should recommend optimization when CAC too high"
    
    # Test when investment would exceed CAC limit
    model.max_cac = 1000  # More reasonable CAC limit
    model.lead_cost_tiers = [{'volume': float('inf'), 'cost': 100}]  # Expensive leads
    recommendation = model.get_investment_recommendation(50000)
    assert recommendation['recommendation'] == 'do_nothing', "Should recommend doing nothing when no good options"
    