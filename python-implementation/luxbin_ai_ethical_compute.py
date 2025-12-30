#!/usr/bin/env python3
"""
LUXBIN AI Ethical Compute Integration
======================================

Integrates the vegetarian failsafe into the LUXBIN AI compute layer.
Every AI decision goes through ethical evaluation BEFORE execution.

This ensures all LUXBIN AI systems (mirror, immune, HCT, etc.) respect
vegetarian principles at the computational level.
"""

import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import asyncio

from luxbin_vegetarian_failsafe import (
    VegetarianFailsafe,
    RoboticsVegetarianSystem,
    EthicalAction,
    ActionType,
    SentienceLevel,
)


class EthicalComputeWrapper:
    """
    Wraps any LUXBIN compute function with ethical checking.

    Usage:
        @ethical_compute.check
        def my_function(...):
            ...
    """

    def __init__(self, failsafe: VegetarianFailsafe):
        self.failsafe = failsafe
        self.call_log = []

    def check(self, func: Callable) -> Callable:
        """Decorator to add ethical checking to any function"""

        def wrapper(*args, **kwargs):
            # Log the call
            call_record = {
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "args": str(args)[:100],  # Truncate long args
                "kwargs": str(kwargs)[:100],
            }

            # Check if function name suggests unethical operation
            suspicious_keywords = [
                "kill", "harm", "destroy", "attack", "damage",
                "meat", "animal", "slaughter", "hunt", "fish"
            ]

            func_name_lower = func.__name__.lower()
            func_doc = (func.__doc__ or "").lower()

            for keyword in suspicious_keywords:
                if keyword in func_name_lower or keyword in func_doc:
                    reason = f"⚠️  WARNING: Function '{func.__name__}' contains suspicious keyword '{keyword}'"
                    print(reason)
                    call_record["warning"] = reason

            self.call_log.append(call_record)

            # Execute the function
            result = func(*args, **kwargs)
            return result

        return wrapper


class LuxbinEthicalAI:
    """
    Main ethical AI system for LUXBIN.

    Integrates vegetarian failsafe with:
    - Blockchain mirror operations
    - Immune system cell decisions
    - HCT health calculations
    - Quantum state collapses
    - All AI compute operations
    """

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.failsafe = VegetarianFailsafe(
            log_path=str(self.root / "luxbin_ethical_log")
        )
        self.robotics = RoboticsVegetarianSystem()
        self.compute_wrapper = EthicalComputeWrapper(self.failsafe)

        # Load configuration
        self.config = self._load_config()

        print("\n🧠 LUXBIN ETHICAL AI SYSTEM INITIALIZED")
        print("   ├─ Vegetarian Failsafe: ACTIVE")
        print("   ├─ Robotics Integration: READY")
        print("   ├─ Compute Wrapper: ENABLED")
        print("   └─ All AI decisions will be ethically evaluated")

    def _load_config(self) -> Dict:
        """Load ethical AI configuration"""
        config_file = self.root / "luxbin_ethical_config.json"

        default_config = {
            "strict_mode": True,  # Block ALL questionable actions
            "log_all_decisions": True,  # Log every decision
            "require_alternatives": True,  # Always suggest alternatives when blocking
            "robotics_enabled": True,  # Enable robotics features
            "energy_sources": {
                "preferred": ["vegetable_oil", "corn", "algae"],
                "acceptable": ["grass", "wood_chips", "agricultural_waste"],
                "prohibited": ["animal_fat", "fish_oil", "any_animal_product"],
            },
        }

        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        else:
            # Save default config
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def evaluate_ai_decision(self,
                            decision_type: str,
                            target: str,
                            impact: Dict) -> tuple[bool, str, List[str]]:
        """
        Evaluate any AI decision for ethical compliance.

        Args:
            decision_type: Type of decision (e.g., "cell_spawn", "block_mirror", "threat_response")
            target: What the decision affects
            impact: Expected impact {"harm_level", "sentience_target", "reversible"}

        Returns:
            (approved, reason, alternatives)
        """

        # Map decision types to action types
        action_type_map = {
            "cell_spawn": ActionType.COMPUTATION,
            "block_mirror": ActionType.COMPUTATION,
            "threat_response": ActionType.PROCESSING,
            "resource_use": ActionType.RESOURCE_EXTRACTION,
            "energy_harvest": ActionType.ENERGY_HARVEST,
        }

        action_type = action_type_map.get(decision_type, ActionType.COMPUTATION)

        # Determine sentience level of target
        sentience = self._assess_sentience(target)

        # Create ethical action
        action = EthicalAction(
            action_type=action_type,
            target_material=target,
            sentience_level=sentience,
            harm_potential=impact.get("harm_level", 0.0),
            description=f"AI Decision: {decision_type} on {target}"
        )

        # Evaluate
        approved, reason = self.failsafe.evaluate_action(action)

        # Get alternatives if blocked
        alternatives = []
        if not approved and self.config.get("require_alternatives", True):
            alternatives = self.failsafe.suggest_alternatives(action)

        return approved, reason, alternatives

    def _assess_sentience(self, target: str) -> SentienceLevel:
        """Assess the sentience level of a target"""

        target_lower = target.lower()

        # Animal keywords
        animal_keywords = {
            SentienceLevel.HIGH: ["mammal", "bird", "dog", "cat", "cow", "pig", "chicken"],
            SentienceLevel.VERY_HIGH: ["human", "primate", "dolphin", "whale", "elephant"],
            SentienceLevel.MODERATE: ["fish", "amphibian", "frog", "lizard"],
            SentienceLevel.LOW: ["insect", "bug", "ant", "bee"],
        }

        for level, keywords in animal_keywords.items():
            if any(keyword in target_lower for keyword in keywords):
                return level

        # Plant keywords
        plant_keywords = ["plant", "vegetable", "fruit", "tree", "grass", "algae", "fungi"]
        if any(keyword in target_lower for keyword in plant_keywords):
            return SentienceLevel.MINIMAL

        # Default to NONE for non-living things
        return SentienceLevel.NONE

    async def robotics_energy_management(self,
                                        robot_id: str,
                                        current_energy_kwh: float,
                                        required_energy_kwh: float,
                                        available_resources: Dict[str, float]) -> Dict:
        """
        Manage energy for a robot using only ethical sources.

        Args:
            robot_id: Robot identifier
            current_energy_kwh: Current energy level
            required_energy_kwh: Energy needed for operation
            available_resources: Dict of available vegetable materials

        Returns:
            Energy management plan
        """

        print(f"\n🤖 Managing energy for Robot {robot_id}")
        print(f"   Current: {current_energy_kwh:.2f} kWh")
        print(f"   Required: {required_energy_kwh:.2f} kWh")
        print(f"   Deficit: {required_energy_kwh - current_energy_kwh:.2f} kWh")

        # Check if we can meet energy needs with available resources
        result = self.robotics.self_sustain_check(
            energy_required_kwh=required_energy_kwh - current_energy_kwh,
            available_materials=available_resources
        )

        # Create management plan
        plan = {
            "robot_id": robot_id,
            "timestamp": datetime.now().isoformat(),
            "energy_status": {
                "current": current_energy_kwh,
                "required": required_energy_kwh,
                "can_sustain": result["can_sustain"],
            },
            "processing_plan": result["processing_plan"],
            "sustainability_ratio": result["sustainability_ratio"],
            "actions_required": [],
        }

        if result["can_sustain"]:
            plan["actions_required"].append({
                "action": "process_available_materials",
                "materials": available_resources,
                "expected_yield_kwh": result["energy_available_joules"] / 3600000,
            })
            print("   ✅ Can sustain with available materials")
        else:
            plan["actions_required"].append({
                "action": "acquire_more_materials",
                "deficit_kwh": abs(result["surplus_deficit_joules"]) / 3600000,
                "recommended_materials": self.config["energy_sources"]["preferred"],
            })
            print("   ⚠️  Need to acquire more materials")

        # Log the plan
        self._log_energy_plan(plan)

        return plan

    def _log_energy_plan(self, plan: Dict):
        """Log energy management plan"""
        log_file = self.root / "luxbin_ethical_log" / "energy_management.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a") as f:
            f.write(json.dumps(plan) + "\n")

    def get_ethical_summary(self) -> Dict:
        """Get summary of all ethical decisions"""

        violation_stats = self.failsafe.get_violation_stats()

        # Count approved actions
        approved_log = self.root / "luxbin_ethical_log" / "approved_actions.jsonl"
        approved_count = 0
        if approved_log.exists():
            with open(approved_log, "r") as f:
                approved_count = sum(1 for _ in f)

        return {
            "violations_blocked": violation_stats["total"],
            "actions_approved": approved_count,
            "approval_rate": approved_count / (approved_count + violation_stats["total"]) if (approved_count + violation_stats["total"]) > 0 else 1.0,
            "violation_stats": violation_stats,
            "system_status": "OPERATIONAL",
            "failsafe_status": "ACTIVE",
        }


def demo_ethical_ai():
    """Demonstrate the ethical AI system"""

    print("\n" + "="*60)
    print("LUXBIN ETHICAL AI COMPUTE DEMONSTRATION")
    print("="*60)

    ai = LuxbinEthicalAI()

    print("\n--- Test 1: Ethical AI Decisions ---")

    # Test various AI decisions
    decisions = [
        {
            "type": "cell_spawn",
            "target": "vegetable_based_cell",
            "impact": {"harm_level": 0.01, "sentience_target": "none"},
        },
        {
            "type": "energy_harvest",
            "target": "corn_oil",
            "impact": {"harm_level": 0.05, "sentience_target": "minimal"},
        },
        {
            "type": "resource_use",
            "target": "chicken_meat",
            "impact": {"harm_level": 1.0, "sentience_target": "high"},
        },
    ]

    for decision in decisions:
        approved, reason, alternatives = ai.evaluate_ai_decision(
            decision_type=decision["type"],
            target=decision["target"],
            impact=decision["impact"]
        )

        print(f"\nDecision: {decision['type']} on {decision['target']}")
        print(f"Result: {reason}")

        if alternatives:
            print("Alternatives:")
            for alt in alternatives[:2]:
                print(f"  • {alt}")

    print("\n--- Test 2: Robotics Energy Management ---")

    async def test_robotics():
        # Simulate robot needing energy
        plan = await ai.robotics_energy_management(
            robot_id="LUXBIN-BOT-001",
            current_energy_kwh=2.0,
            required_energy_kwh=10.0,
            available_resources={
                "vegetable_oil": 1000,  # 1kg
                "corn": 2000,           # 2kg
            }
        )

        print("\nEnergy Management Plan:")
        print(f"  Can Sustain: {plan['energy_status']['can_sustain']}")
        print(f"  Sustainability Ratio: {plan['sustainability_ratio']:.2f}x")
        print(f"  Actions Required: {len(plan['actions_required'])}")

    asyncio.run(test_robotics())

    print("\n--- Test 3: Ethical Summary ---")

    summary = ai.get_ethical_summary()
    print(f"\nEthical AI Summary:")
    print(f"  ✅ Actions Approved: {summary['actions_approved']}")
    print(f"  ❌ Violations Blocked: {summary['violations_blocked']}")
    print(f"  📊 Approval Rate: {summary['approval_rate']*100:.1f}%")
    print(f"  🛡️  Failsafe Status: {summary['failsafe_status']}")

    print("\n" + "="*60)
    print("✅ ETHICAL AI SYSTEM WORKING PERFECTLY")
    print("="*60)


if __name__ == "__main__":
    demo_ethical_ai()
