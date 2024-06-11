import sys
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os

resoultionMultiplier = 1

maxChroma = 132

lch2rgbMap = None

# create path if not existant
if not os.path.exists(os.path.expanduser('~/.lch_rgb')):
	os.makedirs(os.path.expanduser('~/.lch_rgb'))

# load saved mappings if available
if os.path.exists(os.path.expanduser('~/.lch_rgb/map-lch2rgb.pickle')):
	startDT = datetime.datetime.now()
	import pickle
	with open(os.path.expanduser('~/.lch_rgb/map-lch2rgb.pickle'), "rb") as fp:
		lch2rgbMap = pickle.load(fp)
	fp.close()
	print("loaded pickle in", datetime.datetime.now() - startDT)
else:
	startDT = datetime.datetime.now()
	# from colour import XYZ_to_sRGB, Lab_to_XYZ, LCHab_to_Lab
	import coloraide
	print("imported conversions in", datetime.datetime.now() - startDT)

def angleDist(a, b):
	return abs(((b - a) + 180) % 360 - 180)

def upscaleRGB(rgb):
	newRGB = []
	for component in rgb:
		newRGB.append(round(min(1,max(0,component))*255))
	return newRGB

def lch_to_rgb(lightness, chroma, hue):
	c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return c
	return None

def rgb_to_lch(red, green, blue):
	c = coloraide.Color('srgb', [red/255, green/255, blue/255]).convert('lch-d65')
	if c.in_gamut():
		return c
	return None

def highestChromaColor(lightness, hue, stepStop=2):
	stepStop = 1 / (10 ** stepStop)
	chromaStep = 10
	if maxChroma < 10:
		chromaStep = 1
	chroma = maxChroma
	iteration = 0
	while iteration < 45:
		c = lch_to_rgb(lightness, chroma, hue)
		if not c is None:
			if chromaStep == stepStop or maxChroma == 0:
				return c
			else:
				chroma += chromaStep
				chromaStep /= 10
				chroma -= chromaStep
		chroma = max(0, chroma - chromaStep)
		iteration += 1
	print(chromaStep, lightness, chroma, hue, iteration)

def gamutPixel(lightness, chroma, hue):
	c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return upscaleRGB(c.coords())
	else:
		return [0,0,0]

# def showColor(rgb):
	# return np.full([101, 101, 3], [int(rgb.clamped_rgb_r*255), int(rgb.clamped_rgb_g*255), int(rgb.clamped_rgb_b*255)], dtype=np.uint8), [0, 100, 0, 100]

def findRGBGamut(lightness, chroma, hue):
	extent = []
	rgbMap = None
	if lightness and chroma:
		extent = [0, 360, 0, 101]
		rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
		for hue in range(0, 360):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, hue] = rgb
	elif lightness and hue:
		extent = [0, maxChroma+1, 0, 101]
		rgbMap = np.zeros([101, maxChroma+1, 3], dtype=np.uint8)
		for chroma in range(0, maxChroma+1):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, chroma] = rgb
	elif chroma and hue:
		extent = [0, 101, 0, 101]
		rgbMap = np.zeros([101, 101, 3], dtype=np.uint8)
		for lightness in range(0, 101):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, lightness] = rgb
	elif lightness:
		extent = [0, 360, 0, maxChroma+1]
		rgbMap = np.zeros([((maxChroma+1)*resoultionMultiplier), 360, 3], dtype=np.uint8)
		for chroma in np.arange(0, maxChroma+1, 1/resoultionMultiplier):
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(chroma*resoultionMultiplier), hue] = rgb
	elif chroma:
		extent = [0, 360, 0, 101]
		rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
		for lightness in range(0, 101):
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[lightness, hue] = rgb
	elif hue:
		extent = [0, maxChroma+1, 0, 101]
		rgbMap = np.zeros([101*resoultionMultiplier, ((maxChroma+1)*resoultionMultiplier), 3], dtype=np.uint8)
		for lightness in np.arange(0, 101, 1/resoultionMultiplier):
			for chroma in np.arange(0, maxChroma+1, 1/resoultionMultiplier):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(lightness*resoultionMultiplier), int(chroma*resoultionMultiplier)] = rgb
	else:
		return
	return rgbMap, extent

def gamutScatterPlot():
	gamutMap = {}
	Ls = []
	Cs = []
	Hs = []
	RGBs = []
	for lightness in range(100):
		for chroma in range(maxChroma):
			for hue in range(1, 360):
				address = '{} {} {}'.format(lightness, chroma, hue)
				# c = lchColor(lightness, chroma, hue, illuminant='D65')
				# rgb = convert_color(c, sRGBColor)
				c = [lightness, chroma, hue]
				colour.convert(c, 'LCHab', 'sRGB')
				if not outOfGamut(rgb) and lchTolerance(c, convert_color(rgb, lchColor)):
					gamutMap[address] = 1
					prevL = '{} {} {}'.format(lightness-1, chroma, hue)
					prevC = '{} {} {}'.format(lightness, chroma-1, hue)
					prevH = '{} {} {}'.format(lightness, chroma, hue-1)
					if gamutMap.get(prevL) == 0 or gamutMap.get(prevC) == 0 or gamutMap.get(prevH) == 0:
						Ls.append(lightness)
						Cs.append(chroma)
						Hs.append(hue)
						RGBs.append([rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b])
				else:
					gamutMap[address] = 0
	print(len(Ls))
	return Ls, Cs, Hs, RGBs

def localHueDelta(lightness, chroma, hue):
	hueA = (hue - 1) % 360
	hueB = (hue + 1) % 360
	colorA = coloraide.Color('lch-d65', [lightness, chroma, hueA])
	colorB = coloraide.Color('lch-d65', [lightness, chroma, hueB])
	return colorA.delta_e(colorB, method='2000')

def lowestCommonChroma(lightness):
	lowestCommonChroma = None
	for hue in range(0, 360):
		col = highestChromaColor(lightness, hue, 0)
		chroma = col.convert('lch-d65').c
		if lowestCommonChroma is None or chroma < lowestCommonChroma:
			lowestCommonChroma = chroma
	return lowestCommonChroma

def measureHueDelta(lightness):
	rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
	doAvg = False
	if lightness > 100:
		doAvg = True
	deltas = []
	highestD = None
	lowestD = None
	if doAvg == True:
		lccs = {}
		for lightness in range(1, 100):
			lccs[lightness] = lowestCommonChroma(lightness)
			print("lightness", lightness, lccs.get(lightness), "lowest common chroma")
	chroma = lowestCommonChroma(lightness)
	for hue in range(0, 360):
		if doAvg == True:
			dSum = 0
			for lightness in range(1, 100):
				chroma = lccs.get(lightness)
				dSum += localHueDelta(lightness, chroma, hue)
			delta = dSum / 99
		else:
			delta = localHueDelta(lightness, chroma, hue)
		deltas.append(delta)
		if lowestD == None or delta < lowestD:
			lowestD = delta
		if highestD == None or delta > highestD:
			highestD = delta
		print(hue, delta)
	if doAvg == True:
		lightness = 50
		chroma = lccs.get(50)
	deltaRange = highestD - lowestD
	deltaMult = 100 / deltaRange
	freqMult = 10 / (highestD - lowestD)
	print(lowestD, highestD, deltaRange)
	extent = [0, 360, lowestD, highestD]
	perceptualHues = []
	h = 0
	for d in deltas:
		freq = round((d - lowestD) * freqMult) + 1
		for f in range(0, freq):
			perceptualHues.append(h)
		y = int((d - lowestD) * deltaMult)
		for n in range(0, 101):
			if n == y:
				c = coloraide.Color('lch-d65', [lightness, chroma, h]).convert('srgb')
				rgbMap[n, h] = upscaleRGB(c.coords())
			else:
				rgbMap[n, h] = [0,0,0]
		h = h + 1
	lstring = str(lightness)
	if doAvg:
		lstring = 'avg'
	with open(os.path.expanduser('~/.lch_rgb/perceptual_hues-l{}.py'.format(lstring)), "w") as fp:
		fp.write(str(perceptualHues))
	return rgbMap, extent

def measureHSVhueShift():
	rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
	deltas = []
	highestD = None
	lowestD = None
	for hue in range(1, 360):
		lowestHSVhue = None
		highestHSVhue = None
		for lightness in range(10, 91, 5):
			# c = highestChromaColor(lightness, hue)
			for chroma in range(5, 136, 5):
				c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
				if c.in_gamut():
					HSVhue = c.convert('hsv').h
					if lowestHSVhue == None or HSVhue < lowestHSVhue:
						lowestHSVhue = HSVhue
					if highestHSVhue == None or HSVhue > highestHSVhue:
						highestHSVhue = HSVhue
		delta = angleDist(lowestHSVhue, highestHSVhue)
		deltas.append(delta)
		if lowestD == None or delta < lowestD:
			lowestD = delta
		if highestD == None or delta > highestD:
			highestD = delta
		print(hue, delta)
	deltaRange = highestD - lowestD
	deltaMult = 100 / deltaRange
	print(lowestD, highestD, deltaRange)
	extent = [0, 360, lowestD, highestD]
	h = 1
	for d in deltas:
		y = int((d - lowestD) * deltaMult)
		for n in range(0, 101):
			if n == y:
				c = highestChromaColor(50, h)
				rgbMap[n, h] = upscaleRGB(c.coords())
			else:
				rgbMap[n, h] = [0,0,0]
		h = h + 1
	return rgbMap, extent

args = []
for arg in sys.argv[1:]:
	if arg.upper() == 'NONE':
		args.append(None)
	else:
		args.append(int(arg))

plt.style.use('dark_background')

# >>> coloraide.Color('srgb', [1,0,0]).convert('lch-d65')
# color(--lch-d65 53.237% 104.55 40 / 1)
# >>> coloraide.Color('srgb', [0,1,0]).convert('lch-d65')
# color(--lch-d65 87.736% 119.78 136.01 / 1)
# >>> coloraide.Color('srgb', [0,0,1]).convert('lch-d65')
# color(--lch-d65 32.301% 133.81 306.29 / 1)
# >>> coloraide.Color('srgb', [0,1,1]).convert('lch-d65')
# color(--lch-d65 91.115% 50.112 196.38 / 1)
# >>> coloraide.Color('srgb', [1,0,1]).convert('lch-d65')
# color(--lch-d65 60.323% 115.55 328.23 / 1)
# >>> coloraide.Color('srgb', [1,1,0]).convert('lch-d65')
# color(--lch-d65 97.139% 96.912 102.85 / 1)

startDT = datetime.datetime.now()
if len(args) == 3:
	aspect = 1
	rgbMap, extent = findRGBGamut(*args)
elif len(args) == 1:
	rgbMap, extent = measureHueDelta(args[0])
	aspect = 180 / (extent[3] - extent[2])
	print(aspect)
else:
	aspect = 6
	rgbMap, extent = measureHSVhueShift()
print('created image map in', datetime.datetime.now() - startDT)

fig, ax = plt.subplots()
im = ax.imshow(rgbMap, interpolation='nearest', cmap=None, origin='lower', extent=extent, aspect=aspect)

mng = plt.get_current_fig_manager()
plt.show()