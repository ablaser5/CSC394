# Utility file for form interaction
from flask import request

# Takes empty dictionary and fills with data from the form
def loadForm(d):
	for key in request.form:
		if not key == 'submit':
			d[key] = request.form[key]
	return d

# Takes a dictionary with data and checks there are empty fields
def checkEmptyForm(d):
	errors = 0
	for key in d:
		if d[key] == '' or d[key] == ' ':
			errors += 1
	return errors > 0