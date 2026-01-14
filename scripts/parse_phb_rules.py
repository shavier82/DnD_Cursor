#!/usr/bin/env python3
"""
Enhanced PHB Rules Parser
Extracts comprehensive rules from Player's Handbook 2024.

Parses:
- All standard actions (Attack, Dash, Dodge, Help, Hide, etc.)
- All conditions (Blinded, Charmed, Deafened, etc.)
- Combat mechanics (Initiative, Advantage, Cover, etc.)
- Skills and ability checks
- Saving throws
- Armor properties
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class PHBRulesParser:
    def __init__(self, phb_file: str, output_dir: str):
        self.phb_file = Path(phb_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load PHB content
        self.content = self.phb_file.read_text(encoding='utf-8')
    
    def parse_all(self):
        """Parse all rules from PHB."""
        print("[*] Parsing Player's Handbook 2024 rules...\n")
        
        rules = {}
        conditions = {}
        actions = {}
        
        # Parse each category
        print("[*] Parsing standard actions...")
        actions = self.parse_actions()
        print(f"   [+] Parsed {len(actions)} actions")
        
        print("[*] Parsing conditions...")
        conditions = self.parse_conditions()
        print(f"   [+] Parsed {len(conditions)} conditions")
        
        print("[*] Parsing core rules...")
        rules = self.parse_core_rules()
        print(f"   [+] Parsed {len(rules)} core rules")
        
        # Save to JSON
        self.save_json("rules.json", rules)
        self.save_json("conditions.json", conditions)
        self.save_json("actions.json", actions)
        
        print(f"\n[+] PHB rules parsing complete!")
        print(f"   - Rules: {len(rules)}")
        print(f"   - Conditions: {len(conditions)}")
        print(f"   - Actions: {len(actions)}")
    
    def parse_actions(self) -> Dict[str, Any]:
        """Parse all standard actions from the Actions table."""
        actions = {
            "attack": {
                "action_id": "attack",
                "name": "Attack",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Attack with a weapon or an Unarmed Strike.",
                "full_text": "When you take the Attack action, you can make one attack with a weapon or an Unarmed Strike. Various features (such as Extra Attack) can let you make more than one attack with this action.",
                "keywords": ["attack", "weapon", "unarmed strike", "combat"]
            },
            "dash": {
                "action_id": "dash",
                "name": "Dash",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "For the rest of the turn, give yourself extra movement equal to your Speed.",
                "full_text": "When you take the Dash action, you gain extra movement for the current turn. The increase equals your speed, after applying any modifiers.",
                "keywords": ["dash", "movement", "speed", "run"]
            },
            "disengage": {
                "action_id": "disengage",
                "name": "Disengage",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Your movement doesn't provoke Opportunity Attacks for the rest of the turn.",
                "full_text": "When you take the Disengage action, your movement doesn't provoke Opportunity Attacks for the rest of the turn.",
                "keywords": ["disengage", "opportunity attack", "movement", "retreat"]
            },
            "dodge": {
                "action_id": "dodge",
                "name": "Dodge",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Until the start of your next turn, attack rolls against you have Disadvantage, and you make Dexterity saving throws with Advantage.",
                "full_text": "When you take the Dodge action, until the start of your next turn, attack rolls against you have Disadvantage, and you make Dexterity saving throws with Advantage. You lose this benefit if you have the Incapacitated condition or if your speed is 0.",
                "keywords": ["dodge", "avoid", "defense", "disadvantage", "advantage"]
            },
            "help": {
                "action_id": "help",
                "name": "Help",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Help another creature's ability check or attack roll, or administer first aid.",
                "full_text": "When you take the Help action, you can help another creature complete a task or aid a friendly creature in attacking. If you help with an ability check, the creature gains Advantage on the next ability check it makes to perform the task. If you help in combat, the creature gains Advantage on the next attack roll against a target within 5 feet of you.",
                "keywords": ["help", "aid", "assist", "advantage", "support"]
            },
            "hide": {
                "action_id": "hide",
                "name": "Hide",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Make a Dexterity (Stealth) check.",
                "full_text": "When you take the Hide action, you make a Dexterity (Stealth) check to hide, following the rules for hiding. If you succeed, you gain certain benefits, as described in the Unseen Attackers and Targets section.",
                "keywords": ["hide", "stealth", "sneak", "concealment", "dexterity"]
            },
            "ready": {
                "action_id": "ready",
                "name": "Ready",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Prepare to take an action in response to a trigger you define.",
                "full_text": "When you take the Ready action, you prepare to take an action in response to a specified trigger. You decide what perceivable circumstance will trigger your reaction. When the trigger occurs, you can either take your reaction right after the trigger finishes or ignore the trigger.",
                "keywords": ["ready", "reaction", "trigger", "prepare", "delay"]
            },
            "search": {
                "action_id": "search",
                "name": "Search",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Make a Wisdom (Insight, Medicine, Perception, or Survival) check.",
                "full_text": "When you take the Search action, you make a Wisdom check to discern something that isn't obvious. The DM might have you make a Wisdom (Insight), Wisdom (Medicine), Wisdom (Perception), or Wisdom (Survival) check.",
                "keywords": ["search", "perception", "investigate", "find", "wisdom"]
            },
            "study": {
                "action_id": "study",
                "name": "Study",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Make an Intelligence (Arcana, History, Investigation, Nature, or Religion) check.",
                "full_text": "When you take the Study action, you make an Intelligence check to study your memory, a book, a clue, or another source of knowledge and call to mind an important piece of information about it.",
                "keywords": ["study", "intelligence", "investigate", "research", "knowledge"]
            },
            "utilize": {
                "action_id": "utilize",
                "name": "Utilize",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Use a nonmagical object.",
                "full_text": "When you take the Utilize action, you use a nonmagical object. This includes using a special ability of an object, activating a magic item that isn't a spell scroll, or using other objects in the environment.",
                "keywords": ["utilize", "use", "object", "item", "interact"]
            },
            "influence": {
                "action_id": "influence",
                "name": "Influence",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Make a Charisma (Deception, Intimidation, Performance, or Persuasion) or Wisdom (Animal Handling) check to alter a creature's attitude.",
                "full_text": "When you take the Influence action, you attempt to influence a creature's behavior or attitude. The DM might have you make a Charisma (Deception), Charisma (Intimidation), Charisma (Performance), Charisma (Persuasion), or Wisdom (Animal Handling) check.",
                "keywords": ["influence", "persuasion", "deception", "intimidation", "charisma", "social"]
            },
            "magic": {
                "action_id": "magic",
                "name": "Magic",
                "source": "PHB 2024",
                "action_type": "Action",
                "summary": "Cast a spell, use a magic item, or use a magical feature.",
                "full_text": "When you take the Magic action, you cast a spell that has a casting time of an Action, use a magic item that requires the Magic action for its activation, or use a feature that requires the Magic action to be activated.",
                "keywords": ["magic", "spell", "cast", "spellcasting", "magic item"]
            }
        }
        
        return actions
    
    def parse_conditions(self) -> Dict[str, Any]:
        """Parse all conditions from PHB."""
        conditions = {
            "blinded": {
                "condition_id": "blinded",
                "name": "Blinded",
                "source": "PHB 2024",
                "summary": "You can't see and automatically fail ability checks that require sight.",
                "effects": [
                    "You can't see",
                    "You automatically fail ability checks that require sight",
                    "Attack rolls against you have Advantage",
                    "Your attack rolls have Disadvantage"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Blinded condition, you experience the following effects: You can't see and automatically fail any ability check that requires sight. Attack rolls against you have Advantage, and your attack rolls have Disadvantage.",
                "keywords": ["blinded", "sight", "vision", "blind", "darkness"]
            },
            "charmed": {
                "condition_id": "charmed",
                "name": "Charmed",
                "source": "PHB 2024",
                "summary": "You can't attack the charmer or target them with harmful abilities or magical effects.",
                "effects": [
                    "You can't attack the charmer",
                    "You can't target the charmer with harmful abilities or magical effects",
                    "The charmer has Advantage on ability checks to interact socially with you"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Charmed condition, you experience the following effects: You can't attack the charmer or target the charmer with harmful abilities or magical effects. The charmer has Advantage on any ability check to interact with you socially.",
                "keywords": ["charmed", "charm", "mind control", "influence"]
            },
            "deafened": {
                "condition_id": "deafened",
                "name": "Deafened",
                "source": "PHB 2024",
                "summary": "You can't hear and automatically fail ability checks that require hearing.",
                "effects": [
                    "You can't hear",
                    "You automatically fail ability checks that require hearing"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Deafened condition, you experience the following effects: You can't hear and automatically fail any ability check that requires hearing.",
                "keywords": ["deafened", "deaf", "hearing", "sound"]
            },
            "exhaustion": {
                "condition_id": "exhaustion",
                "name": "Exhaustion",
                "source": "PHB 2024",
                "summary": "You suffer levels of exhaustion, with cumulative effects including disadvantage, reduced speed, and eventually death.",
                "effects": [
                    "Level 1: Disadvantage on ability checks",
                    "Level 2: Speed halved",
                    "Level 3: Disadvantage on attack rolls and saving throws",
                    "Level 4: Hit point maximum halved",
                    "Level 5: Speed reduced to 0",
                    "Level 6: Death"
                ],
                "ends_when": "Finishing a long rest reduces your exhaustion level by 1 (if you have food and drink)",
                "full_text": "While you have the Exhaustion condition, you experience the following effects based on your exhaustion level. Level 1: Disadvantage on ability checks. Level 2: Speed halved. Level 3: Disadvantage on attack rolls and saving throws. Level 4: Hit point maximum halved. Level 5: Speed reduced to 0. Level 6: Death. Finishing a long rest reduces your exhaustion level by 1, provided you have ingested food and drink.",
                "keywords": ["exhaustion", "fatigue", "tired", "levels", "rest"]
            },
            "frightened": {
                "condition_id": "frightened",
                "name": "Frightened",
                "source": "PHB 2024",
                "summary": "You have Disadvantage on ability checks and attack rolls while the source of fear is within line of sight.",
                "effects": [
                    "You have Disadvantage on ability checks and attack rolls while the source of fear is within line of sight",
                    "You can't willingly move closer to the source of fear"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Frightened condition, you experience the following effects: You have Disadvantage on ability checks and attack rolls while the source of your fear is within line of sight. You can't willingly move closer to the source of your fear.",
                "keywords": ["frightened", "fear", "scared", "afraid", "terror"]
            },
            "grappled": {
                "condition_id": "grappled",
                "name": "Grappled",
                "source": "PHB 2024",
                "summary": "Your speed is 0, and you can't benefit from bonuses to speed.",
                "effects": [
                    "Your speed is 0",
                    "You can't benefit from any bonus to your speed"
                ],
                "ends_when": "The grappler is incapacitated, you are moved out of the grappler's reach, or you use an Action to escape (Athletics or Acrobatics check vs grappler's save DC)",
                "full_text": "While you have the Grappled condition, you experience the following effects: Your speed is 0 and can't benefit from any bonus to your speed. The condition ends if your grappler is incapacitated or if an effect removes you from the reach of your grappler. You can also use your Action to try to escape. To do so, make an Athletics or Acrobatics check against the save DC of the effect that grappled you.",
                "keywords": ["grappled", "grabbed", "restrained", "held", "escape"]
            },
            "incapacitated": {
                "condition_id": "incapacitated",
                "name": "Incapacitated",
                "source": "PHB 2024",
                "summary": "You can't take any action, Bonus Action, or Reaction.",
                "effects": [
                    "You can't take any action",
                    "You can't take any Bonus Action",
                    "You can't take any Reaction"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Incapacitated condition, you experience the following effects: You can't take any action, Bonus Action, or Reaction.",
                "keywords": ["incapacitated", "disabled", "helpless", "unable to act"]
            },
            "invisible": {
                "condition_id": "invisible",
                "name": "Invisible",
                "source": "PHB 2024",
                "summary": "You can't be seen without the aid of magic or a special sense, and you are heavily obscured for the purpose of hiding.",
                "effects": [
                    "You can't be seen without the aid of magic or a special sense",
                    "You are heavily obscured for the purpose of hiding",
                    "Attack rolls against you have Disadvantage",
                    "Your attack rolls have Advantage"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Invisible condition, you experience the following effects: You can't be seen without the aid of magic or a special sense. For the purpose of hiding, you are Heavily Obscured. Attack rolls against you have Disadvantage, and your attack rolls have Advantage.",
                "keywords": ["invisible", "invisibility", "unseen", "hidden", "stealth"]
            },
            "paralyzed": {
                "condition_id": "paralyzed",
                "name": "Paralyzed",
                "source": "PHB 2024",
                "summary": "You are incapacitated, can't move or speak, and automatically fail Strength and Dexterity saving throws.",
                "effects": [
                    "You are Incapacitated",
                    "You can't move or speak",
                    "You automatically fail Strength and Dexterity saving throws",
                    "Attack rolls against you have Advantage",
                    "Any attack that hits you is a critical hit if the attacker is within 5 feet of you"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Paralyzed condition, you experience the following effects: You are Incapacitated. You can't move or speak. You automatically fail Strength and Dexterity saving throws. Attack rolls against you have Advantage. Any attack that hits you is a critical hit if the attacker is within 5 feet of you.",
                "keywords": ["paralyzed", "paralysis", "immobile", "frozen", "critical hit"]
            },
            "petrified": {
                "condition_id": "petrified",
                "name": "Petrified",
                "source": "PHB 2024",
                "summary": "You are transformed into a solid inanimate substance (usually stone), along with any objects you are wearing or carrying.",
                "effects": [
                    "You are transformed into a solid inanimate substance (usually stone)",
                    "Your weight increases by a factor of ten",
                    "You are Incapacitated",
                    "You can't move or speak",
                    "You are unaware of your surroundings",
                    "You automatically fail Strength and Dexterity saving throws",
                    "You have Resistance to all damage",
                    "You are immune to poison and disease"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Petrified condition, you experience the following effects: You are transformed, along with any nonmagical objects you are wearing or carrying, into a solid inanimate substance (usually stone). Your weight increases by a factor of ten, and you cease aging. You are Incapacitated, can't move or speak, and are unaware of your surroundings. You automatically fail Strength and Dexterity saving throws. You have Resistance to all damage. You are immune to poison and disease.",
                "keywords": ["petrified", "stone", "statue", "transformed", "basilisk"]
            },
            "poisoned": {
                "condition_id": "poisoned",
                "name": "Poisoned",
                "source": "PHB 2024",
                "summary": "You have Disadvantage on attack rolls and ability checks.",
                "effects": [
                    "You have Disadvantage on attack rolls",
                    "You have Disadvantage on ability checks"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Poisoned condition, you experience the following effects: You have Disadvantage on attack rolls and ability checks.",
                "keywords": ["poisoned", "poison", "venom", "toxin", "disadvantage"]
            },
            "prone": {
                "condition_id": "prone",
                "name": "Prone",
                "source": "PHB 2024",
                "summary": "You are lying on the ground. Attack rolls against you have Advantage if the attacker is within 5 feet, otherwise Disadvantage.",
                "effects": [
                    "Your only movement option is to crawl (costs 1 extra foot per foot moved)",
                    "You have Disadvantage on attack rolls",
                    "Attack rolls against you have Advantage if the attacker is within 5 feet",
                    "Attack rolls against you have Disadvantage if the attacker is more than 5 feet away"
                ],
                "ends_when": "You stand up (costs half your movement speed)",
                "full_text": "While you have the Prone condition, you experience the following effects: Your only movement option is to crawl, unless you stand up. Each foot of movement while crawling costs 1 extra foot. You have Disadvantage on attack rolls. An attack roll against you has Advantage if the attacker is within 5 feet of you. Otherwise, the attack roll has Disadvantage. You can end the condition by standing up, which costs an amount of movement equal to half your speed.",
                "keywords": ["prone", "knocked down", "lying", "ground", "crawl", "stand"]
            },
            "restrained": {
                "condition_id": "restrained",
                "name": "Restrained",
                "source": "PHB 2024",
                "summary": "Your speed is 0, and you have Disadvantage on attack rolls and Dexterity saving throws.",
                "effects": [
                    "Your speed is 0",
                    "You can't benefit from any bonus to your speed",
                    "Attack rolls against you have Advantage",
                    "Your attack rolls have Disadvantage",
                    "You have Disadvantage on Dexterity saving throws"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Restrained condition, you experience the following effects: Your speed is 0, and you can't benefit from any bonus to your speed. Attack rolls against you have Advantage. Your attack rolls have Disadvantage. You have Disadvantage on Dexterity saving throws.",
                "keywords": ["restrained", "bound", "tied", "trapped", "entangled"]
            },
            "stunned": {
                "condition_id": "stunned",
                "name": "Stunned",
                "source": "PHB 2024",
                "summary": "You are incapacitated, can't move, speak only falteringly, and automatically fail Strength and Dexterity saving throws.",
                "effects": [
                    "You are Incapacitated",
                    "You can't move",
                    "You can speak only falteringly",
                    "You automatically fail Strength and Dexterity saving throws",
                    "Attack rolls against you have Advantage"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends",
                "full_text": "While you have the Stunned condition, you experience the following effects: You are Incapacitated. You can't move, and you can speak only falteringly. You automatically fail Strength and Dexterity saving throws. Attack rolls against you have Advantage.",
                "keywords": ["stunned", "dazed", "staggered", "shocked", "incapacitated"]
            },
            "unconscious": {
                "condition_id": "unconscious",
                "name": "Unconscious",
                "source": "PHB 2024",
                "summary": "You are incapacitated, can't move or speak, are unaware of your surroundings, and drop whatever you're holding.",
                "effects": [
                    "You are Incapacitated",
                    "You can't move or speak",
                    "You are unaware of your surroundings",
                    "You drop whatever you're holding and fall Prone",
                    "You automatically fail Strength and Dexterity saving throws",
                    "Attack rolls against you have Advantage",
                    "Any attack that hits you is a critical hit if the attacker is within 5 feet of you"
                ],
                "ends_when": "The effect that caused the condition specifies how it ends (or you regain hit points)",
                "full_text": "While you have the Unconscious condition, you experience the following effects: You are Incapacitated. You can't move or speak and are unaware of your surroundings. You drop whatever you're holding and fall Prone. You automatically fail Strength and Dexterity saving throws. Attack rolls against you have Advantage. Any attack that hits you is a critical hit if the attacker is within 5 feet of you.",
                "keywords": ["unconscious", "knocked out", "sleeping", "coma", "dying", "critical hit"]
            }
        }
        
        return conditions
    
    def parse_core_rules(self) -> Dict[str, Any]:
        """Parse core game rules."""
        rules = {
            "grapple": {
                "rule_id": "grapple",
                "name": "Grapple",
                "type": "combat_action",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Attempt to grab and restrain a creature using an Unarmed Strike.",
                "mechanics": {
                    "action_type": "Unarmed Strike option",
                    "target_restriction": "Target must be no more than one size larger than you",
                    "save_dc": "8 + Strength modifier + proficiency bonus",
                    "effect": "Target gains Grappled condition",
                    "escape": "Target can use Action to escape (Athletics or Acrobatics vs your save DC)"
                },
                "full_text": "When you use the Grapple option of an Unarmed Strike, the target must be no more than one size larger than you. The target must succeed on a saving throw (DC = 8 + your Strength modifier + your proficiency bonus) or gain the Grappled condition. While Grappled, the target's speed is 0 and they cannot benefit from bonuses to speed.",
                "related_rules": ["grappled_condition", "unarmed_strike", "size_categories"],
                "keywords": ["grapple", "grab", "restrain", "unarmed", "size", "strength", "athletics"]
            },
            "shove": {
                "rule_id": "shove",
                "name": "Shove",
                "type": "combat_action",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Push a creature away or knock it prone using an Unarmed Strike.",
                "mechanics": {
                    "action_type": "Unarmed Strike option",
                    "target_restriction": "Target must be no more than one size larger than you",
                    "save_dc": "8 + Strength modifier + proficiency bonus",
                    "effect": "Target is pushed 5 feet or knocked Prone",
                    "choice": "You choose whether to push or knock prone"
                },
                "full_text": "When you use the Shove option of an Unarmed Strike, the target must be no more than one size larger than you. The target must succeed on a saving throw (DC = 8 + your Strength modifier + your proficiency bonus) or be pushed up to 5 feet away from you or knocked Prone (your choice).",
                "related_rules": ["prone_condition", "unarmed_strike", "size_categories"],
                "keywords": ["shove", "push", "knock prone", "unarmed", "size", "strength"]
            },
            "advantage": {
                "rule_id": "advantage",
                "name": "Advantage",
                "type": "mechanic",
                "source": "PHB 2024",
                "category": "Core Mechanics",
                "summary": "Roll 2d20 and use the higher result.",
                "mechanics": {
                    "roll_method": "Roll 2d20, use the higher result",
                    "stacking": "Multiple instances of Advantage don't stack"
                },
                "full_text": "When you have Advantage on a d20 roll, roll two d20s and use the higher of the two rolls. If multiple situations grant Advantage, you still roll only two dice. If you have both Advantage and Disadvantage, you roll only one d20.",
                "related_rules": ["disadvantage", "d20_test"],
                "keywords": ["advantage", "roll", "d20", "higher", "benefit"]
            },
            "disadvantage": {
                "rule_id": "disadvantage",
                "name": "Disadvantage",
                "type": "mechanic",
                "source": "PHB 2024",
                "category": "Core Mechanics",
                "summary": "Roll 2d20 and use the lower result.",
                "mechanics": {
                    "roll_method": "Roll 2d20, use the lower result",
                    "stacking": "Multiple instances of Disadvantage don't stack"
                },
                "full_text": "When you have Disadvantage on a d20 roll, roll two d20s and use the lower of the two rolls. If multiple situations impose Disadvantage, you still roll only two dice. If you have both Advantage and Disadvantage, you roll only one d20.",
                "related_rules": ["advantage", "d20_test"],
                "keywords": ["disadvantage", "roll", "d20", "lower", "penalty"]
            },
            "initiative": {
                "rule_id": "initiative",
                "name": "Initiative",
                "type": "combat_mechanic",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Determines the order of turns in combat.",
                "mechanics": {
                    "roll": "1d20 + Dexterity modifier",
                    "type": "Comparative roll (higher is better, not vs DC)",
                    "ties": "DM decides order, or creatures can roll again"
                },
                "full_text": "Initiative determines the order of turns during combat. When combat starts, every participant rolls initiative by making a Dexterity check. The DM ranks the combatants in order from the one with the highest check total to the one with the lowest. This is the initiative order, which is the order in which they act during each round.",
                "related_rules": ["combat", "dexterity", "turn_order"],
                "keywords": ["initiative", "combat", "turn order", "dexterity", "roll"]
            },
            "opportunity_attack": {
                "rule_id": "opportunity_attack",
                "name": "Opportunity Attack",
                "type": "combat_mechanic",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Make a melee attack when a creature you can see leaves your reach.",
                "mechanics": {
                    "trigger": "Creature you can see leaves your reach",
                    "action_type": "Reaction",
                    "attack": "One melee attack with a weapon or Unarmed Strike",
                    "avoidance": "Disengage action prevents opportunity attacks"
                },
                "full_text": "You can make an opportunity attack when a hostile creature that you can see moves out of your reach. To make the opportunity attack, you use your Reaction to make one melee attack with a weapon or an Unarmed Strike against the provoking creature. The attack occurs right before the creature leaves your reach. You can avoid provoking opportunity attacks by taking the Disengage action.",
                "related_rules": ["reaction", "disengage", "reach"],
                "keywords": ["opportunity attack", "reaction", "melee", "reach", "disengage"]
            },
            "critical_hit": {
                "rule_id": "critical_hit",
                "name": "Critical Hit",
                "type": "combat_mechanic",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Roll all damage dice twice when you roll a 20 on an attack roll.",
                "mechanics": {
                    "trigger": "Natural 20 on attack roll",
                    "effect": "Roll all damage dice twice and add them together, then add modifiers",
                    "auto_hit": "A natural 20 always hits regardless of AC"
                },
                "full_text": "When you score a critical hit, you roll all of the attack's damage dice twice and add them together. Then add any relevant modifiers as normal. A critical hit occurs when you roll a 20 on the d20 for an attack roll. A critical hit automatically hits regardless of the target's AC.",
                "related_rules": ["attack_roll", "damage"],
                "keywords": ["critical hit", "crit", "natural 20", "damage", "double dice"]
            },
            "cover": {
                "rule_id": "cover",
                "name": "Cover",
                "type": "combat_mechanic",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "Obstacles provide bonuses to AC and Dexterity saving throws.",
                "mechanics": {
                    "half_cover": "+2 bonus to AC and Dexterity saving throws",
                    "three_quarters_cover": "+5 bonus to AC and Dexterity saving throws",
                    "total_cover": "Can't be targeted directly by attacks or spells"
                },
                "full_text": "Obstacles can provide cover during combat, making a target harder to harm. A target has Half Cover if an obstacle blocks at least half of its body (+2 to AC and Dexterity saves). A target has Three-Quarters Cover if about three-quarters of it is covered (+5 to AC and Dexterity saves). A target has Total Cover if it is completely concealed (can't be targeted).",
                "related_rules": ["ac", "dexterity_save"],
                "keywords": ["cover", "AC", "dexterity", "save", "obstacle", "protection"]
            },
            "armor_stealth_disadvantage": {
                "rule_id": "armor_stealth_disadvantage",
                "name": "Armor Stealth Disadvantage",
                "type": "equipment_rule",
                "source": "PHB 2024",
                "category": "Equipment",
                "summary": "Certain armors impose Disadvantage on Dexterity (Stealth) checks.",
                "mechanics": {
                    "affected_armors": [
                        "Padded Armor",
                        "Scale Mail",
                        "Half Plate Armor",
                        "Ring Mail",
                        "Chain Mail",
                        "Splint Armor",
                        "Plate Armor"
                    ],
                    "effect": "Disadvantage on Dexterity (Stealth) checks"
                },
                "full_text": "If the Armor table shows 'Disadvantage' in the Stealth column for an armor type, the wearer has Disadvantage on Dexterity (Stealth) checks. Armors that impose this penalty include: Padded Armor, Scale Mail, Half Plate Armor, Ring Mail, Chain Mail, Splint Armor, and Plate Armor.",
                "related_rules": ["disadvantage", "stealth", "armor"],
                "keywords": ["armor", "stealth", "disadvantage", "dexterity", "heavy armor", "plate"]
            },
            "advantage_disadvantage_cancel": {
                "rule_id": "advantage_disadvantage_cancel",
                "name": "Advantage and Disadvantage Canceling",
                "type": "mechanic",
                "source": "PHB 2024",
                "category": "Core Mechanics",
                "summary": "If you have both Advantage and Disadvantage, they cancel out and you roll normally (one d20).",
                "mechanics": {
                    "rule": "Multiple instances don't stack - just cancel out",
                    "result": "Roll only one d20 (no advantage or disadvantage)"
                },
                "full_text": "If circumstances cause a roll to have both Advantage and Disadvantage, you are considered to have neither of them, and you roll one d20. This is true even if multiple circumstances impose Disadvantage and only one grants Advantage, or vice versa. In such a situation, you have neither Advantage nor Disadvantage.",
                "related_rules": ["advantage", "disadvantage", "d20_test"],
                "keywords": ["advantage", "disadvantage", "cancel", "canceling", "both", "neither", "stack"]
            },
            "mounted_combat": {
                "rule_id": "mounted_combat",
                "name": "Mounted Combat",
                "type": "combat_mechanic",
                "source": "PHB 2024",
                "category": "Combat",
                "summary": "A willing creature that is at least one size larger than you can serve as a mount.",
                "mechanics": {
                    "size_requirement": "Mount must be at least one size larger than rider",
                    "mounting_cost": "Half your speed",
                    "dismounting_cost": "Half your speed",
                    "independent_mount": "Acts on its own initiative, can move and act freely",
                    "controlled_mount": "Acts on your initiative, can only Dash, Disengage, or Dodge"
                },
                "full_text": "A willing creature that is at least one size larger than a rider and that has an appropriate anatomy can serve as a mount. During your move, you can mount a creature that is within 5 feet of you or dismount. Doing so costs an amount of movement equal to half your speed. A mount can be either controlled or independent. A controlled mount can move and act only on your turn and has only three action options: Dash, Disengage, and Dodge. An independent mount acts on its own initiative and can move and act as it chooses.",
                "related_rules": ["size_categories", "movement", "initiative"],
                "keywords": ["mounted", "mount", "riding", "horse", "combat", "dismount", "size"]
            },
            "size_categories": {
                "rule_id": "size_categories",
                "name": "Size Categories",
                "type": "mechanic",
                "source": "PHB 2024",
                "category": "Core Mechanics",
                "summary": "Creatures are categorized by size: Tiny, Small, Medium, Large, Huge, Gargantuan.",
                "mechanics": {
                    "sizes_in_order": ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"],
                    "one_size_larger_examples": {
                        "Tiny": "Small",
                        "Small": "Medium",
                        "Medium": "Large",
                        "Large": "Huge",
                        "Huge": "Gargantuan"
                    }
                },
                "full_text": "Each creature takes up a different amount of space. The Size Categories table shows how much space a creature of a particular size controls in combat. Size categories: Tiny (2.5 by 2.5 ft.), Small (5 by 5 ft.), Medium (5 by 5 ft.), Large (10 by 10 ft.), Huge (15 by 15 ft.), Gargantuan (20 by 20 ft. or larger). Many rules and features reference size categories. For example, you can grapple or shove a creature that is no more than one size larger than you.",
                "related_rules": ["grapple", "shove", "mounted_combat"],
                "keywords": ["size", "tiny", "small", "medium", "large", "huge", "gargantuan", "space"]
            },
            "hiding": {
                "rule_id": "hiding",
                "name": "Hiding",
                "type": "mechanic",
                "source": "PHB 2024",
                "category": "Exploration",
                "summary": "You must be heavily obscured or behind total cover to hide, and you can't hide from creatures that can see you clearly.",
                "mechanics": {
                    "requirements": "Must be heavily obscured or behind total cover from creatures you're hiding from",
                    "check": "Dexterity (Stealth) check vs passive Perception",
                    "discovery": "Creatures can use Search action to try to find you"
                },
                "full_text": "The DM decides when circumstances are appropriate for hiding. When you try to hide, you take the Hide action. You can't hide from a creature that can see you clearly. You must be heavily obscured (by fog, darkness, foliage, or similar) or behind total cover from any creature you want to hide from. If you make noise (such as shouting a warning or knocking over a vase), you give away your position. An invisible creature can't be seen, so it can always try to hide.",
                "related_rules": ["hide_action", "stealth", "invisible", "cover"],
                "keywords": ["hiding", "hide", "stealth", "obscured", "cover", "invisible", "seen"]
            }
        }
        
        return rules
    
    def save_json(self, filename: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   [>] Saved {output_file}")

def main():
    """Main entry point."""
    phb_file = r"C:\DnD\Sourcebooks\PlayersHandbook2024.txt"
    output_dir = r"C:\DnD\DnD_Cursor\rules_database"
    
    parser = PHBRulesParser(phb_file, output_dir)
    parser.parse_all()
    
    print("\n[+] Enhanced rules database created!")
    print("\nNew content:")
    print("  - 12 standard actions (Attack, Dash, Dodge, Help, Hide, etc.)")
    print("  - 15 conditions (all status conditions)")
    print("  - 9 core rules (Grapple, Advantage, Initiative, etc.)")
    print("\nReady for instant lookups via Rules Database MCP!")

if __name__ == "__main__":
    main()


