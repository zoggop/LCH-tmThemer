from colormath.color_objects import sRGBColor, LCHabColor
from colormath.color_conversions import convert_color
from lxml import etree as ET
import sys
from math import floor, ceil

### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'comment' : {
		'palette' : ['#997A66'],
		'groups' : [
			{'comment':'foreground', 'findHighlight':''}
		],
	},
	'grayscale' : {
		'palette' : ['#ffffff', '#f1f1f1', '#d4d4d4', '#b9b9b9', '#777777', '#616161', '#303030'],
		'groups' : [
			['background', 'findHighlightForeGround', 'selectionBorder'],
			['selection', 'lineHighlight'],
			['stackGuide', 'invisibles'],
			['guide'],
			['activeGuide'],
			['foreground'],
			['caret']
		],
	},
	'background' : {
		'palette' : [95, 13, 10, 0],
		'groups' : [
			{'string':'', 'invalid':'foreground', 'invalid.deprecated':'foreground'},
			['entity.name.class', 'entity.name.function', 'entity.other.inherited-class'],
			['meta.arrayindex, meta.item-access.arguments'],
		]
	},
	'foreground' : {
		'palette' : [49, 95, 11, 6],
		'groups' : [
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background'},
			{'variable.parameter':'', 'invalid.deprecated':'background'},
			['meta.function', 'variable.function', 'entity.other.attribute-name'], # 'meta.functioncall, meta.function-call'
			['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type'],
			{'constant':''},
			# ['variable, support.variable, meta.qualified-name, support.other.variable'],
		]
	}
}

fontStyles = {
	'variable.parameter' : 'italic',
	'support.type' : 'italic',
	'support.class' : 'italic',
	'storage.type' : 'italic',
	'entity.other.inherited-class' : 'italic underline',
	'entity.name.class' : 'underline',
	'variable.function' : 'bold',
	'invalid' : 'bold',
	'invalid.deprecated' : 'bold',
}

### END CONFIGURATION ###

settingsKeys = {'background', 'foreground', 'caret', 'invisibles', 'lineHighlight', 'selection', 'findHighlightForeGround', 'findHighlight', 'selectionBorder', 'guide', 'activeGuide', 'stackGuide'}

def angleDist(a, b):
	return abs(((b - a) + 180) % 360 - 180)

def tolerance(a, b, t):
	return abs(b - a) <= t

def LCHtolerance(a, b, t):
	return tolerance(a.lch_l, b.lch_l, t) and tolerance(a.lch_c, b.lch_c, t) and (a.lch_c == 0 or tolerance(a.lch_h, b.lch_h, t))

def outOfGamut(rgb):
	return rgb.clamped_rgb_r != rgb.rgb_r or rgb.clamped_rgb_g != rgb.rgb_g or rgb.clamped_rgb_b != rgb.rgb_b

def findGoodLightness(lightness, chroma, hue, t, lightnessT):
	found = False
	d = 0
	while not found and d <= lightnessT:
		ls = [lightness + d]
		if d > 0:
			ls.append(lightness - d)
		for l in ls:
			c = LCHabColor(l, chroma, hue)
			rgb = convert_color(c, sRGBColor)
			if not outOfGamut(rgb):
				cc = convert_color(sRGBColor(rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b), LCHabColor)
				if LCHtolerance(c, cc, t):
					found = c
					break
		d += 1
	return found

def findMinHueDist(continuities, wantedNumber, minHueDist, possibles):
	currentNumber = 0
	iterations = 0
	colors = []
	estimateStepComplete = wantedNumber == None
	done = False
	foundEqual = False
	foundLimit = False
	while not done and iterations < 100:
		estimate = 0
		currentNumber = 0
		colors = []
		for ci in range(len(continuities)):
			cont = continuities[ci]
			highH = cont[1]
			if len(continuities) > 1:
				nextCI = (ci + 1) % len(continuities)
				nextCont = continuities[nextCI]
				highH = min(cont[1], nextCont[0] - minHueDist) % 360
			a = cont[0]
			b = cont[1]
			length = angleDist(a, highH)
			divisions = floor(length / minHueDist)
			# print(a, b, highH, length, divisions)
			if estimateStepComplete:
				if divisions == 0:
					hue = int(a + (length / 2)) % 360
					currentNumber += 1
					colors.append(possibles[hue])
				else:
					step = int(length / divisions)
					for n in range(0, length+1, step):
						hue = (a + n) % 360
						currentNumber += 1
						colors.append(possibles[hue])
			else:
				estimate += 1 + divisions
		if wantedNumber == None:
			return colors
		if estimateStepComplete:
			if currentNumber == wantedNumber:
				foundEqual = True
				if foundLimit:
					print(iterations, "final:", minHueDist)
					return colors
				else:
					minHueDist += 1
			if currentNumber > wantedNumber:
				minHueDist += 1
			elif currentNumber < wantedNumber:
				minHueDist -= 1
				if foundEqual:
					foundLimit = True
		else:
			if estimate == wantedNumber:
				print(iterations, "estimate:", minHueDist)
				estimateStepComplete = True
			elif estimate > wantedNumber:
				minHueDist += 1
			elif estimate < wantedNumber:
				minHueDist -= 1
		iterations += 1
			

def generatePalette(lightness, chroma, t, lightnessT, minHueDist):
	possibles = {}
	edges = []
	continuities = []
	colors = []
	prevPossible = True
	for hue in range(361):
		c = findGoodLightness(lightness, chroma, hue, t, lightnessT)
		if c:
			# print(hue, c.lch_l)
			possibles[hue] = c
			if prevPossible == False:
				edges.append([c, 1])
			prevPossible = c
		else:
			if prevPossible != False and hue != 0:
				edges.append([prevPossible, 0])
			prevPossible = False
	for i in range(len(edges)):
		e = edges[i]
		nextI = i + 1
		if nextI == len(edges):
			nextI = 0
		prevI = i - 1
		if prevI == -1:
			prevI = len(edges) - 1
		nextE = edges[nextI]
		prevE = edges[prevI]
		print(int(e[0].lch_h), e[1])
		if e[1] == 1 and nextE[1] == 0:
			continuities.append([int(e[0].lch_h), int(nextE[0].lch_h)])
		elif i == 0 and e[1] == 0 and prevE[1] == 0:
			# if the continuity happens to begin right at hue 0
			continuities.append([0, int(e[0].lch_h)])
		elif i == len(edges) - 1 and e[1] == 1 and nextE[1] == 1:
			# if the continuity happens to end right at hue 360
			continuities.append([int(e[0].lch_h), 360])
	if len(edges) == 0:
		continuities = [[0, 360]]
	if type(minHueDist) == list:
		colors = findMinHueDist(continuities, minHueDist[0], 50, possibles)
	else:
		colors = findMinHueDist(continuities, None, minHueDist, possibles)
	for ci in range(len(colors)):
		c = colors[ci]
		hx = convert_color(c, sRGBColor).get_rgb_hex()
		print(int(c.lch_l), int(c.lch_c), int(c.lch_h), "\t", hx)
		colors[ci] = hx
	return colors

def assignColors(palettes):
	scopes = {}
	settings = {}
	for paletteName in palettes.keys():
		print('')
		print(paletteName)
		paletteDef = palettes.get(paletteName)
		paletteGroups = paletteDef.get('groups')
		palette = paletteDef.get('palette')
		if palette:
			pi = 0
			for g in paletteGroups:
				print(pi, palette[pi])
				if type(g) == dict:
					for key in g.keys():
						target = g.get(key)
						if target == '':
							target = paletteName
						if key in settingsKeys:
							settings[key] = palette[pi]
						else:
							if not scopes.get(key):
								scopes[key] = {}
							scopes[key][target] = palette[pi]
				elif type(g) == list:
					target = paletteName
					for key in g:
						if key in settingsKeys:
							settings[key] = palette[pi]
						else:
							if not scopes.get(key):
								scopes[key] = {}
							scopes[key][target] = palette[pi]
				pi = (pi + 1) % len(palette)
	return scopes, settings

def keyStringPair(parent, key, string):
	k = ET.SubElement(parent, 'key')
	k.text = key
	s = ET.SubElement(parent, 'string')
	s.text = string

tmThemeFile = 'generated.tmTheme'
if len(sys.argv) > 1:
	exec(open(sys.argv[1]).read())
if len(sys.argv) > 2:
	tmThemeFile = sys.argv[2]

# generate palettes from those that are parameters for the generator
for paletteName in palettes.keys():
	paletteDef = palettes.get(paletteName)
	palette = paletteDef.get('palette')
	if type(palette[0]) == int:
		if len(palette) == 4:
			palette.append([len(paletteDef['groups'])])
		palettes[paletteName]['palette'] = generatePalette(*palette)

scopes, settings = assignColors(palettes)

parser = ET.XMLParser(remove_blank_text=True)
tree = ET.parse('./empty.tmTheme', parser)
root = tree.getroot()
a = root.find('.//array')
# add settings
d = ET.SubElement(a, 'dict')
k = ET.SubElement(d, 'key')
k.text = 'settings'
sd = ET.SubElement(d, 'dict')
for key in settings.keys():
	keyStringPair(sd, key, settings.get(key))
for key in scopes.keys():
	targets = scopes.get(key)
	scoD = ET.SubElement(a, 'dict')
	keyStringPair(scoD, 'name', key)
	keyStringPair(scoD, 'scope', key)
	scoK3 = ET.SubElement(scoD, 'key')
	scoK3.text = 'settings'
	scoD2 = ET.SubElement(scoD, 'dict')
	for target in targets.keys():
		keyStringPair(scoD2, target, targets.get(target))
	fontStyle = fontStyles.get(key)
	if fontStyle:
		keyStringPair(scoD2, 'fontStyle', fontStyle)

tree.write(tmThemeFile, pretty_print=True)