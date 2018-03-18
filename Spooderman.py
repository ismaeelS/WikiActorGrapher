#-*- coding: utf-8 -*-
import urllib2
import unicodedata
import re
import json
from bs4 import BeautifulSoup

numberOfActors = 0
numberOfFilms = 0
actorsNeeded = 250
filmsNeeded = 125

foundEnoughActors = False
foundEnoughFilms = False

prototype = []
actorNamesAdded = []
filmNamesAdded = []
baseURL = 'https://en.wikipedia.org'

repeatZ = []

#stop at 125/250 actors/movies
#take care of repeat names
#take care of lists/tables
#actors/movies w/o wiki pages

def main():
	global prototype

	print("#########################")

	actorToGraph("Morgan Freeman", '/wiki/Morgan_Freeman')
	# print("GRAPH AFTER ADDING MORGAN FREEMAN PAGE")
	# printGraph()

	completeGraph("Movies")
	# print("GRAPH AFTER COMPLETING MOVIES")
	# printGraph()

	completeGraph("Actors")
	# print("GRAPH AFTER COMPLETING ACTORS")
	printGraph()

	# createJSON()


def printGraph():
	print("printGraph")
	global prototype
	global repeatZ

	showEverything = True
	printAnything = False
	printAllNodes = True
	graphsubset = prototype
	nodeIndex = 0

	if (showEverything):
		for node in prototype:
			if (node.__class__.__name__ == "Actor"):
				for role in node.roles:
					print(node.name, node.age, " starred in ", role)
			elif (node.__class__.__name__ == "Film"):
				for castmember in node.cast:
					print(node.name, node.gross, " starred ", castmember)
			else:
				print("Warning ", node.name, " is not an actor or a film")
	else:	
		if (printAllNodes == False):
			graphsubset = prototype[nodeIndex].roles
			print prototype[nodeIndex].name

		if (printAnything):
			for node in graphsubset:
				try:
					print(node.name)
				except Exception as e:
					print("Could not print this one")
				else:
					pass
				finally:
					pass
				

	print(numberOfActors, numberOfFilms, actorNamesAdded, filmNamesAdded)

def actorToGraph(actorName, actorHREF):
	print("Enter MF Page")
	global prototype
	global baseURL
	global actorNamesAdded
	global filmNamesAdded

	global repeatZ

	if (actorName not in actorNamesAdded):
		actorURL = baseURL + actorHREF
		actorPage = urllib2.urlopen(actorURL)
		actorSoup = BeautifulSoup(actorPage, 'html.parser')

		age = formatAge(actorSoup)

		currentActor = Actor(actorName, age, actorHREF)

		prototype.append(currentActor) #check before or after adding movies
		actorNamesAdded.append(actorName)

		actorFilmsUL = actorSoup.find('span', id = 'Filmography').parent #check table vs list
		actorFilmsLI = actorFilmsUL.find_next('ul').find_all('li') #this part too

		for movie in actorFilmsLI:
			title = movie.text
			if (title not in filmNamesAdded):
				gross = -1
				flick = Film(title, gross, movie.find('a')["href"])
				# flickToGraph = Film(title, gross, movie.find('a')["href"])
				flick.addActor(currentActor.name)
				# flickToGraph.addActor(currentActor)
				currentActor.addFilm(flick.name) #need to check if film already exists
				prototype.append(flick)
				filmNamesAdded.append(title)
				# print(len(prototype), currentActor.name, len(currentActor.roles))
			else:
				repeatZ.append(title)
				# print(title, " not added to ", currentActor)
	else:
		repeatZ.append(actorName)
		# print(actorName, " not added to prototype")
		

def completeGraph(theType):
	print("completeGraph() with ", theType)
	global prototype
	global baseURL
	global actorNamesAdded
	global filmNamesAdded
	global repeatZ

	global foundEnoughActors

	if (theType == "Movies"):
		for node in prototype:
			if (node.__class__.__name__ == "Film"):
				if (node.href == "None"): #Movie has no wiki page
					continue
				elif (node.gross == -1):
				# elif (node.name == "Lean on Me (1989)"): #(node.name == "Lean on Me (1989)"): #gross == -1 HALP
					# print("Looking at ", node.name)
					movieHREF = node.href
					moviePage =  urllib2.urlopen(baseURL + movieHREF)
					movieSoup = BeautifulSoup(moviePage, 'html.parser')
					
					gross = movieSoup.find('table', {"class": "infobox vevent"}).find_all('tr') #process gross properly
					gross = gross[-1].find('td').text
					gross = formatGross(gross)
					node.gross = gross

					filmActorsUL = movieSoup.find('span', id = 'Cast').parent #check table vs list
					filmActorsLI = filmActorsUL.find_next('ul').find_all('li')

					# print("start of ", node.name)
					for actor in filmActorsLI:
						if (foundEnoughActors):
							return

						age = -1
						actorName = actor.text

						actorName = formatActorName(actorName)
						# print("Looking at ", actorName, " in ", node.name, actorNamesAdded)
						# print(actorName, node.name, node.cast)
						if (actorName not in node.cast):
							age = -1
							actorToAddHREF = actor.find_next('a')["href"]
							# actorToAddHREF = formatHREF(actorToAddHREF)

							nameFromHREF = actorToAddHREF[6:].replace("_", " ")

							# print(actorName, actorToAddHREF[:6], nameFromHREF, nameFromHREF in actorNamesAdded)
							# print()
							if ((actorToAddHREF[:6] != "/wiki/") | (nameFromHREF in actorNamesAdded)):
								# print(actorName, " has no wiki page or has href to previous actor")
								actorToAddHREF = "None"

							# print(actorName, age, actorToAddHREF)
							actorToAdd = Actor(actorName, age, actorToAddHREF)
							actorToAdd.addFilm(node.name)
							node.addActor(actorToAdd.name)
							prototype = [actorToAdd] + prototype
							actorNamesAdded.append(actorName)
							foundEnoughActors = numberOfActors >= actorsNeeded

							# for poop in prototype:
							# 	print(poop.name)
						else:
							repeatZ.append(actorName)
							# print(actorName, " not added to ", node.name)
						# print("done this guy")
					# printGraph()
					# break #HALP REMOVE TO GO PAST FIRST ADDED ACTOR
					# print("end of ", node.name)

	elif (theType == "Actors"):
		for node in prototype:
			if (node.__class__.__name__ == "Film"): #actors in beginning of list
				break
			elif (node.__class__.__name__ == "Actor"):
				if (node.href == "None"):
					print(node.name, " has no wiki page")
					continue
				# if (node.name == "Cathy Murphy"):
				if (node.age == -1):
					print(node.name)
					actorHREF = node.href
					actorPage =  urllib2.urlopen(baseURL + actorHREF)
					actorSoup = BeautifulSoup(actorPage, 'html.parser')
				
					age = formatAge(actorSoup)
					node.age = age

					# print(node.name, age)
					try: #fix this
						currentActor = Actor(actorName, age, actorHREF)

						prototype.append(currentActor) #check before or after adding movies
						actorNamesAdded.append(actorName)
					
						actorFilmsUL = actorSoup.find('span', id = 'Filmography').parent #check table vs list
						actorFilmsLI = actorFilmsUL.find_next('ul').find_all('li') #this part too

						for movie in actorFilmsLI:
							if (foundEnoughFilms):
								return
							title = movie.text
							if (title not in filmNamesAdded):
								gross = -1
								flick = Film(title, gross, movie.find('a')["href"])
								# flickToGraph = Film(title, gross, movie.find('a')["href"])
								flick.addActor(currentActor.name)
								# flickToGraph.addActor(currentActor)
								currentActor.addFilm(flick.name) #need to check if film already exists
								prototype.append(flick)
								filmNamesAdded.append(title)
								foundEnoughFilms = numberOfFilms >= filmsNeeded
					except:
						print("Fatal can't parse page.")
					# currentActor = Actor(actorName, age, actorHREF)
			else:
				print("Reached a node that isn't type Film or Actor")
	else:
		print("Fatal should not be here")

def formatAge(actorSoup): #clean up

	bioTable = actorSoup.find('table', {"class": "infobox biography vcard"})
	if (bioTable == None):
		return "Unknown"
	try:
		age = actorSoup.find('span', {"class": "noprint ForceAgeToShow"}).text
		age = ''.join(character for character in age if character.isdigit())

		return age
	except Exception as e:
		try:
			age = actorSoup.find('span', {"class": "dday deathdate"}).parent.parent.text
		except Exception as e: #check Cathy Murphy
			return "-999"
		age = unicodedata.normalize('NFKD', age).encode('ascii','ignore').rstrip()
		if ("\n" in age):
			newlineIndex = age.index("\n")
			age = age[:newlineIndex]
		age = age[-3:]
		age = ''.join(character for character in age if character.isdigit())

		return age
	else:
		pass
	finally:
		pass
	
	return (-10000)

def formatActorName(actorName): #take care of lean on me case
	actorName = re.sub(u"\u2013", "as", actorName)
	if (actorName.count("-") > 1): #allow one dash in name
		actorName = re.sub(u"-", " ", actorName, 1)
	actorName = re.sub(u"-", "as", actorName, 1)

	if (" as " in actorName):
		endOfName = actorName.index(" as ")
		actorName = actorName[:endOfName]

	return unicodedata.normalize('NFKD', actorName).encode('ascii','ignore').rstrip()

def formatGross(gross): #HALP EDIT THIS
	return gross

# def formatHREF(hrefToEdit):
# 	print(hrefToEdit)
# 	return unicodedata.normalize('NFKD', hrefToEdit).encode('ascii','ignore')

def createJSON(): #format prototype here
	print(json.dumps(prototype))

class Film:
	def __init__(self, name, gross, href):
		global numberOfFilms
		global filmNamesAdded

		self.name = name.encode("utf-8")#unaccented_string = unidecode.unidecode(name)
		self.gross = gross#unidecode.unidecode(gross)
		self.href = href#unidecode.unidecode(href)
		self.cast = []
		if (name not in filmNamesAdded):
			numberOfFilms = numberOfFilms+1

	def addActor(self, actor):
		if (actor not in self.cast):
			self.cast.append(actor)#unidecode.unidecode(actor))

class Actor:
	def __init__(self, name, age, href):
		global numberOfActors
		global actorNamesAdded
		
		# try:
		# 	self.name = unidecode.unidecode(name.decode("utf-8"))#unidecode.unidecode(name)
		# except Exception as e:
		# 	print("PROBLEM WITH ", name)
		self.name = name.encode("utf-8")
		# else:
		# 	pass
		# finally:
		# 	pass
		
		self.age = age#unidecode.unidecode(age)
		self.href = href#unidecode.unidecode(href)
		self.roles = []
		if (name not in actorNamesAdded):
			numberOfActors = numberOfActors+1

	def addFilm(self, film):
		if (film not in self.roles):
			self.roles.append(film)#unidecode.unidecode(film))

if __name__ == "__main__":
    main()