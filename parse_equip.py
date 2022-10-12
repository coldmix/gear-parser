import argparse, copy, json, lupa, os, re, tabulate
from functools import partial

class ReplaceKey():
	def __init__(self, dictMap):
		self.keyReplaceDict = dict()
		for k,v in dictMap.items():
			for i in v:
				self.keyReplaceDict[i.lower()] = k

	def replace(self, key):
		if key.lower() in self.keyReplaceDict:
			return self.keyReplaceDict[key.lower()]
		return key

def luaToPythonType(obj):
	if lupa.lua_type(obj) == 'table':
		dictObj = dict()
		for k, v in obj.items():
			dictObj[k] = luaToPythonType(v)
		return dictObj
	elif lupa.lua_type(obj) == 'list' or isinstance(obj, tuple):
		listObj = list()
		for v in list(obj):
			listObj.append(luaToPythonType(v))
		return listObj
	elif not isinstance(obj, (float, int, str, list, dict, tuple)):
		print("Unsupported type encountered {} - {}".format(type(v), lupa.lua_type(v)))
	return obj

class EquipStats():
	items = []
	unityAugments = []
	defaultSlots = {
		"Main":None,
		"Sub":None,
		"Range":None,
		"Ammo":None,
		"Head":None,
		"Body":None,
		"Hands":None,
		"Legs":None,
		"Feet":None,
		"Neck":None,
		"Waist":None,
		"Left Ear":None,
		"Right Ear":None,
		"Left Ring":None,
		"Right Ring":None,
		"Back":None,
	}
	defaultAttributes = {
		"DMG":0,"Delay":0,"Magic Damage":0,
		"DEF":0,"HP":0,"MP":0,"STR":0,"DEX":0,"VIT":0,"AGI":0,"INT":0,"MND":0,"CHR":0,
		"Haste %":0,"Accuracy":0,"Attack":0,"Ranged Accuracy":0,"Ranged Attack":0,"Magic Accuracy":0,"Magic Attack Bonus":0,
		"Evasion":0,"Magic Evasion":0,"Magic Defense Bonus":0,
		"Damage taken %":0,"Physical damage taken %":0,"Magic damage taken %":0,
		"Double Attack %":0,"Triple Attack %":0,"Quadruple Attack %":0,
	}
	replaceKey = ReplaceKey({
		'Double Attack %':["Dbl.Atk."],
		'Quadruple Attack %':["Quad Attack %"],
		'Accuracy':["Acc."],
		'Attack':["Atk."],
		'Ranged Accuracy':["Rng. Acc."],
		'Ranged Attack':["Rng. Atk."],
		'Magic Attack Bonus':["M. Atk. Bonus", "Magic Atk. Bonus", "Mag.Atk.Bns."],
		'Magic Accuracy':['Mag. Acc.','Mag. Acc'],
		'Magic Damage':['Mag. Dmg.'],
		'Evasion':["Eva."],
		'Magic Evasion':["Mag. Eva."],
		'Magic Defense Bonus':['M. Def. B.','Magic Def. Bonus'],
		'Magic ':["Mag."],
		'Attack ':["Atk."],
		'Bonus ':["Bns."],
		'Left Ear':['ear1','l.ear','left_ear'],
		'Right Ear':['ear2','r.ear','right_ear'],
		'Left Ring':['ring1','l.ring','left_ring'],
		'Right Ring':['ring2','r.ring','right_ring'],
		'Main':['Main Hand'],
		'Range':['Ranged'],
	})
	cleanup = str.maketrans({'"':None, '\n':' '})

	def __init__(self, char = None, equip = None, equipName = None):
		self.stats = {}
		self.active = ['Unity Ranking']
		self.equipName = equipName
		self.char = char
		self.equip = equip
		if self.equip:
			self.stats = self.equipSet(self.equip)

	def addAttribute(stats1, stats2):
		attr = {}
		if 'attribute' in stats1:
			attr = copy.deepcopy(stats1['attribute'])
		if 'attribute' in stats2:
			for key, value in stats2['attribute'].items():
				key = EquipStats.replaceKey.replace(key)
				if isinstance(value,list):
					# Use the maximum value
					value = value[-1]
				attrKey = next((attrKey for attrKey in attr.keys() if attrKey.lower() == key.lower()), None)
				if attrKey in attr:
					attr[attrKey] += value
				else:
					attr[key] = value
		return attr

	def addTrait(stats1, stats2, key='trait'):
		traits = []
		if key in stats1:
			traits = stats1[key]
		if key in stats2:
			for trait in stats2[key]:
				if not any(s.lower() == trait.lower() for s in traits):
					traits.append(trait)
		return traits

	def addStats(baseStats, stats):
		baseStats['attribute'] = copy.deepcopy(EquipStats.addAttribute(baseStats, stats))
		baseStats['trait'] = copy.deepcopy(EquipStats.addTrait(baseStats, stats))
		if 'conditions' in stats:
			for condition, conditionStats in stats['conditions'].items():
				if not 'conditions' in baseStats:
					baseStats['conditions'] = {}
				if not condition in baseStats['conditions']:
					baseStats['conditions'][condition] = {}
				EquipStats.addStats(baseStats['conditions'][condition], conditionStats)
		if 'active' in stats:
			baseStats['active'] = copy.deepcopy(EquipStats.addTrait(baseStats, stats, key='active'))
		return True

	def removeEmptyStats(stats):
		if 'attribute' in stats:
			removeList = []
			for k,v in stats['attribute'].items():
				if isinstance(v, (int,float)) and v == 0:
					removeList.append(k)
			for k in removeList:
				del stats['attribute'][k]
			if len(stats['attribute']) == 0:
				del stats['attribute']
		if 'trait' in stats:
			if isinstance(stats['trait'], dict):
				if 'added' in stats['trait'] and len(stats['trait']['added']) == 0:
					del stats['trait']['added']
				if 'removed' in stats['trait'] and len(stats['trait']['removed']) == 0:
					del stats['trait']['removed']
			if len(stats['trait']) == 0:
				del stats['trait']
		if 'conditions' in stats:
			emptyConditions = []
			for condition, conditionStats in stats['conditions'].items():
				EquipStats.removeEmptyStats(conditionStats)
				if len(conditionStats) == 0:
					emptyConditions.append(condition)
			for condition in emptyConditions:
				del stats['conditions'][condition]
		return stats

	def itemStats(name, slotInput, augments={}, itemId=None, activeConditons=[]):
		slotName = EquipStats.replaceKey.replace(slotInput)
		if itemId:
			item = next((item for item in EquipStats.items if itemId == item['id']), None)
		elif name:
			nameLower = name.lower()
			item = next((item for item in EquipStats.items if nameLower == item['name'].lower()), None)
			if not item:
				item = next((item for item in EquipStats.items if nameLower == item['nameLong'].lower()), None)
		if not item:
			print("Invalid item {} for slot {}".format(name, slotName))
			return None
		if 'slots' in item:
			slot = next((s for s in item['slots'] if s.lower() == slotName.lower()), None)
			if not slot:
				print("Invalid slot {} for {}, valid slots {}".format(slotName, item['name'], item['slots']))
				return None
		else:
			print('{} has no slots'.format(item['name']))
			slot = slotName
		if not augments:
			unityItem = next((unity for unity in EquipStats.unityAugments if item['name'] == unity['name']), None)
			if unityItem:
				# print('Found Unity Augments - {} - {}'.format(unityItem['name'],unityItem['augments']))
				augments = unityItem['augments']
		stats = dict()
		stats['name'] = item['name']
		stats['id'] = item['id']
		stats['slot'] = slot
		if 'attribute' in item:
			stats['attribute'] = item['attribute']
		if 'trait' in item:
			stats['trait'] = item['trait']
		if 'conditions' in item:
			stats['conditions'] = dict()
			for condition, conditionStats in item['conditions'].items():
				# check whether slot condition matches
				condition = EquipStats.replaceKey.replace(condition)
				if (condition.lower() == slot.lower()) or any(s.lower() == condition.lower() for s in activeConditons) :
					if not 'active' in stats:
						stats['active'] = []
					stats['active'].append(condition)
					# print("Slot {} - {} - condition {} matched, adding stats".format(stats['slot'], stats['name'], condition))
					if 'attribute' in conditionStats:
						stats['attribute'] = EquipStats.addAttribute(stats, conditionStats)
					if 'trait' in conditionStats:
						stats['trait'] = EquipStats.addTrait(stats, conditionStats)
				stats['conditions'][condition] = conditionStats
		if augments:
			EquipStats.addStats(stats, augments)
			stats['augments'] = augments
		return stats

	def charSet(self, char):
		self.char = char
		if self.equip:
			equipSet(self.equip)
		return self.stats

	def parseAugments(augments):
		attrList=['STR','DEX','AGI','VIT','INT','CHR']
		augmentStats = {}
		if isinstance(augments, dict):
			listAug = []
			for k,v in augments.items():
				listAug.append(v)
			augments = listAug
			for augment in augments:
				stats = augmentStats
				augmentMatchList = re.findall('(([^\+\-\:]+)([\+|\-| ]\d+)(%?)|([^\+\-\:]+)\:)', augment)
				if augmentMatchList:
					for augmentMatch in augmentMatchList:
						if len(augmentMatch[4]) > 0:
							name = EquipStats.replaceKey.replace(augmentMatch[4].strip().translate(EquipStats.cleanup))
							if not 'conditions' in stats:
								stats['conditions'] = {}
							if not name in stats['conditions']:
								stats['conditions'][name] = {}
							stats = stats['conditions'][name]
						else:
							paramList = re.split('&|/|,',augmentMatch[1])
							for param in paramList:
								param = EquipStats.replaceKey.replace(param.strip().translate(EquipStats.cleanup))
								if len(param) == 0:
									continue
								if not 'attribute' in stats:
									stats['attribute'] = {}
								if param in ('All Base Stats','All Attr.'):
									for attr in attrList:
										stats['attribute'][attr] = int(augmentMatch[2])
								else:
									if len(augmentMatch[3]) > 0:
										param += ' '+augmentMatch[3]
									stats['attribute'][param] = int(augmentMatch[2])
				else:
					if not 'trait' in stats:
						stats['trait'] = []
					stats['trait'].append(match[2])
		return stats

	def equipSet(self, equipSet, removeEmpty=True):
		self.equip = equipSet
		self.stats = {'equip':copy.deepcopy(EquipStats.defaultSlots),
					'attribute':copy.deepcopy(EquipStats.defaultAttributes),
					'conditions':{}}
		if self.equipName:
			self.stats['equipName'] = self.equipName
		if self.char:
			EquipStats.addStats(self.stats, self.char)
		for slot,item in equipSet.items():
			stats = None
			name = None
			itemId = None
			augments = None
			if isinstance(item, dict):
				if 'id' in item:
					itemId = item['id']
				if 'name' in item:
					name = item['name']
				if 'augments' in item:
					augments = EquipStats.parseAugments(item['augments'])
			elif isinstance(item, int):
				itemId = item
			elif isinstance(item, str):
				name = item
			else:
				print("invalid item name or id {} for slot {}".format(item, slot))
				continue
			stats = EquipStats.itemStats(name, slot, augments, itemId=itemId, activeConditons=self.active)
			# print("{} - {}".format(slot, stats))
			if stats:
				slot = stats['slot']
				self.stats['equip'][slot] = {"name":stats['name'], "id":stats['id']}
				if 'augments' in stats:
					self.stats['equip'][slot]['augments'] = copy.deepcopy(stats['augments'])
				if not EquipStats.addStats(self.stats, stats):
					print("Cannot add stats for {}".format(name))
			else:
				print("{} - Slot {} - Item {} - id {} invalid".format(self.equipName, slot, name, itemId))
		if removeEmpty:
			self.stats = EquipStats.removeEmptyStats(self.stats)
		return self.stats

	def diffAttribute(stats1, stats2):
		changedAttr = copy.deepcopy(EquipStats.defaultAttributes)
		if 'attribute' in stats2:
			for attr, value in stats2['attribute'].items():
				changedAttr[attr] = value
		if 'attribute' in stats1:
			for attr, value in stats1['attribute'].items():
				attrKey = next((attrKey for attrKey in changedAttr.keys() if attrKey.lower() == attr.lower()), None)
				if attrKey in changedAttr:
					changedAttr[attrKey] -= value
				else:
					changedAttr[attr] = -value
		return changedAttr

	def diffTrait(stats1, stats2, key='trait'):
		changedTraits = []
		if key in stats2:
			if key in stats1:
				for trait in stats2[key]:
					if not any(s.lower() == trait.lower() for s in stats1[key]):
						changedTraits.append('+'+trait)
				for trait in stats1[key]:
					if not any(s.lower() == trait.lower() for s in stats2[key]):
						changedTraits.append('-'+trait)
			else:
				for trait in stats2[key]:
					changedTraits.append('+'+trait)
		if key in stats1:
			if not key in stats2:
				for trait in stats1[key]:
					changedTraits.append('-'+trait)
		return changedTraits

	def diffStats(stats1, stats2, removeEmpty=True):
		stats = {'equipName':'Difference','attribute':{}, 'trait':[], 'conditions':{}}
		if 'equipName' in stats2 and 'equipName' in stats1:
			stats['equipName'] = '{} - {}'.format(stats2['equipName'],stats1['equipName'])
		stats['attribute'] = EquipStats.diffAttribute(stats1, stats2)
		stats['trait'] = EquipStats.diffTrait(stats1, stats2)
		stats['active'] = EquipStats.diffTrait(stats1, stats2,'active')
		# Handle conditions in stats2 compare to stats1
		if 'conditions' in stats2:
			if not 'conditions' in stats:
				stats['conditions'] = {}
			for condition, conditionStats in stats2['conditions'].items():
				if not condition in stats['conditions']:
					stats['conditions'][condition] = {'attribute':{}, 'trait':[]}
				if not 'conditions' in stats1 or not condition in stats1['conditions']:
					stats['conditions'][condition]['attribute'] = EquipStats.diffAttribute({}, conditionStats)
					stats['conditions'][condition]['trait'] = EquipStats.diffTrait({}, conditionStats)
				else:
					stats['conditions'][condition]['attribute'] = EquipStats.diffAttribute(stats1['conditions'][condition], conditionStats)
					stats['conditions'][condition]['trait'] = EquipStats.diffTrait(stats1['conditions'][condition], conditionStats)
		# Handle conditions in stats1 not found in stats2
		if 'conditions' in stats1:
			if not 'conditions' in stats:
				stats['conditions'] = {}
			for condition, conditionStats in stats1['conditions'].items():
				if not condition in stats['conditions']:
					stats['conditions'][condition] = {'attribute':{}, 'trait':[]}
				if not 'conditions' in stats2 or not condition in stats2['conditions']:
					stats['conditions'][condition]['attribute'] = EquipStats.diffAttribute(conditionStats, {})
					stats['conditions'][condition]['trait'] = EquipStats.diffTrait(conditionStats, {})
				# else:
				# 	stats['conditions'][condition]['attribute'] = EquipStats.diffAttribute(conditionStats, stats2['conditions'][condition])
				# 	stats['conditions'][condition]['trait'] = EquipStats.diffTrait(conditionStats, stats2['conditions'][condition])
		if removeEmpty:
			stats = EquipStats.removeEmptyStats(stats)
		return stats

parser = argparse.ArgumentParser(description='Parse Gearinfo Stats.')
parser.add_argument('filenames',metavar='filename', type=str, nargs='*', help='A lua gearinfo structure file to parse')
parser.add_argument('--demo', action='store_true', help='Generate output using demo data')
parser.add_argument('--diff', action='store_true', help='Generate diff data comparing two files')
parser.add_argument('--gearswap', action='store_true', help='Input file is gearswap format, i.e. sets initialized in get_sets()')
parser.add_argument('--debug', action='store_true', help='Export the lua script to debug.log to line errors investigation')
parser.add_argument('--table', action='store_true', help='Generate in table form')
parser.add_argument('--output', action='store', type=str, help='Output file to write the results')
parser.add_argument('--format',choices=['plain','simple','fancy_grid','html','pretty','mediawiki','github','tsv','htmlcss'], default='fancy_grid', help='Specify format of table')
args = parser.parse_args()

# print(args)
statsList = []
with open("items.json", mode="rt", encoding='utf-8') as file:
	EquipStats.items = json.loads(file.read())
with open("unity_augments.json", mode="rt") as file:
	EquipStats.unityAugments = json.loads(file.read())

def luaStruct(script):
	lua = lupa.LuaRuntime(unpack_returned_tuples=True)
	script = 'function() return '+script+'end'
	if args.debug:
		with open("debug.lua","w", encoding='utf-8') as file:
			file.write(script)
	try:
		lua_func = lua.eval(script)
	except Exception as e:
		print('Lua exception occurred', e, type(e))
		raise
	return luaToPythonType(lua_func())

def setsToList(sets, setList, path = ""):
	equipSlots = ('main','sub','range','ammo','head','neck','left_ear''l.ear','ear1','right_ear','r.ear','ear2','body','hands','left_ring','l.ring','ring1','right_ring','r.ring','ring2','back','waist','legs','feet')
	for k,v in sets.items():
		if isinstance(v, dict) and len(v) > 0:
			if len(path) > 0:
				subpath = '_'.join([path,k.replace(' ','_')])
			else:
				subpath = k.replace(' ','_')
			firstkey = next(iter(v))
			if isinstance(firstkey, str) and firstkey.lower() in equipSlots:
				equipSet = {}
				for slot,item in v.items():
					equipSet[slot] = item
				setList[subpath] = equipSet
			else:
				setsToList(v, setList, subpath)
	return setList

def luaGearSwap(script):
	lua = lupa.LuaRuntime(unpack_returned_tuples=True)
	script += '''

function get_slot_name(slot)
	local equip_slots = {
		main='main',
		sub='sub',
		range='range',
		ranged='range',
		ammo='ammo',
		head='head',
		neck='neck',
		left_ear='left_ear',
		ear1='left_ear',
		lear='left_ear',
		right_ear='right_ear',
		ear2='right_ear',
		rear='right_ear',
		body='body',
		hands='hands',
		left_ring='left_ring',
		ring1='left_ring',
		lring='left_ring',
		right_ring='right_ring',
		ring2='right_ring',
		rring='right_ring',
		back='back',
		waist='waist',
		legs='legs',
		feet='feet'
	}
	slot = slot:gsub("%.","")
	slot = slot:lower()
	return equip_slots[slot]
end

function set_combine(...)
    local combineSets = {...}
    gearSet = {}
    for _, set in pairs(combineSets) do
    	for slot,item in pairs(set) do
    		equipSlot = get_slot_name(slot)
    		if equipSlot ~= nil then
    			gearSet[equipSlot] = item
    		end
    	end
    end
    return gearSet
end

sets = {}
get_sets()
return sets
'''
	if args.debug:
		with open("debug.lua","w", encoding='utf-8') as file:
			file.write(script)
	try:
		results = lua.execute(script)
	except Exception as e:
		print('Lua exception occurred', e, type(e))
		raise
	sets = luaToPythonType(results)
	setList = setsToList(sets, {})
	return setList

if args.demo:
	script = """
	{main="Naegling",ammo="Aurgelmir Orb",head="Flam. Zucchetto +2",body="Dagon Breastplate",hands="Pel. Vambraces +2",legs="Peltast's Cuissots +2",feet="Flam. Gambieras +2",neck="Anu Torque",waist="Sailfi Belt +1",ear1="Telos Earring",ear2="Sherida Earring",ring1="Niqmaddu Ring",ring2="Flamma Ring",back={ name="Brigantia's Mantle", augments={'DEX+20','Accuracy+20 Attack+20','"Store TP"+10',}}}
	"""
	statsList.append(EquipStats(equip=luaStruct(script), equipName='demo1'))
	script = """
	{ammo="Oshasha's Treatise",neck="Fotia Gorget",waist="Fotia Belt",ear1="Moonshade Earring",ear2="Thrud Earring",ring1="Niqmaddu Ring",ring2="Rufescent Ring",head="Blistering Sallet +1",body="Hjarrandi Breastplate",hands="Pel. Vambraces +2",legs="Peltast's Cuissots +2",feet="Sulev. Leggings +2",back={ name="Brigantia's Mantle", augments={'DEX+20','Accuracy+20 Attack+20','"Store TP"+10',}}}
	"""
	statsList.append(EquipStats(equip=luaStruct(script), equipName='demo1'))
elif len(args.filenames) > 0:
	for filename in args.filenames:
		with open(filename,"r", encoding='utf-8') as file:
			result = file.read()
			if args.gearswap:
				path = os.path.dirname(filename)
				match = re.findall('require \"?([^\n\"]+)\"?', result)
				if match:
					for requiredFilename in match:
						searchString = 'require \"?'+re.escape(requiredFilename)+'\"?'
						with open(path+'\\'+requiredFilename,"r", encoding='utf-8') as reqFile:
							reqScript = reqFile.read()
							result = re.sub(searchString, reqScript, result)
				result = luaGearSwap(result)
				# print(json.dumps(result, indent=4))
				# print("Found {} sets in {}".format(len(result), filename))
				for name, equipSet in result.items():
					statsList.append(EquipStats(equip=equipSet, equipName=os.path.basename(filename)+":"+name))
			else:
				result = luaStruct(result)
				if isinstance(result,(list, tuple)):
					for idx, instance in enumerate(result):
						statsList.append(EquipStats(equip=instance, equipName=os.path.basename(filename)+":"+str(idx+1)))
				if isinstance(result,dict):
					statsList.append(EquipStats(equip=result, equipName=os.path.basename(filename)))
else:
	parser.print_help()
	print("Please supply at least one filename or use --demo")
	exit(-1)

if args.diff:
	if len(statsList) < 2:
		print("Minimum of 2 inputs required for diff")
		exit(-1)
	diffStats = EquipStats.diffStats(statsList[0].stats, statsList[1].stats)
else:
	diffStats = None


def statsToTable(stats):
	table = {}
	if 'equipName' in stats:
		table['equipName'] = [stats['equipName']]
	if 'equip' in stats:
		table['equip'] = {}
		for slot, item in stats['equip'].items():
			if item:
				value = item['name']
				if 'augments' in item:
					# value += '\n'+str(item['augments'])
					augList = []
					if 'attribute' in item['augments']:
						for k,v in item['augments']['attribute'].items():
							aug = '{}'.format(k)
							if isinstance(v, int) and (v >= 0):
								aug += '+'
							aug += str(v)
							augList.append(aug)
					if 'trait' in item['augments']:
						augList.extend(item['augments']['trait'])
					if 'conditions' in item['augments']:
						for condition, conditionStats in item['augments']['conditions'].items():
							if 'attribute' in conditionStats:
								for k,v in conditionStats['attribute'].items():
									aug = '{}: {}'.format(condition, k)
									if isinstance(v, int) and (v >= 0):
										aug += '+'
									aug += str(v)
									augList.append(aug)
							if 'trait' in conditionStats:
								for trait in conditionStats['trait']:
									augList.append('{}: {}'.format(condition,trait))
					value += '\n'+'\n'.join(augList)
				table['equip'][slot] = [value]
	if 'attribute' in stats:
		table['attribute'] = {}
		for name,value in stats['attribute'].items():
			table['attribute'][name] = [value]
	if 'trait' in stats:
		table['trait'] = ['\n'.join(stats['trait'])]
	if 'active' in stats:
		table['active'] = ['\n'.join(stats['active'])]

	return table

def mergeTableEntry(mainTable, table, key, length):
	# debugTable = copy.deepcopy(mainTable)
	if key in mainTable:
		attrKey = next((attrKey for attrKey in table.keys() if attrKey.lower() == key.lower()), None)
		if attrKey in table:
			mainTable[key].extend(table[attrKey])
		else:
			mainTable[key].append('')
	elif key in table:
		mainTable[key] = []
		while len(mainTable[key]) < (length-1):
			mainTable[key].append('')
		mainTable[key].extend(table[key])
	# if key in mainTable and len(mainTable[key]) != length:
	# 	print('mergeTableEntry Error {} - {} - {} - {}'.format(mainTable[key], length, debugTable, table, ))


def mergeTable(mainTable, table, length):
	# print("{} - {} - {}".format(mainTable, table, length))
	if 'equip' in mainTable:
		for key in mainTable['equip'].keys():
			if 'equip' in table:
				mergeTableEntry(mainTable['equip'], table['equip'], key, length)
			else:
				mergeTableEntry(mainTable['equip'], {}, key, length)
	if 'equip' in table:
		if not 'equip' in mainTable:
			mainTable['equip'] = {}
		for key in table['equip'].keys():
			if not key in mainTable['equip']:
				mergeTableEntry(mainTable['equip'], table['equip'], key, length)
	if 'attribute' in mainTable:
		for key in mainTable['attribute'].keys():
			if 'attribute' in table:
				mergeTableEntry(mainTable['attribute'], table['attribute'], key, length)
			else:
				mergeTableEntry(mainTable['attribute'], {}, key, length)
	if 'attribute' in table:
		if not 'attribute' in mainTable:
			mainTable['attribute'] = {}
		for key in table['attribute'].keys():
			if not key in mainTable['attribute']:
				mergeTableEntry(mainTable['attribute'], table['attribute'], key, length)
	mergeTableEntry(mainTable, table, 'trait', length)
	mergeTableEntry(mainTable, table, 'active', length)
	return mainTable

def mergeStatsList(statsList):
	statsTable = {'equipName':[], 'equip':{},'base':{},'conditions':{}}
	length = 0
	for stat in statsList:
		length += 1
		setTable = statsToTable(stat)
		mergeTableEntry(statsTable, setTable, 'equipName', length)
		mergeTable(statsTable['base'], setTable, length)
		if 'conditions' in stat:
			for condition, conditionStats in stat['conditions'].items():
				if not condition in statsTable['conditions']:
					statsTable['conditions'][condition] = {}
				mergeTable(statsTable['conditions'][condition], statsToTable(conditionStats), length)
		if 'conditions' in statsTable:
			for condition, conditionStats in statsTable['conditions'].items():
				if not condition in stat['conditions']:
					mergeTable(statsTable['conditions'][condition], {}, length)
	results = []
	firstCol = ''
	if 'equipName' in statsTable:
		entry = ['', 'EquipName']
		entry.extend(statsTable['equipName'])
		results.append(entry)
	if 'equip' in statsTable['base']:
		firstCol = 'Gear'
		for key, value in statsTable['base']['equip'].items():
			entry = [firstCol, key]
			firstCol = ''
			entry.extend(value)
			results.append(entry)
	if 'attribute' in statsTable['base']:
		firstCol = 'Attribute'
		for key, value in statsTable['base']['attribute'].items():
			entry = [firstCol, key]
			firstCol = ''
			entry.extend(value)
			results.append(entry)
	if 'trait' in statsTable['base']:
		entry = ['', 'Trait']
		entry.extend(statsTable['base']['trait'])
		results.append(entry)
	if 'active' in statsTable['base']:
		entry = ['', 'Active']
		entry.extend(statsTable['base']['active'])
		results.append(entry)
	for condition, conditionStats in statsTable['conditions'].items():
		firstCol = condition
		if 'attribute' in conditionStats:
			for key, value in conditionStats['attribute'].items():
				entry = [firstCol, key]
				firstCol = ''
				entry.extend(value)
				results.append(entry)
		if 'trait' in conditionStats:
			entry = [firstCol, 'Trait']
			entry.extend(conditionStats['trait'])
			results.append(entry)
	return results

def my_html_row_with_attrs(celltag, cell_values, colwidths, colaligns):
	alignment = {
		"left":    '',
		"right":   ' style="text-align: right;"',
		"center":  ' style="text-align: center;"',
		"decimal": ' style="text-align: right;"' }
	values_with_attrs =\
		["<{0}{1} class=\"my-cell\">{2}</{0}>".format(celltag, alignment.get(a, ''), c)
			for c, a in zip(cell_values, colaligns)]
	return "<tr class=\"my-row\">" + "".join(values_with_attrs).rstrip() + "</tr>"

htmlCssFormat = tabulate.TableFormat(
	lineabove=tabulate.Line("<table class=\"my-table\">", "", "", ""),
	linebelowheader=None,
	linebetweenrows=None,
	linebelow=tabulate.Line("</table>", "", "", ""),
	headerrow=partial(my_html_row_with_attrs, "th"),
	datarow=partial(my_html_row_with_attrs, "td"),
	padding=0, with_header_hide=None)

output = ''
if args.table:
	equipList = []
	for stat in statsList:
		equipList.append(stat.stats)
	if diffStats:
		equipList.append(diffStats)
	results = mergeStatsList(equipList)
	if args.format == 'htmlcss':
		output += tabulate.tabulate(results, headers='firstrow', tablefmt=htmlCssFormat)
	else:
		output += tabulate.tabulate(results, headers='firstrow', tablefmt=args.format)
else:
	line = '-'*80
	for stat in statsList:
		output += '{}\nStats for Equipset {}\n{}'.format(line, stat.equipName, line)
		output += json.dumps(stat.stats, indent=4)
	if args.diff:
		output += '{}\nDifference between {} and {}\n{}'.format(line, statsList[0].equipName, statsList[1].equipName, line)
		output += json.dumps(diffStats, indent=4)

if args.output:
	with open(args.output,"w", encoding='utf-8') as file:
		file.write(output)
else:
	print(output)
