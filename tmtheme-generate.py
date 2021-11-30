import coloraide
from lxml import etree as ET
import sys
from math import floor, ceil
import os

settingsKeys = {'background', 'foreground', 'caret', 'invisibles', 'lineHighlight', 'selection', 'findHighlightForeGround', 'findHighlight', 'selectionBorder', 'guide', 'activeGuide', 'stackGuide'}

defaultDirectory = '~/AppData/Roaming/Sublime Text 3/Packages/User/'

maxChroma = 134

def angleDist(a, b):
	return abs(((b - a) + 180) % 360 - 180)

def lch_to_rgb(lightness, chroma, hue):
	c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return c
	return None

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

def highestChromaColor(lightness, hue):
	for chroma in range(maxChroma, 0, -1):
		c = lch_to_rgb(lightness, chroma, hue)
		if not c is None:
			if chroma < maxChroma:
				decaChroma = chroma + 0.9
				while decaChroma >= chroma:
					dc = lch_to_rgb(lightness, decaChroma, hue)
					if not dc is None:
						centiChroma = decaChroma + 0.09
						while centiChroma >= decaChroma:
							cc = lch_to_rgb(lightness, centiChroma, hue)
							if not cc is None:
								return cc
							centiChroma -= 0.01
					decaChroma -= 0.1
			else:
				return c

def findEquidistantHues(possibles, continuities, wantedNumber):
	e = 49
	firstHue = continuities[0][0]
	lastHue = firstHue - 1
	if lastHue < 0:
		lastHue = 360
	iterations = 0
	print(firstHue, lastHue)
	goodColors = None
	goodE = None
	eStep = 10
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
		if len(colors) < wantedNumber:
			e -= eStep
		elif len(colors) == wantedNumber:
			if goodColors == None or e > goodE:
				goodColors = colors
				goodE = e
			if eStep == 0.01:
				print(iterations, "found deltae interval:", '{:.2f}'.format(e))
				return goodColors
			e += eStep
			eStep = eStep / 10
			e -= eStep
		elif len(colors) > wantedNumber:
			if eStep <= 0.01 and not goodColors is None:
				return goodColors
			e += eStep
			eStep = eStep / 10
			e -= eStep
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
	print(wantedNumber, minDist, xMin, xMax)
	while True:
		if xVar == 'l':
			lightness = x
		elif xVar == 'c':
			chroma = x
		c = coloraide.Color('lch-d65', [lightness, chroma, hue])
		hx = c.convert('srgb').to_string(hex=True)
		print(int(c.l), int(c.c), int(c.h), "\t", hx)
		colors.append(hx)
		if x == xMax:
			break
		x = min(xMax, x + minDist)
	return colors

def generatePalette(**args):
	lightness = args.get('lightness')
	chroma = args.get('chroma')
	hue = args.get('hue')
	wantedNumber = args.get('wantedNumber')
	minHueDist = args.get('minHueDist')
	lightnessT = args.get('lightnessWidth')
	hues = args.get('hues')
	if not hues is None:
		huesPalette = palettes.get(hues)
		if not huesPalette is None:
			colors = []
			for colorHex in huesPalette.get('palette'):
				h = coloraide.Color(colorHex).convert('lch-d65').h
				if chroma == None:
					c = highestChromaColor(lightness, h).convert('lch-d65')
				else:
					c = findGoodLightness(lightness, chroma, h, lightnessT)
				hx = c.convert('srgb').to_string(hex=True)
				print(int(c.l), int(c.c), int(c.h), "\t", hx)
				colors.append(hx)
			return colors
	startHue = args.get('startHue') or 0
	endHue = startHue - 1
	if endHue == -1:
		endHue = 360
	possibles = {}
	edges = []
	continuities = []
	colors = []
	prevPossible = True
	for hue in range(361):
		if chroma == None:
			c = highestChromaColor(lightness, hue).convert('lch-d65')
		else:
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
		continuities = [[startHue, endHue]]
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

def assignJsonColors(palettes):
	scheme = {}
	for paletteName in palettes.keys():
		paletteDef = palettes.get(paletteName)
		paletteGroups = paletteDef.get('groups')
		palette = paletteDef.get('palette')
		if palette:
			pi = 0
			for g in paletteGroups:
				for key in g:
					scheme[key] = palette[pi]
				pi = (pi + 1) % len(palette)
	return scheme

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

if not configuration is None:
	if configuration.get('type') == 'json':
		scheme = assignJsonColors(palettes)
		scheme['name'] = configuration.get('name')
		import json
		fp = open(os.path.expanduser(os.path.splitext(os.path.split(sys.argv[1])[-1])[0]+'.json'), 'w')
		json.dump(scheme, fp, sort_keys=True, indent=4, separators=(',', ': '))
		fp.close()
		# print(scheme)
		exit()
	elif configuration.get('type') == 'Windows Terminal':
		newScheme = assignJsonColors(palettes)
		newScheme['name'] = configuration.get('name')
		import json
		settingsPath = os.path.expanduser('~/AppData/Local/Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json')
		fp = open(settingsPath)
		settings = json.load(fp)
		fp.close()
		schemes = settings.get('schemes')
		for si in range(len(schemes)):
			scheme = schemes[si]
			name = scheme.get('name')
			if name == configuration.get('name'):
				schemes[si] = newScheme
		fp = open(settingsPath, 'w')
		json.dump(settings, fp, sort_keys=True, indent=4, separators=(',', ': '))
		fp.close()
		exit()

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