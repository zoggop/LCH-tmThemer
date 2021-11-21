import coloraide
from lxml import etree as ET
import sys
from math import floor, ceil

settingsKeys = {'background', 'foreground', 'caret', 'invisibles', 'lineHighlight', 'selection', 'findHighlightForeGround', 'findHighlight', 'selectionBorder', 'guide', 'activeGuide', 'stackGuide'}

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

def findMinHueDist(continuities, wantedNumber, minHueDist, possibles):
	currentNumber = 0
	iterations = 0
	colors = []
	estimateStepComplete = wantedNumber == None
	done = False
	foundEqual = False
	foundLimit = False
	lastNumber = 500
	lastEstimate = 500
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
				nextX = nextCont[0] - minHueDist
				if nextX < 0:
					nextX += 360
				# highH = max(cont[0], min(cont[1], nextX))
				# highH = min(cont[1], nextX)
			a = cont[0]
			if highH < a:
				highH = highH + 360
			length = highH - a
			# print(length, cont, a, highH)
			divisions = floor(length / minHueDist)
			if estimateStepComplete:
				if divisions == 0:
					hue = int(a + (length / 2)) % 360
					currentNumber += 1
					colors.append(possibles[hue])
				else:
					step = int(length / divisions)
					# print(a, b, highH, length, divisions)
					for n in range(0, length+1, step):
						hue = (a + n) % 360
						currentNumber += 1
						# print(n, hue, currentNumber, divisions,step, length)
						colors.append(possibles[hue])
			else:
				estimate += 1 + divisions
		if wantedNumber == None:
			return colors
		if estimateStepComplete:
			if currentNumber == wantedNumber or (currentNumber > wantedNumber and lastNumber < wantedNumber):
				if not foundEqual:
					foundEqual = iterations
					# print(foundEqual, iterations)
				if foundLimit or foundEqual == iterations - 5:
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
			lastNumber = currentNumber
		else:
			if estimate == wantedNumber or (estimate > wantedNumber and lastEstimate < wantedNumber):
				print(iterations, "estimate:", minHueDist, estimate, wantedNumber)
				estimateStepComplete = True
			elif estimate > wantedNumber:
				minHueDist += 1
			elif estimate < wantedNumber:
				minHueDist -= 1
			lastEstimate = estimate
		iterations += 1

def findMinDist(continuities, wantedNumber, minDist, possibles):
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
			highX = cont[1]
			if len(continuities) > 1 and ci != len(continuities) - 1:
				nextCont = continuities[ci + 1]
				highX = min(cont[1], nextCont[0] - minDist)
			a = cont[0]
			length = highX - a
			if length > 0:
				divisions = floor(length / minDist)
				# print(a, b, highH, length, divisions)
				if estimateStepComplete:
					if divisions == 0:
						x = int(a + (length / 2))
						currentNumber += 1
						colors.append(possibles[x])
					else:
						step = int(length / divisions)
						xs = []
						for x in range(a, highX, step):
							xs.append(x)
						for xi in range(0, len(xs)):
							x = xs[xi]
							if xi == len(xs) - 1:
								x = highX
							currentNumber += 1
							colors.append(possibles[x])
				else:
					estimate += 1 + divisions
		if wantedNumber == None:
			return colors
		if estimateStepComplete:
			if currentNumber == wantedNumber:
				foundEqual = True
				if foundLimit:
					print(iterations, "final:", minDist)
					return colors
				else:
					minDist += 1
			if currentNumber > wantedNumber:
				minDist += 1
			elif currentNumber < wantedNumber:
				minDist -= 1
				if foundEqual:
					foundLimit = True
		else:
			if estimate == wantedNumber:
				print(iterations, "estimate:", minDist)
				estimateStepComplete = True
			elif estimate > wantedNumber:
				minDist += 1
			elif estimate < wantedNumber:
				minDist -= 1
		iterations += 1

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
	possibles = {}
	edges = []
	continuities = []
	colors = []
	prevPossible = True
	for x in range(xMin, xMax+1):
		if xVar == 'l':
			lightness = x
		elif xVar == 'c':
			chroma = x
		c = coloraide.Color('lch-d65', [lightness, chroma, hue])
		rgb = c.convert('srgb')
		if rgb.in_gamut():
			possibles[x] = c
			if prevPossible == False:
				edges.append([c, 1])
			prevPossible = c
		else:
			if prevPossible != False and x != xMin:
				edges.append([prevPossible, 0])
				prevPossible = False
	for i in range(len(edges)):
		e = edges[i]
		nextE = None
		if i < len(edges)-2:
			nextE = edges[e+1]
		if e[1] == 1 and nextE and nextE[1] == 0:
				continuities.append([int(getattr(e[0], xVar)), int(getattr(nextE[0], xVar))])
		elif i == 0 and e[1] == 0:
			# if the continuity happens to begin at minimum x
			continuities.append([xMin, int(getattr(e[0], xVar))])
		elif i == len(edges) - 1 and e[1] == 1:
			# if the continuity happens to end at maximum x
			continuities.append([int(getattr(e[0], xVar)), xMax])
	if len(edges) == 0:
		continuities = [[xMin, xMax]]
	if wantedNumber != None:
		colors = findMinDist(continuities, wantedNumber, 50, possibles)
	elif minDist != None:
		colors = findMinDist(continuities, None, minDist, possibles)
	for ci in range(len(colors)):
		c = colors[ci]
		hx = c.convert('srgb').to_string(hex=True)
		print(int(c.l), int(c.c), int(c.h), "\t", hx)
		colors[ci] = hx
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
		colors = findMinHueDist(continuities, wantedNumber, 50, possibles)
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