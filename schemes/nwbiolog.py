### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette

configuration = {
	'name' : 'nwbiolog',
	'type' : 'json', # for Windows Terminal
}

palettes = {
	'colors' : {
		'palette' : {'lightness':85, 'chroma':21, 'startHue':10},
		'groups' : [
			['red'],
			['yellow'],
			['green'],
			['blue'],
		]
	},
}

fontStyles = {
}

### END CONFIGURATION ###