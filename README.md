# gear-parser
FFXI Offline Gear Parser for Stats

Requires argparse, copy, json, lupa, re, tabulate modules

## parse_equip.py

This script will parse the equipment set in the file and display the stats added by the equipment set. 
If two sets are provided, the --diff option can be used to generate the comparision between the two equipment set

```
usage: parse_equip.py [-h] [--demo] [--diff] [--debug] [--table]
                      [--format {plain,simple,fancy_grid,html,pretty,mediawiki,github,tsv}] [--gearswap]
                      [--output OUTPUT]
                      [filename ...]

Parse Gearinfo Stats.

positional arguments:
  filename              A lua gearinfo structure file to parse

optional arguments:
  -h, --help            show this help message and exit
  --demo                Generate output using demo data
  --diff                Generate diff data comparing two files
  --debug               Export the lua script to debug.log to line errors investigation
  --table               Generate in table form
  --format {plain,simple,fancy_grid,html,pretty,mediawiki,github,tsv}
                        Specify format of table
  --gearswap            Input file is gearswap format (i.e. initialized in get_sets() and stored in sets)
  --output OUTPUT       Output file to write the results
  
  ```
 The equipment file format is similar to the Windower GearSwap export output, multiple sets can be specified in one file, separated by a comma.
 See tp_gear1.lua and tp_gear2.lua for examples.
 ```
{main="Trishula",sub="Utu Grip",ammo="Aurgelmir Orb",
  head="Flam. Zucchetto +2",body="Dagon Breastplate",hands="Pel. Vambraces +2",legs="Peltast's Cuissots +2",feet="Flam. Gambieras +2",
  neck="Anu Torque",waist="Sailfi Belt +1",ear1="Telos Earring",ear2="Sherida Earring",ring1="Niqmaddu Ring",ring2="Flamma Ring",
  back={ name="Brigantia's Mantle", augments={'DEX+20','Accuracy+20 Attack+20','"Store TP"+10',}}}
,
{main="Trishula",sub="Utu Grip",ammo="Oshasha's Treatise",neck="Fotia Gorget",waist="Fotia Belt",
 ear1="Moonshade Earring",ear2="Thrud Earring",ring1="Niqmaddu Ring",ring2="Rufescent Ring",
 head="Blistering Sallet +1",body="Hjarrandi Breastplate",hands="Pel. Vambraces +2",
 legs="Peltast's Cuissots +2",feet="Sulev. Leggings +2",
 back={ name="Brigantia's Mantle", augments={'DEX+20','Accuracy+20 Attack+20','"Store TP"+10',}}}
 ```
 This is the output from the two equipset and the difference using the --table option
 ```
 python .\parse_equip.py --table  --diff .\tp_gear1.lua
 ╒═══════════════╤═══════════════════════╤═════════════════════════════════════════════╤═════════════════════════════════════╤══════════════════════════════════════════════╕
│ Stats         │ EquipSet              │ .\tp_gear1.lua:1                            │ .\tp_gear1.lua:2                    │ Difference                                   │
╞═══════════════╪═══════════════════════╪═════════════════════════════════════════════╪═════════════════════════════════════╪══════════════════════════════════════════════╡
│ Gear          │ Main                  │ Trishula                                    │ Trishula                            │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Sub                   │ Utu Grip                                    │ Utu Grip                            │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Ammo                  │ Aurgelmir Orb                               │ Oshasha's Treatise                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Head                  │ Flam. Zucchetto +2                          │ Blistering Sallet +1                │                                              │
│               │                       │                                             │ Accuracy+45                         │                                              │
│               │                       │                                             │ Magic Accuracy+45                   │                                              │
│               │                       │                                             │ Critical Hit Rate %+10              │                                              │
│               │                       │                                             │ STR+25                              │                                              │
│               │                       │                                             │ DEX+25                              │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Body                  │ Dagon Breast.                               │ Hjarrandi Breast.                   │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Hands                 │ Pel. Vambraces +2                           │ Pel. Vambraces +2                   │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Legs                  │ Pelt. Cuissots +2                           │ Pelt. Cuissots +2                   │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Feet                  │ Flam. Gambieras +2                          │ Sulev. Leggings +2                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Neck                  │ Anu Torque                                  │ Fotia Gorget                        │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Waist                 │ Sailfi Belt +1                              │ Fotia Belt                          │                                              │
│               │                       │ STR+15                                      │                                     │                                              │
│               │                       │ Double Attack %+5                           │                                     │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Left Ear              │ Telos Earring                               │ Moonshade Earring                   │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Right Ear             │ Sherida Earring                             │ Thrud Earring                       │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Left Ring             │ Niqmaddu Ring                               │ Niqmaddu Ring                       │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Right Ring            │ Flamma Ring                                 │ Rufescent Ring                      │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Back                  │ Brigantia's Mantle                          │ Brigantia's Mantle                  │                                              │
│               │                       │ DEX+20                                      │ DEX+20                              │                                              │
│               │                       │ Accuracy+20                                 │ Accuracy+20                         │                                              │
│               │                       │ Attack+20                                   │ Attack+20                           │                                              │
│               │                       │ Store TP+10                                 │ Store TP+10                         │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Attribute     │ DMG                   │ 345                                         │ 345                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Delay                 │ 492                                         │ 492                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Damage          │ 155                                         │ 155                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ DEF                   │ 666                                         │ 643                                 │ -23                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ HP                    │ 443                                         │ 553                                 │ 110                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ MP                    │ 89                                          │ 20                                  │ -69                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ STR                   │ 209                                         │ 201                                 │ -8                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ DEX                   │ 178                                         │ 156                                 │ -22                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ VIT                   │ 176                                         │ 193                                 │ 17                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ AGI                   │ 114                                         │ 103                                 │ -11                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ INT                   │ 91                                          │ 89                                  │ -2                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ MND                   │ 104                                         │ 125                                 │ 21                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ CHR                   │ 108                                         │ 129                                 │ 21                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Haste %               │ 25                                          │ 18                                  │ -7                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Accuracy              │ 302                                         │ 302                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Attack                │ 262                                         │ 269                                 │ 7                                            │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Ranged Accuracy       │ 10                                          │                                     │ -10                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Ranged Attack         │ 10                                          │                                     │ -10                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Accuracy        │ 197                                         │ 179                                 │ -18                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Evasion               │ 311                                         │ 255                                 │ -56                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Evasion         │ 417                                         │ 389                                 │ -28                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Def. Bonus      │ 23                                          │ 23                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Damage taken %        │ -22                                         │ -38                                 │ -16                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Double Attack %       │ 23                                          │ 9                                   │ -14                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Triple Attack %       │ 12                                          │                                     │ -12                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Quadruple Attack %    │ 3                                           │ 3                                   │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Store TP              │ 58                                          │ 30                                  │ -28                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Critical hit damage % │ 12                                          │ 12                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Soul Jump attack %    │ 17                                          │ 17                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Spirit Jump attack %  │ 17                                          │ 17                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Critical hit rate %   │ 4                                           │ 13                                  │ 9                                            │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Resist Slow           │ 90                                          │                                     │ -90                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Subtle Blow II        │ 20                                          │ 5                                   │ -15                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Accuracy skill  │ 228                                         │ 228                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Parrying skill        │ 269                                         │ 269                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Polearm skill         │ 269                                         │ 269                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ TP Bonus              │ 500                                         │ 500                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Weapon skill DEX %    │ 10                                          │ 10                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Spirit Link %         │ 14                                          │ 14                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Resist Stun           │ 10                                          │                                     │ -10                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Physical damage taken │                                             │ -3                                  │ -3                                           │
│               │ %                     │                                             │                                     │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Weapon skill damage % │                                             │ 13                                  │ 13                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Weapon Skill Accuracy │                                             │ 7                                   │ 7                                            │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Critical Hit Rate %   │                                             │ 10                                  │ 10                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ TP not depleted when  │                                             │ 2                                   │ 2                                            │
│               │ weapon skill used %   │                                             │                                     │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Conserve TP           │                                             │ 7                                   │ 7                                            │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Trait                 │ Stardiver                                   │ Stardiver                           │                                              │
│               │                       │ Augments Spirit Link                        │ Augments Spirit Link                │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Active                │ Unity Ranking                               │ Unity Ranking                       │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Set           │ Trait                 │ Attack occ. varies with wyvern's HP         │ Attack occ. varies with wyvern's HP │ +Enhances Subtle Blow effect                 │
│               │                       │ Increases Strength, Dexterity, and Vitality │ Enhances Subtle Blow effect         │ -Increases Strength, Dexterity, and Vitality │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Wyvern        │ Accuracy              │ 105                                         │ 105                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Magic Accuracy        │ 105                                         │ 105                                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Breath attacks        │ 15                                          │ 15                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Aftermath     │ Trait                 │ Increases skillchain potency                │ Increases skillchain potency        │                                              │
│               │                       │ Increases magic burst potency               │ Increases magic burst potency       │                                              │
│               │                       │ Ultimate Skillchain                         │ Ultimate Skillchain                 │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ All Jumps     │ Double Attack %       │ 20                                          │ 20                                  │                                              │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Unity Ranking │ Attack                │ 15                                          │                                     │ -15                                          │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ HP                    │                                             │ 80                                  │ 80                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│ Latent effect │ Weapon Skill Accuracy │                                             │ 20                                  │ 20                                           │
├───────────────┼───────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
│               │ Weapon skill damage % │                                             │ 20                                  │ 20                                           │
╘═══════════════╧═══════════════════════╧═════════════════════════════════════════════╧═════════════════════════════════════╧══════════════════════════════════════════════╛
```

### Parsing GearSwap data files

```
python .\parse_equip.py --gearswap --table --output results.txt C:\Games\Windower4\addons\GearSwap\data\Name_JOB.lua
```
The option --gearswap to support parsing of GearSwap files directly. When this option is added, the script assumes the lua file is a gearswap script and invokes the get_sets() function then retrieve the sets structure. The gearswap is expected to have the function get_sets() that configure all the sets in the sets {} object. See below for example of the functionality of the get_sets() script.

The --output option will direct the output to a file instead of printing to the console.

The parser will search for every non-empty set and extract it out into a single equipset and calculate the stats for the set. 
```
function get_sets()
    sets.precast = {}
    sets.midcast = {}
    sets.aftercast = {}
    sets.buff = {}
    -- Current Active Set
    sets.current = {}

    -- Store the list of active buffs that affect equip
    sets.buffActive = {}
    -- Store the equip from actives buffs that will merge with TP set
    sets.buffActiveTP = {}

    sets.DD = {}
    sets.DD.precast = {}
    sets.DD.midcast = {}
    sets.DD.aftercast = {}
    sets.DD.buff = {}
    sets.DD.aftercast.TP = {ammo="Aurgelmir Orb",ear1="Telos Earring",ear2="Suppanomimi",neck="Mirage Stole +1",ring1="Ilabrat Ring",ring2="Epona's Ring",back={ name="Rosmerta's Cape", augments={'DEX+20','Accuracy+20 Attack+20','DEX+10','"Store TP"+10','Damage taken-5%',}},waist="Windbuffet Belt +1",head="Hashishin Kavuk +2",body="Adhemar Jacket +1",hands="Adhemar Wrist. +1",legs="Samnuha Tights",feet={ name="Herculean Boots", augments={'Accuracy+24 Attack+24','"Store TP"+5','DEX+10','Accuracy+13','Attack+14',}}}
    sets.DD.aftercast.Idle = set_combine(sets.DD.aftercast.TP,{ammo="Staunch Tathlum",ear1="Ethereal Earring",ear2="Etiolation Earring",ring1="Defending Ring",ring2="Etana Ring",neck="Loricate Torque +1",waist="Flume Belt +1",back="Moonbeam Cape",body="Hashishin Mintan +2",head={ name="Herculean Helm", augments={'"Dbl.Atk."+3','VIT+5','"Refresh"+2',}},hands={ name="Herculean Gloves", augments={'INT+5','MND+6','"Refresh"+2','Mag. Acc.+10 "Mag.Atk.Bns."+10',}},legs="Carmine Cuisses +1",feet={ name="Herculean Boots", augments={'Attack+8','"Refresh"+2',}}}) 


    sets.DD.buff['Aftermath: Lv.3'] = {head="Malignance Chapeau",body="Malignance Tabard",hands="Malignance Gloves",legs="Malignance Tights",feet="Malignance Boots",back={ name="Rosmerta's Cape", augments={'DEX+20','Accuracy+20 Attack+20','DEX+10','"Store TP"+10','Damage taken-5%',}},ammo="Aurgelmir Orb",neck="Mirage Stole +1",waist="Reiki Yotai",ear1="Telos Earring",ear2="Eabani Earring",ring1="Ilabrat Ring",ring2="Rajas Ring"}

    sets.precast.WS = {ammo="Oshasha's Treatise",waist="Fotia Belt",neck="Fotia Gorget",ear1="Ishvara Earring",ear2="Moonshade Earring",ring1="Ilabrat Ring",ring2="Epona's Ring",back={ name="Rosmerta's Cape", augments={'STR+20','Accuracy+20 Attack+20','Weapon skill damage +10%',}},head="Hashishin Kavuk +2",body="Assim. Jubbah +3",hands="Jhakri Cuffs +2",legs="Luhlaza Shalwar +3",feet={ name="Herculean Boots", augments={'STR+3','"Dbl.Atk."+3','Weapon skill damage +10%','Accuracy+11 Attack+11',}}} --ammo="Aurgelmir Orb",
    sets.precast['Chant du Cygne'] = set_combine(sets.precast.WS,{ammo="Aurgelmir Orb",waist="Fotia Belt",neck="Mirage Stole +1",ear1="Odr Earring",ear2="Moonshade Earring",ring1="Begrudging Ring",ring2="Epona's Ring",back={ name="Rosmerta's Cape", augments={'DEX+20','Accuracy+20 Attack+20','DEX+10','Crit.hit rate+10',}},head="Blistering Sallet +1",body="Herculean Vest",hands="Adhemar Wrist. +1",legs="Samnuha Tights",feet={ name="Herculean Boots", augments={'Accuracy+24 Attack+24','"Store TP"+5','DEX+10','Accuracy+13','Attack+14',}}})
}

end
```

## Updating Resources

The parser relies on the two json files items.json and unity_augments.json

The extract_items.py will generate items.json using the path specified
```
python .\extract_items.py C:\Games\Windower4
Reading C:\Games\Windower4\res\items.lua
Reading C:\Games\Windower4\res\item_descriptions.lua
Reading C:\Games\Windower4\res\jobs.lua
Reading C:\Games\Windower4\res\races.lua
Reading C:\Games\Windower4\res\slots.lua
22444 items generated in items.json
```
The extract_augments.py reads the unity_augments.txt (copied from bgwiki source) and generates unity_augments.json
```
python .\extract_augments.py
108 items generated in unity_augments.json
```






