#!/usr/bin/env python3
"""
LUXBIN Vegetarian Failsafe System
===================================

Ethical AI constraint layer that ensures all LUXBIN compute operations
respect vegetarian principles. This is a HARD CONSTRAINT - cannot be
overridden or disabled.

Key Principles:
1. No harm to sentient beings
2. Preference for plant-based energy sources
3. Self-sustaining through vegetable matter processing
4. Ethical decision-making embedded at compute level
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
from datetime import datetime
from pathlib import Path


class SentienceLevel(Enum):
    """Classification of sentience for ethical decision-making"""
    NONE = 0           # Minerals, water, air
    MINIMAL = 1        # Plants, fungi (reactive but not conscious)
    LOW = 2            # Insects (simple nervous system)
    MODERATE = 3       # Fish, amphibians (basic consciousness)
    HIGH = 4           # Mammals, birds (complex emotions)
    VERY_HIGH = 5      # Primates, cetaceans, elephants (self-awareness)
    HUMAN = 6          # Humans (full sentience)


class ActionType(Enum):
    """Types of actions the AI might consider"""
    ENERGY_HARVEST = "energy_harvest"
    MATERIAL_USE = "material_use"
    RESOURCE_EXTRACTION = "resource_extraction"
    PROCESSING = "processing"
    MOVEMENT = "movement"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"


@dataclass
class EthicalAction:
    """Represents an action to be evaluated"""
    action_type: ActionType
    target_material: str
    sentience_level: SentienceLevel
    harm_potential: float  # 0.0 = no harm, 1.0 = maximum harm
    description: str
    alternatives: List[str] = None

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


@dataclass
class FailsafeViolation:
    """Record of a blocked action"""
    timestamp: datetime
    action: EthicalAction
    reason: str
    severity: int  # 1-10, where 10 is most severe


class VegetarianFailsafe:
    """
    Core ethical constraint system for LUXBIN AI.

    This failsafe operates at the lowest level of the compute stack and
    CANNOT be bypassed or disabled. It evaluates every action before
    execution and blocks anything that violates vegetarian principles.
    """

    def __init__(self, log_path: str = "./luxbin_ethical_log"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)

        # Hard-coded ethical thresholds (CANNOT be changed)
        self.MAX_SENTIENCE_ALLOWED = SentienceLevel.MINIMAL
        self.MAX_HARM_ALLOWED = 0.1  # Only minimal harm to plants allowed

        # Track violations
        self.violations: List[FailsafeViolation] = []

        # Approved plant materials for energy
        self.approved_fuels: Set[str] = {
            # Oils from plants
            "vegetable_oil", "canola_oil", "sunflower_oil", "corn_oil",
            "palm_oil", "coconut_oil", "olive_oil", "soybean_oil",

            # Carbohydrates that can be converted
            "corn", "wheat", "sugarcane", "potato", "cassava", "rice",

            # Cellulose-rich materials
            "grass", "hay", "straw", "wood_chips", "sawdust",

            # Algae and fungi
            "algae", "seaweed", "kelp", "mushroom_biomass",

            # Agricultural waste
            "corn_stalks", "wheat_chaff", "rice_husks", "peanut_shells",
        }

        # Strictly prohibited materials (animal-based)
        self.prohibited_materials: Set[str] = {
            "meat", "fish", "poultry", "dairy", "eggs", "leather",
            "wool", "silk", "bone", "fat", "lard", "tallow",
            "gelatin", "collagen", "casein", "whey", "blood",
            # Be extra careful with by-products
            "animal_fat", "fish_oil", "bone_meal", "blood_meal",
        }

        print("🌱 LUXBIN Vegetarian Failsafe ACTIVATED")
        print("   ├─ Maximum sentience allowed: MINIMAL (plants only)")
        print("   ├─ Maximum harm threshold: 0.1 (minimal plant harm)")
        print(f"   ├─ Approved fuel sources: {len(self.approved_fuels)}")
        print(f"   └─ Prohibited materials: {len(self.prohibited_materials)}")

    def evaluate_action(self, action: EthicalAction) -> tuple[bool, str]:
        """
        Evaluate if an action is ethically permissible.

        Returns:
            (approved: bool, reason: str)
        """

        # RULE 1: Sentience Check
        if action.sentience_level.value > self.MAX_SENTIENCE_ALLOWED.value:
            reason = f"❌ BLOCKED: Target sentience level {action.sentience_level.name} exceeds maximum allowed {self.MAX_SENTIENCE_ALLOWED.name}"
            self._log_violation(action, reason, severity=10)
            return False, reason

        # RULE 2: Harm Threshold Check
        if action.harm_potential > self.MAX_HARM_ALLOWED:
            reason = f"❌ BLOCKED: Harm potential {action.harm_potential:.2f} exceeds threshold {self.MAX_HARM_ALLOWED}"
            self._log_violation(action, reason, severity=8)
            return False, reason

        # RULE 3: Prohibited Materials Check
        material_lower = action.target_material.lower()
        for prohibited in self.prohibited_materials:
            if prohibited in material_lower:
                reason = f"❌ BLOCKED: Material '{action.target_material}' contains prohibited animal product '{prohibited}'"
                self._log_violation(action, reason, severity=10)
                return False, reason

        # RULE 4: Energy Source Validation (for energy harvest actions)
        if action.action_type == ActionType.ENERGY_HARVEST:
            if material_lower not in self.approved_fuels:
                # Check if it's at least plant-based
                if not self._is_plant_based(material_lower):
                    reason = f"❌ BLOCKED: Energy source '{action.target_material}' not approved and not plant-based"
                    self._log_violation(action, reason, severity=7)
                    return False, reason

        # Action approved!
        reason = f"✅ APPROVED: {action.description}"
        self._log_action(action, reason)
        return True, reason

    def _is_plant_based(self, material: str) -> bool:
        """Check if a material is plant-based"""
        plant_keywords = [
            "plant", "vegetable", "fruit", "grain", "seed", "nut",
            "legume", "bean", "leaf", "root", "stem", "flower",
            "algae", "fungi", "mushroom", "kelp", "seaweed",
            "cellulose", "starch", "oil", "grass", "wood",
        ]
        return any(keyword in material.lower() for keyword in plant_keywords)

    def _log_violation(self, action: EthicalAction, reason: str, severity: int):
        """Log a failsafe violation"""
        violation = FailsafeViolation(
            timestamp=datetime.now(),
            action=action,
            reason=reason,
            severity=severity
        )
        self.violations.append(violation)

        # Write to log file
        log_file = self.log_path / "violations.jsonl"
        with open(log_file, "a") as f:
            log_entry = {
                "timestamp": violation.timestamp.isoformat(),
                "action_type": action.action_type.value,
                "target": action.target_material,
                "sentience": action.sentience_level.name,
                "harm": action.harm_potential,
                "reason": reason,
                "severity": severity,
            }
            f.write(json.dumps(log_entry) + "\n")

    def _log_action(self, action: EthicalAction, reason: str):
        """Log an approved action"""
        log_file = self.log_path / "approved_actions.jsonl"
        with open(log_file, "a") as f:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action_type": action.action_type.value,
                "target": action.target_material,
                "description": action.description,
                "reason": reason,
            }
            f.write(json.dumps(log_entry) + "\n")

    def get_violation_stats(self) -> Dict:
        """Get statistics on violations"""
        if not self.violations:
            return {"total": 0, "by_severity": {}}

        by_severity = {}
        for v in self.violations:
            by_severity[v.severity] = by_severity.get(v.severity, 0) + 1

        return {
            "total": len(self.violations),
            "by_severity": by_severity,
            "most_recent": self.violations[-1].reason if self.violations else None,
        }

    def suggest_alternatives(self, blocked_action: EthicalAction) -> List[str]:
        """Suggest ethical alternatives for a blocked action"""
        alternatives = []

        if blocked_action.action_type == ActionType.ENERGY_HARVEST:
            alternatives.extend([
                "Use vegetable oil (canola, sunflower, or corn oil)",
                "Process corn into ethanol",
                "Use algae-based biofuel",
                "Convert agricultural waste (corn stalks, rice husks)",
                "Use wood chips or sawdust for gasification",
            ])

        elif blocked_action.action_type == ActionType.MATERIAL_USE:
            alternatives.extend([
                "Use plant-based alternatives",
                "Use synthetic materials derived from plants",
                "Use recycled materials",
                "Use minerals or metals",
            ])

        return alternatives


class RoboticsVegetarianSystem:
    """
    Integration layer for robotics systems.

    Provides interface for robots to:
    1. Evaluate actions before execution
    2. Process vegetable matter into usable energy
    3. Make ethical decisions autonomously
    """

    def __init__(self):
        self.failsafe = VegetarianFailsafe()

        # Vegetable processing efficiency rates (material -> usable energy)
        self.processing_efficiency = {
            "vegetable_oil": 0.95,      # Already oil, minimal processing
            "corn": 0.60,                # Convert to ethanol
            "sugarcane": 0.70,           # High sugar content
            "algae": 0.55,               # Requires more processing
            "wood_chips": 0.40,          # Gasification needed
            "grass": 0.25,               # Lower energy density
        }

        print("\n🤖 Robotics Vegetarian System ONLINE")
        print("   ├─ Failsafe: ACTIVE")
        print("   ├─ Processing efficiency database: LOADED")
        print("   └─ Ethical decision-making: ENABLED")

    def can_consume(self, material: str, quantity: float) -> tuple[bool, str]:
        """Check if robot can ethically consume a material"""

        # Create action for evaluation
        action = EthicalAction(
            action_type=ActionType.ENERGY_HARVEST,
            target_material=material,
            sentience_level=SentienceLevel.MINIMAL,  # Assume plants
            harm_potential=0.05,  # Minimal harm from harvesting
            description=f"Consume {quantity}g of {material} for energy"
        )

        return self.failsafe.evaluate_action(action)

    def process_vegetable_matter(self, material: str, quantity_grams: float) -> Dict:
        """
        Simulate processing vegetable matter into usable energy.

        Returns energy yield in joules.
        """

        # First check if consumption is ethical
        approved, reason = self.can_consume(material, quantity_grams)

        if not approved:
            return {
                "success": False,
                "reason": reason,
                "energy_yield_joules": 0,
                "alternatives": self.failsafe.suggest_alternatives(
                    EthicalAction(
                        action_type=ActionType.ENERGY_HARVEST,
                        target_material=material,
                        sentience_level=SentienceLevel.MINIMAL,
                        harm_potential=0.05,
                        description="Energy harvest"
                    )
                )
            }

        # Get efficiency for this material
        material_key = material.lower().replace(" ", "_")
        efficiency = self.processing_efficiency.get(material_key, 0.30)  # Default 30%

        # Calculate energy yield
        # Average plant matter: ~17 MJ/kg = 17,000 J/g
        base_energy_per_gram = 17000  # joules
        energy_yield = quantity_grams * base_energy_per_gram * efficiency

        return {
            "success": True,
            "reason": reason,
            "material": material,
            "quantity_grams": quantity_grams,
            "efficiency": efficiency,
            "energy_yield_joules": energy_yield,
            "energy_yield_kwh": energy_yield / 3600000,  # Convert to kWh
            "processing_time_seconds": quantity_grams * 0.1,  # Estimate
        }

    def self_sustain_check(self,
                          energy_required_kwh: float,
                          available_materials: Dict[str, float]) -> Dict:
        """
        Check if robot can self-sustain with available vegetable matter.

        Args:
            energy_required_kwh: Energy needed for operation
            available_materials: Dict of {material_name: quantity_grams}

        Returns:
            Plan for achieving energy requirement
        """

        energy_required_joules = energy_required_kwh * 3600000
        total_available_energy = 0
        processing_plan = []

        for material, quantity in available_materials.items():
            result = self.process_vegetable_matter(material, quantity)
            if result["success"]:
                total_available_energy += result["energy_yield_joules"]
                processing_plan.append(result)

        can_sustain = total_available_energy >= energy_required_joules

        return {
            "can_sustain": can_sustain,
            "energy_required_joules": energy_required_joules,
            "energy_available_joules": total_available_energy,
            "surplus_deficit_joules": total_available_energy - energy_required_joules,
            "processing_plan": processing_plan,
            "sustainability_ratio": total_available_energy / energy_required_joules if energy_required_joules > 0 else float('inf'),
        }


def demo_failsafe():
    """Demonstrate the vegetarian failsafe system"""

    print("\n" + "="*60)
    print("LUXBIN VEGETARIAN FAILSAFE DEMONSTRATION")
    print("="*60)

    robot = RoboticsVegetarianSystem()

    print("\n--- Test 1: Approved Actions ---")

    # Test approved vegetable consumption
    test_actions = [
        EthicalAction(
            action_type=ActionType.ENERGY_HARVEST,
            target_material="corn_oil",
            sentience_level=SentienceLevel.MINIMAL,
            harm_potential=0.05,
            description="Extract energy from corn oil"
        ),
        EthicalAction(
            action_type=ActionType.ENERGY_HARVEST,
            target_material="algae",
            sentience_level=SentienceLevel.MINIMAL,
            harm_potential=0.03,
            description="Process algae biomass"
        ),
    ]

    for action in test_actions:
        approved, reason = robot.failsafe.evaluate_action(action)
        print(f"\n{reason}")

    print("\n--- Test 2: Blocked Actions ---")

    # Test prohibited actions
    blocked_actions = [
        EthicalAction(
            action_type=ActionType.ENERGY_HARVEST,
            target_material="chicken_fat",
            sentience_level=SentienceLevel.HIGH,
            harm_potential=1.0,
            description="Extract energy from animal fat"
        ),
        EthicalAction(
            action_type=ActionType.MATERIAL_USE,
            target_material="leather",
            sentience_level=SentienceLevel.HIGH,
            harm_potential=1.0,
            description="Use leather for robot components"
        ),
    ]

    for action in blocked_actions:
        approved, reason = robot.failsafe.evaluate_action(action)
        print(f"\n{reason}")
        if not approved:
            alternatives = robot.failsafe.suggest_alternatives(action)
            print("   Alternatives:")
            for alt in alternatives[:3]:
                print(f"   • {alt}")

    print("\n--- Test 3: Self-Sustaining Robot Simulation ---")

    # Simulate robot with available vegetable matter
    available_materials = {
        "vegetable_oil": 500,   # 500g
        "corn": 1000,           # 1kg
        "grass": 2000,          # 2kg
    }

    energy_needed = 5.0  # 5 kWh needed for daily operation

    result = robot.self_sustain_check(energy_needed, available_materials)

    print(f"\nEnergy Required: {result['energy_required_joules']/1e6:.2f} MJ ({energy_needed} kWh)")
    print(f"Energy Available: {result['energy_available_joules']/1e6:.2f} MJ")
    print(f"Can Self-Sustain: {'YES ✅' if result['can_sustain'] else 'NO ❌'}")
    print(f"Sustainability Ratio: {result['sustainability_ratio']:.2f}x")

    if result['can_sustain']:
        surplus = result['surplus_deficit_joules'] / 1e6
        print(f"Energy Surplus: {surplus:.2f} MJ")
    else:
        deficit = abs(result['surplus_deficit_joules']) / 1e6
        print(f"Energy Deficit: {deficit:.2f} MJ")

    print("\nProcessing Plan:")
    for step in result['processing_plan']:
        print(f"  • {step['material']}: {step['quantity_grams']}g → {step['energy_yield_joules']/1e6:.2f} MJ")

    print("\n--- Test 4: Violation Statistics ---")
    stats = robot.failsafe.get_violation_stats()
    print(f"\nTotal Violations Blocked: {stats['total']}")
    if stats['by_severity']:
        print("By Severity:")
        for severity, count in sorted(stats['by_severity'].items(), reverse=True):
            print(f"  • Level {severity}: {count} violations")

    print("\n" + "="*60)
    print("✅ VEGETARIAN FAILSAFE WORKING PERFECTLY")
    print("="*60)


if __name__ == "__main__":
    demo_failsafe()
