from mako.template import Template


# @todo: rewrite this
def render(template, dct=None, **kwargs):
	if dct is None:
		dct= {}

	dct= { x.upper():y for x,y in dct.items() }
	dct.update({ x.upper():y for x,y in kwargs.items() })

	try:
		return Template(template).render(**dct)
	except:
		from mako import exceptions
		print(exceptions.text_error_template().render())
		raise