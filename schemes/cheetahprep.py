### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'grayscale' : {
		'palette' : {'chroma':0, 'hue':0, 'xMin':15, 'xMax':65, 'wantedNumber':4},
	},
	'background' : {
		'palette' : {'lightness':25, 'chroma':46, 'lightnessWidth':0, 'wantedNumber':3},
	},
	'foreground' : {
		'palette' : {'lightness':65, 'chroma':54, 'lightnessWidth':0, 'wantedNumber':6},
	},
	'comment' : {
		'palette' : {'lightness':55, 'chroma':24, 'lightnessWidth':0, 'wantedNumber':6},
	}
}
### END CONFIGURATION ###