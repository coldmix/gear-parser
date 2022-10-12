import argparse, json, lupa, re

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

class LuaParser:
	def parse(self, filename, debugfile = None, opener=None):
		with open(filename, encoding='utf-8', opener=opener) as file:
			print("Reading {}".format(filename))
			script = file.read()
			lua = lupa.LuaRuntime(unpack_returned_tuples=True)
			lua_func = lua.eval('function()'+script+'end')
			result = lua_func()
			# print("{} type {}".format(filename, type(result)))
			if isinstance(result, (tuple,list)):
				result = luaToPythonType(result[0])
			else:
				result = luaToPythonType(result)
			if debugfile:
				with open(debugfile, mode="wt", encoding='utf-8') as file:
					file.write(json.dumps(result, indent=4))
			return result

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

replaceKey = ReplaceKey({
				'Double Attack %':["Dbl.Atk."],
				'Quadruple Attack %':["Quad Attack %"],
				'Accuracy':["Acc."],
				'Attack':["Atk."],
				'Ranged Accuracy':["Rng. Acc."],
				'Ranged Attack':["Rng. Atk."],
				'Magic Attack Bonus':["M. Atk. Bonus", "Magic Atk. Bonus"],
				'Magic Accuracy':['Mag. Acc.','Mag. Acc'],
				'Magic Damage':['Mag. Dmg.'],
				'Evasion':["Eva."],
				'Magic Evasion':["Mag. Eva."],
				'Magic Defense Bonus':['M. Def. B.','Magic Def. Bonus'],
				'Magic':["Mag."],
				'Left Ear':['ear1','l.ear','left_ear'],
				'Right Ear':['ear2','r.ear','right_ear'],
				'Left Ring':['ring1','l.ring','left_ring'],
				'Right Ring':['ring2','r.ring','right_ring'],
				'Main':['Main Hand'],
				'Range':['Ranged'],
			})

parser = argparse.ArgumentParser(description='Extract Items Info')
parser.add_argument('path',metavar='Windower Path', type=str, help='Path of Windower installation')
args = parser.parse_args()

windowerPath = args.path.strip('\\')
windowerResPath = args.path+"\\res\\"

parser = LuaParser()
items = parser.parse(windowerResPath+"items.lua")
itemsDesc = parser.parse(windowerResPath+"item_descriptions.lua")
jobs = parser.parse(windowerResPath+"jobs.lua")
races = parser.parse(windowerResPath+"races.lua")
slots = parser.parse(windowerResPath+"slots.lua")
itemsList = []
for k,v in races.items():
	name = v['en']
	name = re.sub('♂','Male',name)
	name = re.sub('♀','Female',name)
	v['en'] = name

cleanup = str.maketrans({'"':None, '\n':' '})
for key, item in items.items():
	item['name'] = item['en']
	item['nameLong'] = item['enl']
	del item['en']
	del item['enl']
	del item['ja']
	del item['jal']
	if key in itemsDesc:
		replacePattern = str.maketrans({
			'\ue000':'Fire',
			'\ue001':'Ice',
			'\ue002':'Wind',
			'\ue003':'Earth',
			'\ue004':'Lightning',
			'\ue005':'Water',
			'\ue006':'Light',
			'\ue007':'Dark',
			'\u21d2':'=>',
			'\u21d4':'<=>'})
		item['description'] = re.sub('\n([a-z])',r' \1',itemsDesc[key]['en'])
		item['description'] = item['description'].replace(",\n",", ")
		item['description'] = item['description'].replace("thern \n","thern ")
		item['description'] = item['description'].replace("Teleport\"\n","Teleport\" ")
		item['description'] = item['description'].translate(replacePattern)
	# else:
	# 	print("No description for {} Name {}".format(key, item['en']))
	if 'races' in item:
		race = []
		for k, v in races.items():
			if ((1 << v['id']) & item['races']):
				race.append(v['en'])
		item['races'] = race
	if 'jobs' in item:
		job = []
		for k,v in jobs.items():
			if ((1 << v['id']) & item['jobs']):
				job.append(v['ens'])
		item['jobs'] = job
	if 'slots' in item:
		slot = []
		for k,v in slots.items():
			if ((1 << v['id']) & item['slots']):
				slot.append(v['en'])
		item['slots'] = slot
	if 'description' in item:
		attr = []
		descList = item['description'].split("\n");
		if 'category' in item:
			if item['category'] in ('Armor','Weapon','Usable'):
				attrFound = False
				condition = None
				item['attribute'] = dict()
				item['trait'] = []
				attribute = item['attribute']
				trait = item['trait']
				for desc in descList:
					# attr = re.findall('(([^:\+\-]+)(:|\+|-)\s?(\d+[～~]?\d*)(\%?)|([^:\+\-]+):\s?|([\S ]+))', desc)
					attr = re.findall('((["A-Z][^:\+\-]+)(:|\+|-)\s?(\d+[～~]?\d*)(\%?)(\s?\(Max\.?\s?(\-?\d+)\))?|(["A-Z][^:\+\-]+):\s?|(["A-Z][\S ]+))', desc)
					# if item['category'] == 'Usable':
					# 	print('{} - {}'.format(item['name'],attr))
					for match in attr:
						if len(match[1]) > 0:
							attrFound = True
							name = replaceKey.replace(match[1].strip().translate(cleanup))
							if len(match[6]) > 0:
								value = int(match[6])
								attribute[name] = value
							else:
								if len(match[4]) > 0:
									name += ' '+match[4]
									name = replaceKey.replace(name)
								splitSet = {'～','-'}
								pos = next((i for i, ch in enumerate(match[3]) if ch in splitSet), None)
								if pos and match[3][pos+1:] != '':
									minVal = int(match[3][:pos])
									maxVal = int(match[3][pos+1:])
									if (match[2] == '-'):
										minVal = - minVal
										maxVal = - maxVal
									attribute[name] = [minVal, maxVal]
								else:
									if pos:
										value = int(match[3][:pos])
									else:
										value = int(match[3])
									if match[2] == '-':
										value = -value
									attribute[name] = value
						elif len(match[7].strip()) > 0:
							attrFound = True
							# print('{} - {}'.format(item['name'],attr))
							if not 'conditions' in item:
								item['conditions'] = dict()
							condition = match[7].strip().translate(cleanup)
							item['conditions'][condition] = dict()
							item['conditions'][condition]['attribute'] = dict()
							item['conditions'][condition]['trait'] = []
							attribute = item['conditions'][condition]['attribute']
							trait = item['conditions'][condition]['trait']
						elif len(match[8].strip()) > 0:
							submatch = re.match('(Incr|Conv|Spel)([^\d]+)(\d[\d\.]+)(\%?[^\d]*)', match[8])
							if submatch:
								# print('{}'.format(submatch))
								if len(submatch.group(1).strip()) > 0:
									attrFound = True
									name = submatch.group(1).strip()
									name += submatch.group(2).strip()
									name += ' '+submatch.group(4).strip()
									name = replaceKey.replace(name.translate(cleanup))
									if '.' in submatch.group(3):
										value = float(submatch.group(3))
									else:
										value = int(submatch.group(3))
									if name == 'Converts HP to MP':
										attribute['HP'] = -value
										attribute['MP'] = value
									elif name == 'Converts MP to HP':
										attribute['HP'] = value
										attribute['MP'] = -value
									else:
										attribute[name] = value
							elif attrFound:
								# print('{} - {}'.format(item['name'],attr))
								name = match[8].strip().translate(cleanup)
								if isinstance(condition, str) and (condition.lower() == 'set'):
									attribute[name] = 1
								else:
									trait.append(name)
	itemsList.append(item)

with open("items.json", mode="wt", encoding='utf-8') as file:
	file.write(json.dumps(itemsList, indent=4, sort_keys=True))
print("{} items generated in items.json".format(len(itemsList)))