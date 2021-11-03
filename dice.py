import random

def rollTotal(rolls, dieType, dieBound): # Takes a number of rolls, upper bound of die value and a string naming the die itself (i.e. "d20")
	total = 0
	print(("Rolling {}{}...").format(rolls,dieType))
	for i in range(rolls): # rolls the given number of dice and returns the sum of the total
		newroll = random.randint(1,dieBound)
		print(("Rolled a {}").format(newroll))
		total += newroll
	return total
	
def d20(rolls = 1, boolRollTotal = False): # roll a d20 x number of times
	if boolRollTotal == True and rolls > 1: 
		return rollTotal(rolls, "d20", 20) # pass this off to rollTotal()
	elif rolls > 1: # otherwise put all roll outcomes into an array and return it
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,20))
		return rollOutcomes
	else:
		return random.randint(1,20) # If only one roll, just return number between 1 and 20

def d12(rolls = 1, boolRollTotal = False): # roll d12, same code as d20. Ditto for all other d(number) functions here
	if boolRollTotal == True and rolls > 1:
		return rollTotal(rolls, "d12", 12)
	elif rolls > 1:
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,12))
		return  rollOutcomes
	else:
		return random.randint(1,12)

def d10(rolls = 1, boolRollTotal = False): # roll d10
	if boolRollTotal == True and rolls > 1:
		return rollTotal(rolls, "d10", 10)
	if rolls > 1:
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,10))
		return rollOutcomes
	else:
		return random.randint(1,10)

def d8(rolls = 1, boolRollTotal = False): # roll d8
	if boolRollTotal == True and rolls > 1:
		return rollTotal(rolls, "d8", 8)
	elif rolls > 1:
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,8))
		return rollOutcomes
	else:
		return random.randint(1,8)

def d6(rolls = 1, boolRollTotal = False): # roll d6
	if boolRollTotal == True and rolls > 1:
		return rollTotal(rolls, "d6", 6)
	elif rolls > 1:
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,6))
		return rollOutcomes
	else:
		return random.randint(1,6)

def d4(rolls = 1, boolRollTotal = False): #roll d4
	if boolRollTotal == True and rolls > 1:
		return rollTotal(rolls, "d4", 4)
	elif rolls > 1:
		rollOutcomes = []
		for i in range(rolls):
			rollOutcomes.append(random.randint(1,6))
		return rollOutcomes
	else:
		return random.randint(1,4)

def comparisonRoll(dieBound, rolls = 2): # Make competition check: two or more checks made between two or more people to see who comes out on top.
	compareDiceAry = []
	for i in range(rolls):
		diceOutcome = random.randint(1,dieBound)
		print(("Roll {}: {}").format(i+1,diceOutcome))
		compareDiceAry.append(diceOutcome)
	return compareDiceAry
				
def rollAdv():
	print("Rolling 2d20 with Advantage...") # Advantage: roll 2d20, use highest value. Used in situations like surprise attacks or anywhere where success is more likely.
	diceRolled = comparisonRoll(20)
	if diceRolled[1] > diceRolled[0]:
		return diceRolled[1]
	elif diceRolled[0] > diceRolled[1]:
		return diceRolled[0]
	else:
		raise Exception
	
def rollDisadv():
	print("Rolling 2d20 with Disadvantage...") # Disadvantage: roll 2d20, use lowest value. Used in situations where failure is likely (i.e. slashing blindly at something in the dark.)
	diceRolled = comparisonRoll(20)
	if diceRolled[1] < diceRolled[0]:
		return diceRolled[1]
	elif diceRolled[0] < diceRolled[1]:
		return diceRolled[0]
	else:
		raise Exception