import sys
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import math

resoultionMultiplier = 1

maxChroma = 0.4
pixelsPerChroma = 250
pixelsChroma = math.ceil(maxChroma * pixelsPerChroma)

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
	c = coloraide.Color('oklch', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return c
	return None

def rgb_to_lch(red, green, blue):
	c = coloraide.Color('srgb', [red/255, green/255, blue/255]).convert('oklch')
	if c.in_gamut():
		return c
	return None

def highestChromaColor(lightness, hue, stepStop=4):
	stepStop = 1 / (10 ** stepStop)
	chromaStep = 0.1
	if maxChroma < 0.1:
		chromaStep = 0.01
	chroma = maxChroma
	iteration = 0
	while iteration < 45:
		c = lch_to_rgb(lightness, chroma, hue)
		if not c is None:
			# print(chroma, chromaStep, stepStop)
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
	c = coloraide.Color('oklch', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return upscaleRGB(c.coords())
	else:
		return [0,0,0]

# def showColor(rgb):
	# return np.full([101, 101, 3], [int(rgb.clamped_rgb_r*255), int(rgb.clamped_rgb_g*255), int(rgb.clamped_rgb_b*255)], dtype=np.uint8), [0, 100, 0, 100]

def findRGBGamut(lightness, chroma, hue):
	extent = []
	aspect = 1
	rgbMap = None
	if lightness and chroma:
		extent = [0, 360, 0, 360]
		rgbMap = np.zeros([100, 360, 3], dtype=np.uint8)
		for hue in range(0, 360):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 100):
				rgbMap[y, hue] = rgb
	elif lightness and hue:
		extent = [0, maxChroma, 0, maxChroma]
		rgbMap = np.zeros([100, pixelsChroma, 3], dtype=np.uint8)
		for pixelChroma in range(0, pixelsChroma):
			chroma = pixelChroma / pixelsPerChroma
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 100):
				rgbMap[y, pixelChroma] = rgb
	elif chroma and hue:
		extent = [0, 1, 0, 1]
		rgbMap = np.zeros([100, 100, 3], dtype=np.uint8)
		for pixelLightness in range(0, 100):
			lightness = pixelLightness / 100
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 100):
				rgbMap[y, pixelLightness] = rgb
	elif lightness:
		extent = [0, 360, 0, maxChroma]
		aspect = 360 / maxChroma
		rgbMap = np.zeros([(pixelsChroma*resoultionMultiplier), 360, 3], dtype=np.uint8)
		for pixelChroma in np.arange(0, pixelsChroma, 1/resoultionMultiplier):
			chroma = pixelChroma / pixelsPerChroma
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(pixelChroma*resoultionMultiplier), hue] = rgb
	elif chroma:
		extent = [0, 360, 0, 1]
		aspect = 360
		rgbMap = np.zeros([100, 360, 3], dtype=np.uint8)
		for pixelLightness in range(0, 100):
			lightness = pixelLightness / 100
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[pixelLightness, hue] = rgb
	elif hue:
		extent = [0, maxChroma, 0, 1]
		aspect = maxChroma
		rgbMap = np.zeros([100*resoultionMultiplier, pixelsChroma*resoultionMultiplier, 3], dtype=np.uint8)
		for pixelLightness in np.arange(0, 100, 1/resoultionMultiplier):
			lightness = pixelLightness / 100
			for pixelChroma in np.arange(0, pixelsChroma, 1/resoultionMultiplier):
				chroma = pixelChroma / pixelsPerChroma
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(pixelLightness*resoultionMultiplier), int(pixelChroma*resoultionMultiplier)] = rgb
	else:
		return
	return rgbMap, extent, aspect

def localHueDelta(lightness, chroma, hue):
	hueA = (hue - 1) % 360
	hueB = (hue + 1) % 360
	colorA = coloraide.Color('oklch', [lightness, chroma, hueA])
	colorB = coloraide.Color('oklch', [lightness, chroma, hueB])
	return colorA.delta_e(colorB, method='2000')

def lowestCommonChroma(lightness):
	lowestCommonChroma = None
	for hue in range(0, 360):
		col = highestChromaColor(lightness, hue)
		chroma = col.convert('oklch').c
		if lowestCommonChroma is None or chroma < lowestCommonChroma:
			lowestCommonChroma = chroma
	return lowestCommonChroma

def measureHueDelta(lightness):
	rgbMap = np.zeros([100, 360, 3], dtype=np.uint8)
	doAvg = False
	if lightness > 1:
		doAvg = True
	deltas = []
	highestD = None
	lowestD = None
	if doAvg == True:
		lccs = {}
		for pixelLightness in range(1, 100):
			lightness = pixelLightness / 100
			lccs[pixelLightness] = lowestCommonChroma(lightness)
			print("lightness", lightness, lccs.get(pixelLightness), "lowest common chroma")
	chroma = lowestCommonChroma(lightness)
	for hue in range(0, 360):
		if doAvg == True:
			dSum = 0
			for pixelLightness in range(1, 100):
				lightness = pixelLightness / 100
				chroma = lccs.get(pixelLightness)
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
		lightness = 0.5
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
		for n in range(0, 100):
			if n == y:
				c = coloraide.Color('oklch', [lightness, chroma, h]).convert('srgb')
				rgbMap[n, h] = upscaleRGB(c.coords())
			else:
				rgbMap[n, h] = [0,0,0]
		h = h + 1
	lstring = str(lightness)
	if doAvg:
		lstring = 'avg'
	with open(os.path.expanduser('~/.oklch_rgb/perceptual_hues-l{}.py'.format(lstring)), "w") as fp:
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
				c = coloraide.Color('oklch', [lightness, chroma, hue]).convert('srgb')
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

def measureGamutStats(resL=100, resC=100, resH=360):
	maxL, maxC = 0, 0
	total, totalL, totalC = 0, 0, 0
	# rgbMapL = np.zeros([resL, resH, 3], dtype=np.uint8)
	# rgbMapC = np.zeros([resC, resH, 3], dtype=np.uint8)
	for pl in range(resL):
		l = pl / (resL - 1)
		for pc in range(resC):
			c = (pc / (resC - 1)) * 0.4
			for ph in range(resH):
				h = (ph / (resH - 1)) * 359
				col = coloraide.Color('oklch', [l, c, h]).convert('srgb')
				if col.in_gamut():
					total += 1
					totalL += l
					totalC += c
					if l > maxL:
						maxL = l
					if c > maxC:
						maxC = c
	avgL = totalL / total
	avgC = totalC / total
	print('{}/{} lightness avg/max'.format(avgL, maxL))
	print('{}/{} chroma avg/max'.format(avgC, maxC))

args = []
for arg in sys.argv[1:]:
	if arg.upper() == 'NONE':
		args.append(None)
	elif arg.upper() == 'STATS':
		args.append('stats')
	else:
		args.append(float(arg))

plt.style.use('dark_background')

startDT = datetime.datetime.now()
if len(args) == 3:
	rgbMap, extent, aspect = findRGBGamut(*args)
elif len(args) == 1:
	if args[0] == 'stats':
		measureGamutStats()
		exit()
	else:
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
# mng.window.state('zoomed')
plt.show()