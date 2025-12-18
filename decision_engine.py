from typing import Dict, List, Any, Tuple
import json
from datetime import datetime, timedelta

class PolicyDecisionEngine:
    def __init__(self, context):
        self.context = context
        self.scenarios = []
    
    def assess_scenario(self, scenario_data: Dict) -> Dict:
        """Comprehensive scenario assessment with sensitivity"""
        
        # Calculate key metrics with more granularity
        ev_to_charger = scenario_data['total_evs'] / max(scenario_data['public_chargers'], 1)
        
        # Infrastructure pressure with 5 levels
        if ev_to_charger > 200:
            infra_pressure = "Critical"
            infra_score = 1.0
        elif ev_to_charger > 150:
            infra_pressure = "High"
            infra_score = 0.8
        elif ev_to_charger > 100:
            infra_pressure = "Medium-High"
            infra_score = 0.6
        elif ev_to_charger > 50:
            infra_pressure = "Medium"
            infra_score = 0.4
        else:
            infra_pressure = "Low"
            infra_score = 0.2
        
        # Grid risk with sensitivity to multiple factors
        grid_score = 0
        
        # Base score from peak charging
        if scenario_data['peak_charging_share'] > 70:
            grid_score += 0.4
        elif scenario_data['peak_charging_share'] > 50:
            grid_score += 0.3
        elif scenario_data['peak_charging_share'] > 30:
            grid_score += 0.2
        else:
            grid_score += 0.1
        
        # Adjust based on charger type
        charger_type = scenario_data.get('charger_types', 'Balanced')
        if charger_type == '20kW Focus':
            grid_score += 0.2
        elif charger_type == 'Fast-Charge Heavy':
            grid_score += 0.3
        
        # Adjust based on V2G adoption
        v2g_adoption = scenario_data.get('v2g_adoption', 20)
        grid_score -= (v2g_adoption / 100) * 0.2  # V2G reduces grid risk
        
        # Adjust based on solar integration
        solar_integration = scenario_data.get('solar_integration', 30)
        grid_score -= (solar_integration / 100) * 0.15  # Solar reduces grid risk
        
        # Determine grid risk level
        if grid_score > 0.6:
            grid_risk = "Critical"
        elif grid_score > 0.45:
            grid_risk = "High"
        elif grid_score > 0.3:
            grid_risk = "Medium-High"
        elif grid_score > 0.15:
            grid_risk = "Medium"
        else:
            grid_risk = "Low"
        
        # Financial viability with investment-regulatory matrix
        investment_map = {
            "Conservative": 0.2,
            "Moderate": 0.5,
            "Aggressive": 0.7,
            "Transformative": 0.9
        }
        
        regulatory_map = {
            "Traditional": 0.2,
            "Adaptive": 0.5,
            "Innovation-Friendly": 0.7,
            "Sandbox Approach": 0.9
        }
        
        investment_score = investment_map.get(scenario_data.get('investment_appetite', 'Moderate'), 0.5)
        regulatory_score = regulatory_map.get(scenario_data.get('regulatory_flexibility', 'Adaptive'), 0.5)
        
        financial_score = (investment_score + regulatory_score) / 2
        
        if financial_score > 0.7:
            financial_viability = "Excellent"
        elif financial_score > 0.5:
            financial_viability = "Good"
        elif financial_score > 0.3:
            financial_viability = "Moderate"
        else:
            financial_viability = "Poor"
        
        # Social acceptance score
        social_score = 0.5  # Base
        
        # Higher two-wheeler share improves acceptance (familiar technology)
        if scenario_data['two_wheeler_share'] > 60:
            social_score += 0.2
        elif scenario_data['two_wheeler_share'] > 40:
            social_score += 0.1
        
        # Solar integration improves public perception
        social_score += (scenario_data.get('solar_integration', 30) / 100) * 0.15
        
        if social_score > 0.7:
            social_acceptance = "High"
        elif social_score > 0.5:
            social_acceptance = "Medium"
        else:
            social_acceptance = "Low"
        
        return {
            'infrastructure_pressure': infra_pressure,
            'infrastructure_score': infra_score,
            'grid_risk': grid_risk,
            'grid_score': grid_score,
            'financial_viability': financial_viability,
            'financial_score': financial_score,
            'social_acceptance': social_acceptance,
            'social_score': social_score,
            'ev_to_charger_ratio': round(ev_to_charger, 1),
            'urgency_level': self._calculate_urgency(infra_score, grid_score),
            'recommendation_priority': self._calculate_priority(scenario_data)
        }
    
    def _calculate_urgency(self, infra_score: float, grid_score: float) -> str:
        """Calculate overall urgency level"""
        max_score = max(infra_score, grid_score)
        
        if max_score > 0.8:
            return "Immediate"
        elif max_score > 0.6:
            return "Urgent"
        elif max_score > 0.4:
            return "High Priority"
        elif max_score > 0.2:
            return "Medium Priority"
        else:
            return "Low Priority"
    
    def _calculate_priority(self, scenario_data: Dict) -> str:
        """Calculate which aspect needs most attention"""
        scores = {
            'infrastructure': scenario_data['total_evs'] / max(scenario_data['public_chargers'], 1) / 200,
            'grid': scenario_data['peak_charging_share'] / 100,
            'finance': 0.5 if scenario_data.get('investment_appetite') in ['Conservative', 'Moderate'] else 0.8,
            'social': (100 - scenario_data['two_wheeler_share']) / 100  # Lower two-wheeler = higher social barrier
        }
        
        return max(scores, key=scores.get)
    
    def generate_recommendations(self, scenario_data: Dict, assessment: Dict) -> List[Dict]:
        """Generate dynamic, sensitive recommendations based on inputs"""
        recommendations = []
        
        # Get stakeholder for tailoring
        stakeholder = scenario_data.get('stakeholder', '')
        policy_priority = scenario_data.get('policy_priority', 'Balanced Growth')
        urgency = assessment.get('urgency_level', 'Medium Priority')
        
        # ===== INFRASTRUCTURE RECOMMENDATIONS =====
        infra_pressure = assessment['infrastructure_pressure']
        ev_to_charger = assessment['ev_to_charger_ratio']
        
        if infra_pressure in ["Critical", "High"]:
            # Dynamic infrastructure recommendation based on severity
            if ev_to_charger > 200:
                title = "EMERGENCY: Massive Infrastructure Deployment Required"
                description = f"Critical infrastructure gap with {ev_to_charger}:1 EV-to-charger ratio. Requires immediate deployment of {scenario_data['total_evs']//50} new charging stations."
                timeframe = "3-6 months"
                priority = "Critical"
                estimated_cost = f"${scenario_data['total_evs'] * 1500:,.0f}"
            elif ev_to_charger > 150:
                title = "Accelerate Charging Infrastructure Rollout"
                description = f"High pressure with {ev_to_charger}:1 ratio. Target deployment of {scenario_data['total_evs']//80} new stations."
                timeframe = "6-12 months"
                priority = "High"
                estimated_cost = f"${scenario_data['total_evs'] * 1200:,.0f}"
            else:
                title = "Expand Charging Network"
                description = f"Moderate pressure with {ev_to_charger}:1 ratio. Plan for {scenario_data['total_evs']//100} new stations."
                timeframe = "12-18 months"
                priority = "Medium"
                estimated_cost = f"${scenario_data['total_evs'] * 1000:,.0f}"
            
            recommendations.append({
                'title': title,
                'description': description,
                'timeframe': timeframe,
                'impact': 'High',
                'category': 'Infrastructure',
                'priority': priority,
                'stakeholders': ['MININFRA', 'RURA', 'City of Kigali'],
                'estimated_cost': estimated_cost,
                'kpi': f'Reduce EV-to-charger ratio to 50:1 (Current: {ev_to_charger}:1)',
                'actions': self._get_infrastructure_actions(scenario_data, infra_pressure)
            })
        
        # ===== GRID MANAGEMENT RECOMMENDATIONS =====
        grid_risk = assessment['grid_risk']
        peak_share = scenario_data['peak_charging_share']
        
        if grid_risk in ["Critical", "High", "Medium-High"]:
            # Dynamic grid recommendation based on risk level
            if peak_share > 70:
                title = "CRITICAL: Immediate Grid Protection Measures"
                description = f"Extreme peak charging ({peak_share}%) risks grid failure. Implement emergency measures."
                timeframe = "1-3 months"
                mitigation = "Mandatory off-peak charging, emergency DG deployment"
            elif peak_share > 50:
                title = "Implement Smart Grid Solutions"
                description = f"High peak charging ({peak_share}%) requires advanced grid management."
                timeframe = "3-9 months"
                mitigation = "Time-of-Use tariffs, smart charging, V2G programs"
            else:
                title = "Proactive Grid Planning"
                description = f"Moderate peak charging ({peak_share}%) allows for planned upgrades."
                timeframe = "9-18 months"
                mitigation = "Grid reinforcement, distributed generation planning"
            
            # Adjust based on charger type
            charger_type = scenario_data.get('charger_types', 'Balanced')
            if charger_type == '20kW Focus' or charger_type == 'Fast-Charge Heavy':
                description += f" Aggravated by {charger_type} strategy."
                mitigation += ", consider charger power management"
            
            recommendations.append({
                'title': title,
                'description': description,
                'timeframe': timeframe,
                'impact': 'High' if peak_share > 50 else 'Medium',
                'category': 'Grid Management',
                'priority': 'High' if grid_risk in ["Critical", "High"] else 'Medium',
                'stakeholders': ['REG', 'RURA', 'MININFRA'],
                'estimated_cost': '$5-15M' if peak_share > 50 else '$2-8M',
                'kpi': f'Reduce peak charging to <40% (Current: {peak_share}%)',
                'mitigation_strategy': mitigation
            })
        
        # ===== TWO-WHEELER SPECIFIC RECOMMENDATIONS =====
        two_wheeler_share = scenario_data['two_wheeler_share']
        
        if two_wheeler_share > 60:
            title = "E-Moto Priority Strategy"
            description = f"Dominant two-wheeler share ({two_wheeler_share}%) requires specialized infrastructure focus."
            actions = [
                "Deploy high-density e-moto charging hubs",
                "Standardize battery swapping systems",
                "Develop e-moto dedicated lanes"
            ]
        elif two_wheeler_share > 40:
            title = "Integrated Two-Wheeler Planning"
            description = f"Significant two-wheeler share ({two_wheeler_share}%) needs balanced approach."
            actions = [
                "Mixed-use charging stations",
                "E-moto purchase subsidies",
                "Operator training programs"
            ]
        else:
            title = "Mainstream EV Focus"
            description = f"Lower two-wheeler share ({two_wheeler_share}%) allows focus on car infrastructure."
            actions = [
                "Standard car charging networks",
                "Public charging corridors",
                "Fleet electrification programs"
            ]
        
        recommendations.append({
            'title': title,
            'description': description,
            'timeframe': '6-24 months',
            'impact': 'High' if two_wheeler_share > 60 else 'Medium',
            'category': 'Fleet Strategy',
            'priority': 'High' if two_wheeler_share > 60 else 'Medium',
            'stakeholders': ['City of Kigali', 'RDB', 'Private Sector'],
            'estimated_cost': f"${scenario_data['total_evs'] * 200 * (two_wheeler_share/100):,.0f}",
            'kpi': f'Optimize infrastructure for {two_wheeler_share}% two-wheeler fleet',
            'actions': actions
        })
        
        # ===== POLICY PRIORITY RECOMMENDATIONS =====
        if policy_priority == 'Climate Impact Maximization':
            solar = scenario_data.get('solar_integration', 30)
            rec = {
                'title': 'Renewable Charging Strategy',
                'description': f'Align with climate goals. Current solar integration: {solar}%.',
                'timeframe': '12-36 months',
                'impact': 'High' if solar < 50 else 'Medium',
                'category': 'Climate & Environment',
                'priority': 'High' if solar < 30 else 'Medium',
                'stakeholders': ['REMA', 'REG', 'MININFRA'],
                'estimated_cost': f"${scenario_data['total_evs'] * 300:,.0f}",
                'kpi': f'Achieve {max(50, solar + 20)}% renewable charging by 2030'
            }
            
            if solar < 30:
                rec['actions'] = ['Solar mandate for new stations', 'Renewable energy credits', 'Green financing']
            else:
                rec['actions'] = ['Scale successful models', 'Grid integration of renewables', 'Carbon tracking']
            
            recommendations.append(rec)
        
        elif policy_priority == 'Grid Stability & Resilience':
            recommendations.append({
                'title': 'Grid Resilience Framework',
                'description': 'Prioritize grid stability in EV integration planning.',
                'timeframe': '6-18 months',
                'impact': 'High',
                'category': 'Grid Infrastructure',
                'priority': 'High',
                'stakeholders': ['REG', 'RURA', 'MININFRA'],
                'estimated_cost': '$10-25M',
                'kpi': 'Maintain grid stability at 100,000+ EVs',
                'actions': ['Advanced grid monitoring', 'Resilience standards', 'Backup power systems']
            })
        
        # ===== FINANCIAL RECOMMENDATIONS =====
        investment_appetite = scenario_data.get('investment_appetite', 'Moderate')
        regulatory_flexibility = scenario_data.get('regulatory_flexibility', 'Adaptive')
        
        if investment_appetite in ['Aggressive', 'Transformative'] and regulatory_flexibility in ['Innovation-Friendly', 'Sandbox Approach']:
            recommendations.append({
                'title': 'Advanced PPP Framework',
                'description': f'High investment appetite ({investment_appetite}) with flexible regulation ({regulatory_flexibility}) enables innovative partnerships.',
                'timeframe': '6-24 months',
                'impact': 'High',
                'category': 'Financial',
                'priority': 'High',
                'stakeholders': ['MINECOFIN', 'RDB', 'Private Sector'],
                'estimated_cost': 'PPP (Public: $10-50M, Private: 3-5x leverage)',
                'kpi': f'Attract ${scenario_data["total_evs"] * 100:,.0f} private investment',
                'roi': '12-20%'
            })
        
        # ===== STAKEHOLDER-SPECIFIC RECOMMENDATIONS =====
        stakeholder_recs = self._get_stakeholder_recommendations(stakeholder, scenario_data, assessment)
        recommendations.extend(stakeholder_recs)
        
        # ===== URGENCY-BASED RECOMMENDATIONS =====
        if urgency in ["Immediate", "Urgent"]:
            recommendations.append({
                'title': 'Rapid Response Team',
                'description': f'{urgency} situation detected. Establish cross-functional team.',
                'timeframe': '1 month',
                'impact': 'High',
                'category': 'Governance',
                'priority': 'Critical',
                'stakeholders': ['All relevant agencies'],
                'estimated_cost': 'Minimal',
                'kpi': 'Weekly progress monitoring',
                'actions': ['Immediate stakeholder coordination', 'Emergency funding access', 'Fast-track approvals']
            })
        
        # Sort by priority
        priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 0), reverse=True)
        
        return recommendations
    
    def _get_infrastructure_actions(self, scenario_data: Dict, pressure_level: str) -> List[str]:
        """Get specific infrastructure actions based on pressure"""
        actions = []
        
        if pressure_level == "Critical":
            actions = [
                "Emergency permitting for charging stations",
                "Temporary mobile charging solutions",
                "Priority grid connections",
                "Public land allocation"
            ]
        elif pressure_level == "High":
            actions = [
                "Fast-track approval process",
                "50% subsidy for public chargers",
                "EV-ready building codes",
                "Corridor development"
            ]
        else:
            actions = [
                "Standard approval process",
                "30% subsidy for public chargers",
                "Planning for future growth",
                "Public-private partnerships"
            ]
        
        # Adjust based on urban/rural split
        urban_rural = scenario_data.get('urban_rural_split', (70, 30))
        if urban_rural[0] > 80:  # Highly urban
            actions.append("Focus on high-density urban charging")
        else:
            actions.append("Balanced urban-rural deployment")
        
        return actions
    
    def _get_stakeholder_recommendations(self, stakeholder: str, scenario_data: Dict, assessment: Dict) -> List[Dict]:
        """Get stakeholder-specific recommendations"""
        stakeholder_recs = []
        
        if 'Government' in stakeholder or 'MININFRA' in stakeholder:
            stakeholder_recs.append({
                'title': 'Policy Coordination Framework',
                'description': 'Coordinate across ministries and agencies for coherent EV policy.',
                'category': 'Governance',
                'priority': 'High',
                'timeframe': '3-12 months'
            })
        
        if 'REG' in stakeholder or 'Utility' in stakeholder:
            stakeholder_recs.append({
                'title': 'Grid Modernization Plan',
                'description': 'Upgrade distribution network for EV integration.',
                'category': 'Grid Infrastructure',
                'priority': 'High',
                'timeframe': '12-36 months'
            })
        
        if 'Private Investor' in stakeholder or 'Developer' in stakeholder:
            stakeholder_recs.append({
                'title': 'Investment Readiness Assessment',
                'description': 'Evaluate market opportunities and regulatory environment.',
                'category': 'Financial',
                'priority': 'Medium',
                'timeframe': '1-3 months',
                'roi': '15-25%'
            })
        
        if 'Kigali' in stakeholder:
            stakeholder_recs.append({
                'title': 'Urban Mobility Integration',
                'description': 'Integrate EV charging with urban planning and public transport.',
                'category': 'Urban Planning',
                'priority': 'Medium',
                'timeframe': '6-24 months'
            })
        
        return stakeholder_recs
    
    # Keep the other methods (generate_roadmap, get_baseline_scenario, etc.) from previous version
    def generate_roadmap(self, scenario_data: Dict, stakeholder: str) -> List[Dict]:
        """Generate implementation roadmap"""
        today = datetime.now()
        
        # Adjust roadmap based on urgency
        assessment = self.assess_scenario(scenario_data)
        urgency = assessment.get('urgency_level', 'Medium Priority')
        
        if urgency in ["Immediate", "Urgent"]:
            phase1_duration = 90  # days
            phase2_start = 91
            phase2_duration = 270
        else:
            phase1_duration = 180
            phase2_start = 181
            phase2_duration = 360
        
        roadmap = [
            {
                'Phase': 'Phase 1: Foundation',
                'Tasks': 'Regulatory framework, Pilot programs, Capacity building',
                'Start': today,
                'End': today + timedelta(days=phase1_duration),
                'Responsible': stakeholder,
                'Budget': '$5-10M',
                'Priority': 'High'
            },
            {
                'Phase': 'Phase 2: Scaling',
                'Tasks': 'Infrastructure deployment, Incentive rollout, Grid upgrades',
                'Start': today + timedelta(days=phase2_start),
                'End': today + timedelta(days=phase2_start + phase2_duration),
                'Responsible': 'Multiple stakeholders',
                'Budget': '$20-50M',
                'Priority': 'Medium'
            },
            {
                'Phase': 'Phase 3: Optimization',
                'Tasks': 'Smart charging, V2G implementation, System integration',
                'Start': today + timedelta(days=phase2_start + phase2_duration + 1),
                'End': today + timedelta(days=1080),
                'Responsible': 'REG + Private sector',
                'Budget': '$30-70M',
                'Priority': 'Low'
            }
        ]
        
        return roadmap
    
    def get_baseline_scenario(self) -> Dict:
        """Get Rwanda's current baseline scenario"""
        return {
            'total_evs': 12500,
            'public_chargers': 156,
            'ev_growth': 20,
            'two_wheeler_share': 52,
            'peak_charging_share': 50,
            'policy_priority': 'Balanced Growth',
            'investment_appetite': 'Moderate',
            'regulatory_flexibility': 'Adaptive',
            'stakeholder': 'National Government / MININFRA',
            'charger_types': 'Balanced',
            'solar_integration': 15,
            'v2g_adoption': 5,
            'fleet_mix': ['E-Motos', 'Taxis']
        }
    
    def compare_scenarios(self, scenario1: Dict, scenario2: Dict) -> Dict:
        """Compare two scenarios"""
        assessment1 = self.assess_scenario(scenario1)
        assessment2 = self.assess_scenario(scenario2)
        
        differences = []
        
        # Compare key metrics
        if abs(scenario1['total_evs'] - scenario2['total_evs']) > 10000:
            diff = abs(scenario1['total_evs'] - scenario2['total_evs'])
            differences.append(f"EV fleet difference: {diff:,} vehicles")
        
        if assessment1['infrastructure_pressure'] != assessment2['infrastructure_pressure']:
            differences.append(f"Infrastructure pressure: {assessment1['infrastructure_pressure']} vs {assessment2['infrastructure_pressure']}")
        
        if assessment1['grid_risk'] != assessment2['grid_risk']:
            differences.append(f"Grid risk: {assessment1['grid_risk']} vs {assessment2['grid_risk']}")
        
        if assessment1['financial_viability'] != assessment2['financial_viability']:
            differences.append(f"Financial viability: {assessment1['financial_viability']} vs {assessment2['financial_viability']}")
        
        return {
            'scenario1_assessment': assessment1,
            'scenario2_assessment': assessment2,
            'differences': differences,
            'recommendation_differences': len(self.generate_recommendations(scenario1, assessment1)) - 
                                         len(self.generate_recommendations(scenario2, assessment2))
        }
    
    def save_scenario(self, name: str, scenario_data: Dict, assessment: Dict):
        """Save scenario for future reference"""
        scenario = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'data': scenario_data,
            'assessment': assessment,
            'recommendations': self.generate_recommendations(scenario_data, assessment)
        }
        
        self.scenarios.append(scenario)
        
        # Save to file
        try:
            with open('saved_scenarios.json', 'w') as f:
                json.dump(self.scenarios, f, indent=2, default=str)
        except:
            pass