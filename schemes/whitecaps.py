### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'grayscale' : {
		'palette' : {'chroma':0, 'hue':0, 'xMin':0, 'xMax':100},
		'groups' : [
			['caret', 'foreground', 'variable.parameter'],
			['activeGuide'],
			['guide'],
			['stackGuide', 'invisibles'],
			['selection', 'lineHighlight'],
			['background', 'findHighlightForeGround', 'selectionBorder'],
		],
	},
	'background' : {
		'palette' : {'lightness':95, 'chroma':25, 'lightnessWidth':0},
		'groups' : [
			{'string':'', 'invalid':'foreground', 'invalid.deprecated':'foreground', 'markup.deleted':'', 'meta.separator':''},
			['entity.other.inherited-class', 'variable.function', 'entity.other.attribute-name'],
			['meta.arrayindex, meta.item-access.arguments', 'markup.inserted'],
			# ['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type', 'markup.italic', 'markup.bold'],
		]
	},
	'foreground' : {
		# 'palette' : {'lightness':33, 'chroma':131, 'lightnessWidth':0},
		'palette' : ['#0000ff', '#a00000'],
		'groups' : [
			# ['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type', 'markup.italic', 'markup.bold'],
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background', 'markup.heading':''},
			['entity.name.function', 'entity.name.class'], # 'meta.functioncall, meta.function-call', 'meta.function', 'variable.function', 'entity.other.attribute-name'
			# {'constant':''},
			# {'variable.parameter':'', 'invalid.deprecated':'background'},
			# ['variable, support.variable, meta.qualified-name, support.other.variable'],
		]
	},
	'comment' : {
		'palette' : {'lightness':40, 'chroma':25, 'lightnessWidth':0},
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
	'entity.name.class' : 'bold underline',
	'entity.name.function' : 'bold',
	'invalid' : 'bold',
	'invalid.deprecated' : 'bold',
	'markup.heading' : 'underline',
	'markup.italic' : 'italic',
	'markup.bold' : 'bold',
}

### END CONFIGURATION ###