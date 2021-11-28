import coloraide
from lxml import etree as ET
import sys
from math import floor, ceil
import os

settingsKeys = {'background', 'foreground', 'caret', 'invisibles', 'lineHighlight', 'selection', 'findHighlightForeGround', 'findHighlight', 'selectionBorder', 'guide', 'activeGuide', 'stackGuide'}

defaultDirectory = '~/AppData/Roaming/Sublime Text 3/Packages/User/'

def angleDist(a, b):
	return abs(((b - a) + 180) % 360 - 180)

def findGoodLightness(lightness, chroma, hue, lightnessT):
	found = False
	d = 0
	while not found and d <= lightnessT:
		ls = [lightness + d]
		if d > 0:
			ls.append(lightness - d)
		for l in ls:
			c = coloraide.Color('lch-d65', [l, chroma, hue])
			rgb = c.convert('srgb')
			if rgb.in_gamut():
				found = c
				break
		d += 1
	return found

def findEquidistantHues(possibles, continuities, wantedNumber):
	e = 8
	firstHue = continuities[0][0]
	lastHue = firstHue - 1
	if lastHue < 0:
		lastHue = 360
	iterations = 0
	print(firstHue, lastHue)
	goodColors = None
	goodE = None
	wentOver = False
	while iterations < 200:
		colors = [possibles[firstHue]]
		done = False
		while not done:
			startH = int(colors[-1].h + 1)
			if startH == 361:
				startH = 0
			hue = startH
			while hue != int(colors[-1].h):
				c = possibles.get(hue)
				# print(hue, c)
				if c != None:
					deltaELast = colors[-1].delta_e(c, method='2000')
					deltaEFirst = colors[0].delta_e(c, method='2000')
					if min(deltaELast, deltaEFirst) >= e:
						colors.append(c)
						break
				hue = hue + 1
				if hue == 361:
					hue = 0
				if hue == lastHue:
					done = True
					break
		# print(iterations, e, len(colors), wantedNumber)
		if len(colors) > wantedNumber:
			if wentOver and goodColors != None:
				return goodColors
			else:
				e = e + int(len(colors) / wantedNumber)
		elif len(colors) < wantedNumber:
			wentOver = True
			e = e - 1
		elif len(colors) == wantedNumber:
			if wentOver and goodColors != None:
				return goodColors
			if goodColors == None or e > goodE:
				goodColors = colors
				goodE = e
			e = e + 0.1
		iterations = iterations + 1

def generateLinearPalette(**args):
	lightness = args.get('lightness')
	chroma = args.get('chroma')
	hue = args.get('hue')
	wantedNumber = args.get('wantedNumber')
	minDist = args.get('minDist')
	xMin = 0
	xMax = 100
	if args.get('xMin') != None:
		xMin = args.get('xMin')
	if args.get('xMax') != None:
		xMax = args.get('xMax')
	if hue == None or (lightness == None and chroma == None):
		return
	xVar = 'l'
	if lightness != None:
		xVar = 'c'
	colors = []
	xWidth = xMax - xMin
	if wantedNumber != None:
		minDist = xWidth / (wantedNumber - 1)
	x = xMin
	while x <= xMax:
		if xVar == 'l':
			lightness = x
		elif xVar == 'c':
			chroma = x
		c = coloraide.Color('lch-d65', [lightness, chroma, hue])
		hx = c.convert('srgb').to_string(hex=True)
		print(int(c.l), int(c.c), int(c.h), "\t", hx)
		colors.append(hx)
		x = x + minDist
	return colors

def generatePalette(**args):
	lightness = args.get('lightness')
	chroma = args.get('chroma')
	hue = args.get('hue')
	wantedNumber = args.get('wantedNumber')
	minHueDist = args.get('minHueDist')
	lightnessT = args.get('lightnessWidth')
	possibles = {}
	edges = []
	continuities = []
	colors = []
	prevPossible = True
	for hue in range(361):
		c = findGoodLightness(lightness, chroma, hue, lightnessT)
		if c:
			# print(hue, c.l)
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
		# print(int(e[0].h), e[1])
		if e[1] == 1 and nextE[1] == 0:
			continuities.append([int(e[0].h), int(nextE[0].h)])
		elif i == 0 and e[1] == 0 and prevE[1] == 0:
			# if the continuity happens to begin right at hue 0
			continuities.append([0, int(e[0].h)])
		elif i == len(edges) - 1 and e[1] == 1 and nextE[1] == 1:
			# if the continuity happens to end right at hue 360
			continuities.append([int(e[0].h), 360])
	if len(edges) == 0:
		continuities = [[0, 360]]
	print(continuities)
	if minHueDist == None:
		# colors = findMinHueDist(continuities, wantedNumber, 50, possibles)
		colors = findEquidistantHues(possibles, continuities, wantedNumber)
	else:
		colors = findMinHueDist(continuities, None, minHueDist, possibles)
	print(continuities, minHueDist, wantedNumber, len(possibles))
	for ci in range(len(colors)):
		c = colors[ci]
		hx = c.convert('srgb').to_string(hex=True)
		print(int(c.l), int(c.c), int(c.h), "\t", hx)
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
	tmThemeFile = os.path.expanduser(defaultDirectory + os.path.splitext(os.path.split(sys.argv[1])[-1])[0]+'.tmTheme')
	print(tmThemeFile)
if len(sys.argv) > 2:
	tmThemeFile = sys.argv[2]

# generate palettes from those that are parameters for the generator
for paletteName in palettes.keys():
	paletteDef = palettes.get(paletteName)
	palette = paletteDef.get('palette')
	if type(palette) == dict:
		if palette.get('minHueDist') == None and palette.get('minDist') == None:
			palette['wantedNumber'] = len(paletteDef['groups'])
		if palette.get('hue') == None:
			palettes[paletteName]['palette'] = generatePalette(**palette)
		else:
			palettes[paletteName]['palette'] = generateLinearPalette(**palette)

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