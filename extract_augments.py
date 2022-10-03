import argparse, copy, json, re

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
		'Left Ear':['ear1','l.ear','left_ear'],
		'Right Ear':['ear2','r.ear','right_ear'],
		'Left Ring':['ring1','l.ring','left_ring'],
		'Right Ring':['ring2','r.ring','right_ring'],
		'Main':['Main Hand'],
		'Accuracy':["Acc."],
		'Attack':["Atk."],
		'Ranged Accuracy':["Rng. Acc."],
		'Ranged Attack':["Rng. Atk."],
		'Magic Atk. Bonus':["M. Atk. Bonus"],
		'Magic Accuracy':['Mag. Acc.'],
		'Evasion':["Eva."],
		'Magic Evasion':["Mag. Eva."],
		'Magic Def. Bonus':['M. Def. B.'],
	})

items = []
lines = None
with open("unity_augments.txt","r") as file:
	lines = file.readlines()
item = None
cleanup = str.maketrans({'"':None, '\n':' '})
attrList=['STR','DEX','AGI','VIT','INT','CHR']
stats = None
for line in lines:
	if line.startswith('{{Unity Armor Row'):
		item = {}
	elif line.startswith('}}'):
		if item:
			items.append(copy.deepcopy(item))
		item = None
	elif isinstance(item,dict):
		match = re.search('(Name|Aug\d)=(.*)', line)
		if match:
			# print("{} - Found {}".format(line, match))
			if match[1] == 'Name':
				item['name'] = match[2].strip().translate(cleanup)
			else:
				if not 'augments' in item:
					item['augments'] = {}
				stats = item['augments']
				matchList = re.findall('(([^\+\-\:]+)([\+|\-| ]\d+)(%?)|([^\+\-\:]+)\:)',match[2])
				if matchList:
					for augmentMatch in matchList:
						# print(augmentMatch)
						if len(augmentMatch[4]) > 0:
							name = augmentMatch[4].strip().translate(cleanup)
							if not 'conditions' in stats:
								stats['conditions'] = {}
							if not name in stats['conditions']:
								stats['conditions'][name] = {}
							stats = stats['conditions'][name]
						else:
							paramList = re.split('&|/|,',augmentMatch[1])
							for param in paramList:
								param = replaceKey.replace(param.strip().translate(cleanup))
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

with open("unity_augments.json","w") as file:
	file.write(json.dumps(items, indent=4))
print("{} items generated in unity_augments.json".format(len(items)))