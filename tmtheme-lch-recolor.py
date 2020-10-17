from colormath.color_objects import sRGBColor, LCHabColor
from colormath.color_conversions import convert_color
from lxml import etree as ET
import sys
from math import floor


tmTheme = sys.argv[1]

# the top-level dictionary index defines which palette to use, not whether to set the background or foreground
# whether to set background or foreground is determined by the value of the group dict. if the value is an empty string, the palette name will be used, or in the case of settings keys, not needed
# lists of names can include both scopes and names of settings keys
groups = {
	'comment' : [
		{'comment':'foreground', 'findHighlight':''}
	],
	'grayscale' : [
		['background', 'findHighlightForeGround', 'selectionBorder'],
		['selection', 'lineHighlight'],
		['stackGuide', 'invisibles'],
		['guide'],
		['activeGuide'],
		['foreground'],
		['caret']
	],
	'background' : [
		['meta.arrayindex, meta.item-access.arguments'],
		['string'],
		['entity.name.class', 'entity.name.function', 'entity.other.inherited-class'],
		{'variable.parameter':'', 'invalid':'foreground', 'invalid.deprecated':'foreground'}
	],
	'foreground' : [
		{'constant':'', 'invalid.deprecated':'background'},
		['variable, support.variable, meta.qualified-name, support.other.variable'],
		{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background'}
		{'entity.name.function':'background'}
		['storage.type', 'support.function', 'support.constant', 'support.class, support.type'], ,
		['meta.functioncall, meta.function-call'],
		['entity.other.attribute-name'],
	]
}

palettes = {
	'grayscale' : ['#ffffff', '#f1f1f1', '#d4d4d4', '#b9b9b9', '#777777', '#616161', '#303030'],
	'comment': ['#997A66'],
	'foreground': ['#CE4B44', '#0A7EBB', '#8969B2', '#B65395', '#038B3F', '#668302', '#AC6902', '#BD5C20'],
	'background': ['#FFF3F9','#E1FCEE','#E2FFD1','#FEF9B8'],
}

LCs= {
'foreground': [ [40, 100], [0, 0] ],
'background': [ [95, 15] ],
'Comment': [ [50, 20] ] 
}

settingsKeys = {'background', 'foreground', 'caret', 'invisibles', 'lineHighlight', 'selection', 'findHighlightForeGround', 'findHighlight', 'selectionBorder', 'guide', 'activeGuide', 'stackGuide'}

LCHs = {}
for key in palettes.keys():
	LCHs[key] = []
	for hex in palettes.get(key):
		LCHs[key].append(convert_color(sRGBColor(0,0,0).new_from_rgb_hex(hex), LCHabColor))

def tolerance(a, b, t):
	return abs(b - a) <= t

def LCHtolerance(a, b, t):
	return tolerance(a.lch_l, b.lch_l, t) and tolerance(a.lch_c, b.lch_c, t) and tolerance(a.lch_h, b.lch_h, t)

def outOfGamut(rgb):
	return rgb.clamped_rgb_r != rgb.rgb_r or rgb.clamped_rgb_g != rgb.rgb_g or rgb.clamped_rgb_b != rgb.rgb_b

def generatePalette(lightness, chroma, minHueDist, t):
	edges = []
	continuities = []
	colors = []
	countSinceEdge = 0
	prevPossible = True
	for hue in range(361):
		c = LCHabColor(lightness, chroma, hue)
		rgb = convert_color(c, sRGBColor)
		cc = convert_color(sRGBColor(rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b), LCHabColor)
		if not outOfGamut(rgb) and LCHtolerance(c, cc, t):
			# print(hue)
			if prevPossible == False:
				edges.append([c, 1])
				countSinceEdge = 0
			prevPossible = c
		else:
			if prevPossible != False and hue != 0:
				edges.append([prevPossible, 0])
				countSinceEdge = 0
			prevPossible = False
		countSinceEdge += 1
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
	for cont in continuities:
		a = cont[0]
		b = cont[1]
		length = b - a
		if b < a:
			bb = 360 + b
			length = bb - a
		capacity = 1 + floor(length / minHueDist)
		# print(a, b, length, capacity)
		if capacity == 1:
			hue = ((length / 2) + a) % 360
			colors.append(LCHabColor(lightness, chroma, hue))
		else:
			colors.append(LCHabColor(lightness, chroma, a))
			if capacity > 2:
				maximum = b
				if b < a:
					maximum = a + b
				for hue in range(a + minHueDist, maximum, minHueDist):
					hue = hue % 360
					colors.append(LCHabColor(lightness, chroma, hue))
			colors.append(LCHabColor(lightness, chroma, b))
	# hexes = []
	for c in colors:
		hex = convert_color(c, sRGBColor).get_rgb_hex()
		print(int(c.lch_h), hex)
		# hexes.append(hex)
	return colors

def recolorToPalette(hex, kind):
	lch = convert_color(sRGBColor(0,0,0).new_from_rgb_hex(hex), LCHabColor)
	bestDist = 1000
	bestColor = LCHabColor(0,0,0)
	for col in LCHs.get(kind):
		dist = abs(lch.lch_l - col.lch_l) + abs(lch.lch_c - col.lch_c) + abs(lch.lch_h - col.lch_h)
		if dist < bestDist:
			bestDist = dist
			bestColor = col
	if bestColor:
		nc = convert_color(bestColor, sRGBColor)
		return sRGBColor(nc.clamped_rgb_r, nc.clamped_rgb_g, nc.clamped_rgb_b).get_rgb_hex(), bestColor.lch_l, bestColor.lch_c, bestColor.lch_h

def recolorHue(hex, kind):
	lch = convert_color(sRGBColor(0,0,0).new_from_rgb_hex(hex), LCHabColor)
	bestDist = 200
	bestPair = []
	# print(lch.lch_l, lch.lch_c)
	for pair in LCs.get(kind):
		l = pair[0]
		c = pair[1]
		dist = abs(lch.lch_l - l) + (abs(lch.lch_c - c) / 3)
		# print(dist, pair)
		if dist < bestDist:
			bestDist = dist
			bestPair = pair
	if bestPair:
		nc = convert_color(LCHabColor(bestPair[0], bestPair[1], lch.lch_h), sRGBColor)
		# print(nc.clamped_rgb_r, nc.clamped_rgb_g, nc.clamped_rgb_b)
		if bestPair[1] == 100 and bestPair[0] > 0:
			re = convert_color(nc, LCHabColor)
			reC = 100 - re.lch_c
			reL = bestPair[0]
			while reC > 25 and reL < 100 and reL < bestPair[0] + 20:
				reL += 5
				re = convert_color(nc, LCHabColor)
				reC = 100 - re.lch_c
				print(bestPair[1], 'vs', int(re.lch_c), ': intensified')
				nc = convert_color(LCHabColor(reL, 100, lch.lch_h), sRGBColor)
		return sRGBColor(nc.clamped_rgb_r, nc.clamped_rgb_g, nc.clamped_rgb_b).get_rgb_hex(), int(bestPair[0]), int(bestPair[1]), int(lch.lch_h)

LCHs['foreground'] = generatePalette(41, 100, 5, 10)
print(' ')
LCHs['background'] = generatePalette(95, 10, 5, 360)

tree = ET.parse(tmTheme)
root = tree.getroot()
modified = False
for el in root.iter("string"):
	if el.text and el.text[:1] == '#':
		scope = False
		for e in el.getparent().getparent().iter("key"):
			if e.text == 'scope':
				scope = e.getprevious().text
				break
		if scope:
			print('    ' + el.text, scope)
			kind = el.getprevious().text
			if LCs.get(scope):
				kind = scope
			newHex, l, c, h = recolorToPalette(el.text, kind)
			if newHex:
				print(' -> ' + newHex, el.getprevious().text, l, c, h)
				el.text = newHex
				modified = True



if modified:
	tree.write('C:\\Users\\zoggop\\AppData\\Roaming\\Sublime Text 3\\Packages\\User\\recolored.tmTheme')

findRGBGamut(95, 10, None, 10)


