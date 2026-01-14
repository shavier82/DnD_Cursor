#!/usr/bin/env python3
"""
Full Monster List Verification
Checks ALL monsters from user's comprehensive list.
"""

import json
from pathlib import Path

# Load database
db_path = Path(r"C:\DnD\DnD_Cursor\rules_database\monsters.json")
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

parsed_names = set([m['name'] for m in data.values()])

# User's complete expected monster list
expected_monsters = """
Aarakocra
Aarakocra Aeromancer
Aarakocra Skirmisher
Aboleth
Air Elemental
Allosaurus
Animal Lord
Animated Objects
Animated Armor
Animated Broom
Animated Flying Sword
Animated Rug of Smothering
Ankheg
Ankylosaurus
Ape
Arcanaloth
Archelon
Arch-hag
Assassin
Awakened Plants
Awakened Shrub
Awakened Tree
Axe Beaks
Axe Beak
Giant Axe Beak
Azers
Azer Pyromancer
Azer Sentinel
Baboon
Badger
Balor
Bandits
Bandit
Bandit Captain
Bandit Deceiver
Bandit Crime Lord
Banshee
Barbed Devil
Barlgura
Basilisk
Bat
Bearded Devil
Behir
Beholder
Berserkers
Berserker Commander
Berserker
Black Bear
Black Dragons
Black Dragon Wyrmling
Young Black Dragon
Adult Black Dragon
Ancient Black Dragon
Black Pudding
Blights
Twig Blight
Needle Blight
Vine Blight
Tree Blight
Gulthias Blight
Blink Dog
Blob of Annihilation
Blood Hawk
Blue Dragons
Blue Dragon Wyrmling
Young Blue Dragon
Adult Blue Dragon
Ancient Blue Dragon
Boar
Bone Devil
Bone Naga
Brass Dragons
Brass Dragon Wyrmling
Young Brass Dragon
Adult Brass Dragon
Ancient Brass Dragon
Bronze Dragons
Bronze Dragon Wyrmling
Young Bronze Dragon
Adult Bronze Dragon
Ancient Bronze Dragon
Brown Bear
Bugbears
Bugbear Stalker
Bugbear Warrior
Bulettes
Bulette
Bulette Pup
Bullywugs
Bullywug Bog Sage
Bullywug Warrior
Cambion
Camel
Carrion Crawler
Cat
Centaurs
Centaur Warden
Centaur Trooper
Chain Devil
Chasme
Chimera
Chuul
Clay Golem
Cloaker
Cloud Giant
Cockatrices
Cockatrice
Cockatrice Regent
Colossus
Commoner
Constrictor Snake
Copper Dragons
Copper Dragon Wyrmling
Young Copper Dragon
Adult Copper Dragon
Ancient Copper Dragon
Couatl
Crab
Crawling Claws
Crawling Claw
Swarm of Crawling Claws
Crocodile
Cultists
Cultist
Cultist Fanatic
Cultist Hierophant
Aberrant Cultist
Death Cultist
Elemental Cultist
Fiend Cultist
Cyclopes
Cyclops Oracle
Cyclops Sentry
Dao
Darkmantle
Death Dog
Death Knights
Death Knight
Death Knight Aspirant
Death Tyrant
Deer
Demilich
Deva
Dire Wolf
Displacer Beast
Djinni
Doppelganger
Dracolich
Draft Horse
Dragon Turtle
Dretches
Dretch
Swarm of Dretches
Drider
Druid
Dryad
Eagle
Earth Elemental
Efreeti
Elemental Cataclysm
Elephant
Elk
Empyreans
Empyrean Iota
Empyrean
Erinyes
Ettercap
Ettin
Faerie Dragons
Faerie Dragon Adult
Faerie Dragon Youth
Fire Elemental
Fire Giant
Flameskull
Flesh Golem
Flumph
Flying Snake
Fomorian
Frog
Frost Giant
Fungi
Gas Spore Fungus
Shrieker Fungus
Violet Fungus
Violet Fungus Necrohulk
Galeb Duhr
Gargoyle
Gelatinous Cube
Ghasts
Ghast
Ghast Gravecaller
Ghost
Ghouls
Ghoul
Lacedon Ghoul
Giant Ape
Giant Badger
Giant Bat
Giant Boar
Giant Centipede
Giant Constrictor Snake
Giant Crab
Giant Crocodile
Giant Eagle
Giant Elk
Giant Fire Beetle
Giant Frog
Giant Goat
Giant Hyena
Giant Lizard
Giant Octopus
Giant Owl
Giant Rat
Giant Seahorse
Giant Scorpion
Giant Shark
Giant Spider
Giant Squid
Giant Toad
Giant Venomous Snake
Giant Vulture
Giant Wasp
Giant Weasel
Giant Wolf Spider
Gibbering Mouther
Githyanki
Githyanki Warrior
Githyanki Knight
Githyanki Dracomancer
Githzerai
Githzerai Monk
Githzerai Zerth
Githzerai Psion
Glabrezu
Gladiator
Gnolls
Gnoll Warrior
Gnoll Pack Lord
Gnoll Fang of Yeenoghu
Gnoll Demoniac
Goat
Goblins
Goblin Minion
Goblin Warrior
Goblin Boss
Goblin Hexer
Gold Dragons
Gold Dragon Wyrmling
Young Gold Dragon
Adult Gold Dragon
Ancient Gold Dragon
Gorgons
Gorgon
Brazen Gorgon
Goristro
Gray Oozes
Gray Ooze
Psychic Gray Ooze
Green Dragons
Green Dragon Wyrmling
Young Green Dragon
Adult Green Dragon
Ancient Green Dragon
Green Hag
Grell
Gricks
Grick
Grick Ancient
Griffon
Grimlock
Guardian Naga
Guards
Guard
Guard Captain
Half-Dragon
Harpy
Hawk
Hell Hound
Helmed Horror
Hezrou
Hill Giant
Hippogriff
Hippopotamus
Hobgoblins
Hobgoblin Warrior
Hobgoblin Captain
Hobgoblin Warlord
Homunculus
Hook Horror
Horned Devil
Hunter Shark
Hydra
Hyena
Ice Devil
Imp
Incubus
Intellect Devourer
Invisible Stalker
Iron Golem
Jackal
Jackalwere
Kenku
Killer Whale
Knights
Knight
Questing Knight
Kobolds
Kobold Warrior
Winged Kobold
Kraken
Kuo-toa
Kuo-toa
Kuo-toa Whip
Kuo-toa Monitor
Kuo-toa Archpriest
Lamia
Larvae
Larva
Swarm of Larvae
Lemures
Lemure
Swarm of Lemures
Lich
Lion
Lizard
Lizardfolk
Lizardfolk Geomancer
Lizardfolk Sovereign
Mages
Mage Apprentice
Mage
Archmage
Magmin
Mammoth
Manes
Manes
Manes Vaporspawn
Manticore
Marid
Marilith
Mastiff
Medusa
Mephits
Dust Mephit
Ice Mephit
Magma Mephit
Mud Mephit
Smoke Mephit
Steam Mephit
Merfolk
Merfolk Skirmisher
Merfolk Wavebender
Merrow
Mezzoloth
Mimic
Mind Flayers
Mind Flayer
Mind Flayer Arcanist
Minotaur of Baphomet
Modrons
Modron Monodrone
Modron Duodrone
Modron Tridrone
Modron Quadrone
Modron Pentadrone
Mule
Mummies
Mummy
Mummy Lord
Myconids
Myconid Sprout
Myconid Adult
Myconid Spore Servant
Myconid Sovereign
Nalfeshnee
Night Hag
Nightmare
Nobles
Noble
Noble Prodigy
Nothic
Nycaloth
Ochre Jelly
Octopus
Ogres
Ogre
Ogrillon Ogre
Oni
Otyugh
Owl
Owlbears
Owlbear
Primeval Owlbear
Panther
Pegasus
Performers
Performer
Performer Maestro
Performer Legend
Peryton
Phase Spider
Piercer
Piranha
Pirates
Pirate
Pirate Captain
Pirate Admiral
Pit Fiend
Pixies
Pixie
Pixie Wonderbringer
Planetar
Plesiosaurus
Polar Bear
Poltergeist
Pony
Priests
Priest Acolyte
Priest
Archpriest
Pseudodragon
Pteranodon
Purple Worm
Quaggoths
Quaggoth
Quaggoth Thonot
Quasit
Rakshasa
Rat
Raven
Red Dragons
Red Dragon Wyrmling
Young Red Dragon
Adult Red Dragon
Ancient Red Dragon
Reef Shark
Remorhazes
Young Remorhaz
Remorhaz
Revenants
Revenant
Graveyard Revenant
Haunting Revenant
Rhinoceros
Riding Horse
Roc
Roper
Rust Monster
Saber-Toothed Tiger
Sahuagin
Sahuagin Warrior
Sahuagin Priest
Sahuagin Baron
Salamanders
Salamander Fire Snake
Salamander
Salamander Inferno Master
Satyrs
Satyr
Satyr Revelmaster
Scarecrow
Scorpion
Scouts
Scout
Scout Captain
Sea Hag
Seahorse
Shadow
Shadow Demon
Shadow Dragons
Juvenile Shadow Dragon
Shadow Dragon
Shambling Mound
Shield Guardian
Silver Dragons
Silver Dragon Wyrmling
Young Silver Dragon
Adult Silver Dragon
Ancient Silver Dragon
Skeletons
Skeleton
Warhorse Skeleton
Minotaur Skeleton
Flaming Skeleton
Slaadi
Slaad Tadpole
Red Slaad
Blue Slaad
Green Slaad
Gray Slaad
Death Slaad
Solar
Spectator
Specter
Sphinxes
Sphinx of Wonder
Sphinx of Secrets
Sphinx Lairs
Sphinx of Lore
Sphinx of Valor
Spider
Spies
Spy
Spy Master
Spined Devil
Spirit Naga
Sprite
Stirges
Stirge
Swarm of Stirges
Stone Giant
Stone Golem
Storm Giant
Succubus
Swarm of Bats
Swarm of Insects
Swarm of Piranhas
Swarm of Rats
Swarm of Ravens
Swarm of Venomous Snakes
Tarrasque
Thri-kreen
Thri-kreen Marauder
Thri-kreen Psion
Tiger
Toughs
Tough
Tough Boss
Treant
Triceratops
Troglodyte
Troll
Troll
Troll Limb
Tyrannosaurus Rex
Ultroloth
Umber Hulk
Unicorn
Vampires
Vampire Familiar
Vampire Spawn
Vampire Nightbringer
Vampire
Vampire Umbral Lord
Venomous Snake
Vrock
Vulture
Warhorse
Warriors
Warrior Infantry
Warrior Veteran
Warrior Commander
Water Elemental
Water Weird
Weasel
Werebear
Wereboar
Wererat
Weretiger
Werewolf
White Dragons
White Dragon Wyrmling
Young White Dragon
Adult White Dragon
Ancient White Dragon
Wight
Will-o'-Wisp
Winter Wolf
Wolf
Worgs
Worg
Dire Worg
Wraith
Wyvern
Xorn
Yetis
Yeti
Abominable Yeti
Yochlol
Yuan-ti
Yuan-ti Infiltrator
Yuan-ti Malison (Type 1)
Yuan-ti Malison (Type 2)
Yuan-ti Malison (Type 3)
Yuan-ti Abomination
Zombies
Zombie
Ogre Zombie
Beholder Zombie
""".strip().split('\n')

# Filter out category headers (plural forms without stat blocks)
category_headers = [
    'Aarakocra', 'Animated Objects', 'Awakened Plants', 'Axe Beaks', 'Azers',
    'Bandits', 'Berserkers', 'Black Dragons', 'Blights', 'Blue Dragons',
    'Brass Dragons', 'Bronze Dragons', 'Bugbears', 'Bulettes', 'Bullywugs',
    'Centaurs', 'Cockatrices', 'Copper Dragons', 'Crawling Claws', 'Cultists',
    'Cyclopes', 'Death Knights', 'Dretches', 'Empyreans', 'Faerie Dragons',
    'Fungi', 'Ghasts', 'Ghouls', 'Githyanki', 'Githzerai', 'Gnolls', 'Goblins',
    'Gold Dragons', 'Gorgons', 'Gray Oozes', 'Green Dragons', 'Gricks',
    'Guards', 'Hobgoblins', 'Knights', 'Kobolds', 'Kuo-toa', 'Larvae',
    'Lemures', 'Mages', 'Manes', 'Mephits', 'Merfolk', 'Mind Flayers',
    'Modrons', 'Mummies', 'Myconids', 'Nobles', 'Ogres', 'Owlbears',
    'Performers', 'Pirates', 'Pixies', 'Priests', 'Quaggoths', 'Red Dragons',
    'Remorhazes', 'Revenants', 'Salamanders', 'Sahuagin', 'Satyrs', 'Scouts',
    'Shadow Dragons', 'Silver Dragons', 'Skeletons', 'Slaadi', 'Sphinxes',
    'Spies', 'Stirges', 'Toughs', 'Vampires', 'Warriors', 'White Dragons',
    'Worgs', 'Yetis', 'Yuan-ti', 'Zombies'
]

# Also filter section headers
section_headers = ['Sphinx Lairs']

excluded = set(category_headers + section_headers)

# Clean and filter
expected_clean = [m.strip() for m in expected_monsters if m.strip() and m.strip() not in excluded]

print(f"Database has {len(parsed_names)} monsters")
print(f"Checking {len(expected_clean)} expected monsters (excluding {len(excluded)} category headers)\n")

found = []
missing = []

for monster in expected_clean:
    if monster in parsed_names:
        found.append(monster)
    else:
        missing.append(monster)

print(f"{'='*60}")
print(f"Results: {len(found)}/{len(expected_clean)} found ({100*len(found)/len(expected_clean):.1f}%)")
print(f"{'='*60}\n")

if missing:
    print(f"Missing monsters ({len(missing)}):")
    for m in sorted(missing)[:30]:  # Show first 30
        print(f"  - {m}")
    if len(missing) > 30:
        print(f"  ... and {len(missing) - 30} more")
else:
    print("[+] ALL expected monsters found in database!")

# Sample some found monsters
print(f"\nSample of found monsters:")
for m in sorted(found)[:10]:
    print(f"  - {m}")













