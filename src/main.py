# Import required libraries
import numpy as np
import pandas as pd

class CallCenterModel:
    def __init__(self, 
                 base_leads=1000,           
                 base_salespeople=10,        
                 max_leads_per_salesperson=150, 
                 salesperson_cost=4000,     
                 max_cac=1000,  # Add CAC limit
                 lead_quality_distribution={  
                     'A': {
                         'conversion_rate': 0.15,  
                         'distribution': 0.20,     
                     },
                     'B': {
                         'conversion_rate': 0.10,
                         'distribution': 0.30,
                     },
                     'C': {
                         'conversion_rate': 0.05,
                         'distribution': 0.50,
                     }
                 },
                 lead_cost_tiers=[          
                     {'volume': 1000, 'cost': 40},    
                     {'volume': 2000, 'cost': 52},    
                     {'volume': 5000, 'cost': 64},    
                     {'volume': float('inf'), 'cost': 80}  
                 ]):
        self.base_leads = base_leads
        self.base_salespeople = base_salespeople
        self.max_leads_per_salesperson = max_leads_per_salesperson
        self.salesperson_cost = salesperson_cost
        self.max_cac = max_cac  # Store CAC limit
        self.lead_quality_distribution = lead_quality_distribution
        self.lead_cost_tiers = lead_cost_tiers

    def calculate_lead_cost(self, total_leads):
        """Calculate total cost for a given number of leads using tiered pricing"""
        total_cost = 0
        remaining_leads = total_leads
        
        for tier in self.lead_cost_tiers:
            if remaining_leads <= 0:
                break
                
            # Calculate leads in this tier
            prev_volume = 0 if self.lead_cost_tiers.index(tier) == 0 else self.lead_cost_tiers[self.lead_cost_tiers.index(tier)-1]['volume']
            tier_volume = tier['volume'] - prev_volume
            leads_in_tier = min(remaining_leads, tier_volume)
            
            # Add cost for this tier
            total_cost += leads_in_tier * tier['cost']
            remaining_leads -= leads_in_tier
            
        return total_cost

    def calculate_metrics(self, lead_multipliers=None, investment_amount=None):
        results = []
        
        # Lead scenarios
        multipliers_to_use = lead_multipliers if lead_multipliers is not None else np.arange(1.0, 2.1, 0.1)
        for multiplier in multipliers_to_use:
            total_leads = self.base_leads * multiplier
            max_capacity = self.base_salespeople * self.max_leads_per_salesperson
            
            leads_by_quality = {
                tier: {
                    'total': total_leads * dist['distribution'],
                    'conversion': dist['conversion_rate']
                }
                for tier, dist in self.lead_quality_distribution.items()
            }
            
            remaining_capacity = max_capacity
            handled_leads = 0
            total_conversions = 0
            
            for tier in ['A', 'B', 'C']:
                tier_leads = leads_by_quality[tier]['total']
                leads_handled = min(remaining_capacity, tier_leads)
                handled_leads += leads_handled
                total_conversions += leads_handled * leads_by_quality[tier]['conversion']
                remaining_capacity -= leads_handled
                if remaining_capacity <= 0:
                    break
            
            lead_cost = self.calculate_lead_cost(total_leads)
            total_cost = lead_cost + (self.salesperson_cost * self.base_salespeople)
            cost_per_sale = total_cost / total_conversions if total_conversions > 0 else float('inf')
            
            # Calculate separate CACs for detailed view only
            lead_cac = lead_cost / total_conversions if total_conversions > 0 else float('inf')
            agent_cac = (self.salesperson_cost * self.base_salespeople) / total_conversions if total_conversions > 0 else float('inf')
            
            results.append({
                'scenario': f"{multiplier:.1f}x leads",
                'sales': total_conversions,
                'total_cac': cost_per_sale,    # Renamed for clarity
                'lead_cac': lead_cac,
                'agent_cac': agent_cac,
                'handled_leads': handled_leads,
                'total_leads': total_leads,
                'total_cost': total_cost,
                'lead_cost': lead_cost,
                'agent_cost': self.salesperson_cost * self.base_salespeople
            })
        
        # Agent scenarios
        original_salespeople = self.base_salespeople
        for additional_agents in range(1, 4):
            new_total = original_salespeople + additional_agents
            self.base_salespeople = new_total
            
            total_leads = self.base_leads
            max_capacity = self.base_salespeople * self.max_leads_per_salesperson
            
            leads_by_quality = {
                tier: {
                    'total': total_leads * dist['distribution'],
                    'conversion': dist['conversion_rate']
                }
                for tier, dist in self.lead_quality_distribution.items()
            }
            
            remaining_capacity = max_capacity
            handled_leads = 0
            total_conversions = 0
            
            for tier in ['A', 'B', 'C']:
                tier_leads = leads_by_quality[tier]['total']
                leads_handled = min(remaining_capacity, tier_leads)
                handled_leads += leads_handled
                total_conversions += leads_handled * leads_by_quality[tier]['conversion']
                remaining_capacity -= leads_handled
                if remaining_capacity <= 0:
                    break
            
            lead_cost = self.calculate_lead_cost(total_leads)
            agent_cost = self.salesperson_cost * self.base_salespeople
            total_cost = lead_cost + agent_cost
            cost_per_sale = total_cost / total_conversions if total_conversions > 0 else float('inf')
            
            # Calculate separate CACs for detailed view only
            lead_cac = lead_cost / total_conversions if total_conversions > 0 else float('inf')
            agent_cac = (self.salesperson_cost * self.base_salespeople) / total_conversions if total_conversions > 0 else float('inf')
            
            results.append({
                'scenario': f"+{additional_agents} agent{'s' if additional_agents > 1 else ''}",
                'sales': total_conversions,
                'total_cac': cost_per_sale,    # Renamed for clarity
                'lead_cac': lead_cac,
                'agent_cac': agent_cac,
                'handled_leads': handled_leads,
                'total_leads': total_leads,
                'total_cost': total_cost,
                'lead_cost': lead_cost,
                'agent_cost': agent_cost
            })
        
        self.base_salespeople = original_salespeople
        return pd.DataFrame(results)

    def get_investment_recommendation(self, investment_amount):
        """Analyze whether to invest in more leads, more salespeople, or nothing"""
        # Calculate baseline metrics
        base_metrics = self.calculate_metrics([1.0]).iloc[0]
        current_cac = base_metrics['total_cac']
        
        # Calculate how many whole agents we can hire
        additional_agents = investment_amount // self.salesperson_cost
        
        # Calculate leads scenario
        additional_leads_possible = investment_amount / self.calculate_lead_cost(1)  # How many leads we can buy
        lead_multiplier = (self.base_leads + additional_leads_possible) / self.base_leads
        leads_metrics = self.calculate_metrics([lead_multiplier]).iloc[0]
        leads_cac = leads_metrics['total_cac']
        
        # Calculate people scenario
        if additional_agents > 0:
            original_salespeople = self.base_salespeople
            self.base_salespeople += additional_agents
            people_metrics = self.calculate_metrics([1.0]).iloc[0]
            self.base_salespeople = original_salespeople  # Reset back
            people_cac = people_metrics['total_cac']
        else:
            people_metrics = base_metrics
            people_cac = current_cac
        
        # Determine recommendation based on CAC and incremental sales
        leads_incremental = leads_metrics['sales'] - base_metrics['sales'] if leads_cac <= self.max_cac else 0
        people_incremental = people_metrics['sales'] - base_metrics['sales'] if people_cac <= self.max_cac else 0
        
        if max(leads_incremental, people_incremental) <= 0:
            recommendation = 'do_nothing'
            reason = 'No investment scenario meets CAC requirements'
        else:
            recommendation = 'people' if people_incremental > leads_incremental else 'leads'
            reason = f'Best incremental sales achieved by investing in {recommendation}'
        
        return {
            'recommendation': recommendation,
            'reason': reason,
            'current_cac': current_cac,
            'leads_cac': leads_cac,
            'people_cac': people_cac,
            'base_metrics': base_metrics,
            'leads_metrics': leads_metrics,
            'people_metrics': people_metrics,
            'leads_incremental': leads_incremental,
            'people_incremental': people_incremental
        }

def main():
    # Create model with default parameters
    model = CallCenterModel()
    
    # Calculate results
    results = model.calculate_metrics()
    
    # Print optimal points
    optimal_sales = results.loc[results['sales'].idxmax()]
    optimal_cost = results.loc[results['cost_per_sale'].idxmin()]
    
    print("\nOptimal Points:")
    print(f"Maximum Sales at multiplier: {optimal_sales['lead_multiplier']:.1f}")
    print(f"- Sales: {optimal_sales['sales']:.0f}")
    print(f"- Cost per Sale: ${optimal_sales['cost_per_sale']:.2f}")
    print(f"\nMinimum Cost per Sale at multiplier: {optimal_cost['lead_multiplier']:.1f}")
    print(f"- Sales: {optimal_cost['sales']:.0f}")
    print(f"- Cost per Sale: ${optimal_cost['cost_per_sale']:.2f}")
    
    # Get investment recommendation
    investment = 50000  # Example investment amount
    recommendation = model.get_investment_recommendation(investment)
    
    print(f"\nInvestment Recommendation for ${investment:,}:")
    print(f"ROI from investing in leads: {recommendation['leads_incremental'] / investment:.2%}")
    print(f"ROI from investing in people: {recommendation['people_incremental'] / investment:.2%}")
    print(f"Recommendation: Invest in {recommendation['recommendation']}")

if __name__ == "__main__":
    main()