from typing import Dict, List
from dataclasses import dataclass

@dataclass
class RwandaNationalTargets:
    ev_2030_target: int = 30000
    ev_2050_target: int = 150000
    charging_stations_2025: int = 500

@dataclass
class GridParameters:
    total_capacity_mw: float = 230.0
    peak_demand_mw: float = 180.0

@dataclass
class EconomicParameters:
    electricity_tariff: float = 0.18
    fuel_price: float = 1.35

@dataclass 
class VehicleFleetData:
    total_evs: int = 12500
    e_motos: int = 6500

class RwandaEVContext:
    def __init__(self):
        self.targets = RwandaNationalTargets()
        self.grid = GridParameters()
        self.economics = EconomicParameters()
        self.fleet = VehicleFleetData()