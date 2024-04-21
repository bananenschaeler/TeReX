import re

def link_to_id(link):
	sub = link.split("abs/",1)[1]
	if "v" in sub:
		sub = sub.split("v",1)[0]
	return sub
