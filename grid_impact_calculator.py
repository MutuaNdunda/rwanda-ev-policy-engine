from typing import Dict

class GridImpactCalculator:
    def __init__(self):
        self.base_grid_capacity = 230.0
        self.peak_base_demand = 100.0
        
        # DG requirements from research
        self.dg_requirements = {
            '10kW': 6.5,  # MW
            '20kW': 24.5  # MW
        }
    
    def calculate_grid_impact(self, scenario_data: Dict) -> Dict:
        total_evs = scenario_data['total_evs']
        peak_share = scenario_data['peak_charging_share'] / 100
        
        # Simplified calculation
        if scenario_data.get('charger_types') == '10kW Focus':
            power = 7
        elif scenario_data.get('charger_types') == '20kW Focus':
            power = 12
        else:
            power = 10
        
        additional_demand = (total_evs * power * peak_share) / 1000 / 2  # Diversity factor
        total_demand = self.peak_base_demand + additional_demand
        
        # Cap utilization at 100% for display
        utilization = min((total_demand / self.base_grid_capacity) * 100, 100)
        
        # Calculate DG requirements
        dg_needed = self._calculate_dg_requirements(scenario_data, additional_demand)
        
        # Determine grid risk level
        grid_risk = self._determine_grid_risk_level(additional_demand)
        
        return {
            'additional_demand_mw': round(additional_demand, 2),
            'total_demand_mw': round(total_demand, 2),
            'grid_capacity_utilization': round(utilization, 1),
            'dg_capacity_needed': round(dg_needed, 2),  # ADDED THIS KEY
            'grid_risk_level': grid_risk,
            'is_grid_overloaded': total_demand > self.base_grid_capacity
        }
    
    def _calculate_dg_requirements(self, scenario_data: Dict, additional_demand: float) -> float:
        """Calculate DG capacity needed based on research"""
        
        charger_type = scenario_data.get('charger_types', 'Balanced')
        
        if charger_type == '10kW Focus':
            base_dg = self.dg_requirements['10kW']
        elif charger_type == '20kW Focus':
            base_dg = self.dg_requirements['20kW']
        else:
            base_dg = (self.dg_requirements['10kW'] + self.dg_requirements['20kW']) / 2
        
        # Scale based on additional demand
        scaling_factor = additional_demand / 25.0  # Normalize to research scenario
        
        return base_dg * scaling_factor
    
    def _determine_grid_risk_level(self, additional_demand: float) -> str:
        """Determine grid risk level"""
        
        if additional_demand > 50:
            return "High"
        elif additional_demand > 30:
            return "Medium"
        else:
            return "Low"