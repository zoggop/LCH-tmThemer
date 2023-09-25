### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'grayscale' : {
		'palette' : {'chroma':0, 'hue':0, 'tolerance':1000, 'xMin':23, 'gamutCheck':False},
		'groups' : [
			['caret'],
			['foreground'],
			['activeGuide'],
			['guide'],
			['stackGuide', 'invisibles'],
			['selection', 'lineHighlight'],
			['background', 'findHighlightForeGround', 'selectionBorder'],
		],
	},
	'background' : {
		'palette' : {'lightness':95, 'chroma':20, 'tolerance':10, 'lightnessWidth':0},
		'groups' : [
			{'string':'', 'invalid':'foreground', 'invalid.deprecated':'foreground', 'markup.deleted':''},
			['entity.name.class', 'entity.other.inherited-class'],
			['meta.arrayindex, meta.item-access.arguments', 'markup.inserted'],
		]
	},
	'foreground' : {
		# 'palette' : {'lightness':52, 'chroma':85, 'tolerance':5, 'lightnessWidth':0},
		'palette' : ['#e00096', '#d10000', '#008b00', '#0051fc', '#9e05d6'],
		'groups' : [
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background'},
			{'variable.parameter':'', 'invalid.deprecated':'background'},
			['meta.function', 'variable.function', 'entity.other.attribute-name', 'entity.name.function'], # 'meta.functioncall, meta.function-call'
			['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type'],
			{'constant':''},
			# ['variable, support.variable, meta.qualified-name, support.other.variable'],
		]
	},
	'comment' : {
		'palette' : {'lightness':50, 'chroma':15, 'tolerance':5, 'lightnessWidth':0},
		'groups' : [
			[],
			{'comment':'foreground', 'findHighlight':''},
			[],
			[],
			[],
			[],
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
	'entity.name.function' : 'bold',
	'invalid' : 'bold',
	'invalid.deprecated' : 'bold',
}

### END CONFIGURATION ###