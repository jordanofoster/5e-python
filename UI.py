import stats, dice, inventory, UI, classes, pickle, shelve

class combat(object): #Object that represents entering combat.

    def __init__(self, *combatants): #Recieve all enemy/player objects that will be in the fight.
        self.initiatives = []
        self.turnOrder = []

        print("\nRoll for initiative!\n") #Each fighter rolls 1d20 + dexterity modifier to determine initiative, or turn order. Highest value goes first.
        for fighter in combatants:
            self.initiatives.append(fighter.rollStat(fighter.Dexterity))
            print(("{} rolls a {}").format(fighter.Name, self.initiatives[combatants.index(fighter)])) # these print statements just announce results to the player so they know what to expect.
        for i in self.initiatives:
            self.turnOrder.append(combatants[(sorted(self.initiatives, reverse=True)).index(i)]) # Take each combatant's initiative roll and sort it in descending order, representing turn order.
        print(("{} goes first!").format(self.turnOrder[0].Name))
        del self.initiatives # Delete this variable as it simply acted as a placeholder to store initial rolls.

    def begin(self): # Begins combat loop.
        enemiesLeft = True
        while enemiesLeft == True:
            enemiesLeft = False # Just presumptively assuming all enemies are dead unless shown otherwise (i.e. it's an enemy's turn.)
            for fighter in self.turnOrder:
                if fighter.isDead == False: # Skip someone's turn if they're dead.
                    if isinstance(fighter, stats.player) == True: # If they're a player, bring up the turn menu.
                        successfulChoice = False
                        while successfulChoice == False: # While an action has not been decided on:
                            try: # Catch any inputs that aren't listed as an option.
                                successfulChoice = True
                                mainMenuChoice = int(input(self.turnMainMenu(fighter))) # Pull up the main menu where player decides to attack, cast a spell, use an item or run away.
                                if mainMenuChoice == 1:
                                    fightMenuChoice = self.fightMenu(fighter) # If player chooses option 1, pull up list of weapons to choose from.
                                    if fightMenuChoice == False:
                                        successfulChoice = False # Player has cancelled their choice.
                                    elif fightMenuChoice == None: 
                                        raise Exception("No Weapons!") # player should never have no weapons - even spellcaster classes like Wizards have daggers if nothing else.
                                elif mainMenuChoice == 2:
                                    spellMenuChoice = self.spellMenu(fighter) # If player chooses option 2, pull up list of spells to choose from.
                                    if spellMenuChoice == False:
                                        successfulChoice = False
                                    elif spellMenuChoice == None: 
                                        print("No Spells!") #Currently this will always show up as the only functional class (fighter) has no spellcasting ability.
                                        if type(fighter.Class) == classes.wizard or type(fighter.Class) == classes.ranger:
                                            raise Exception("No spells on spellcasting class!") # If you're a spellcasting class and you have no spells, something's gone wrong. Time to panic.
                                        else:
                                            successfulChoice = False # Otherwise that's simply not an option for you, so just repeat the main menu choice.
                                elif mainMenuChoice == 3:
                                    itemMenuChoice = self.itemMenu(fighter) # If player chooses option 3, pull up list of items to use.
                                    if itemMenuChoice == False:
                                        successfulChoice = False
                                    elif itemMenuChoice == None:
                                        print("No items!") # This will always happen as non-equipment class items have not been implemented yet.
                                        successfulChoice = False
                                elif mainMenuChoice == 4: # Attempt to escape the battle.
                                    enemyPassivePerceptions = [] 
                                    for fighter in self.turnOrder:
                                        if isinstance(fighter, stats.enemy) and fighter.isDead == False:
                                            enemyPassivePerceptions.append(fighter.PassivePerception)
                                    fleeOutcome = self.Flee(fighter, enemyPassivePerceptions)
                                    if fleeOutcome == True:
                                        print("Successfully fleeing!") # If you succeed, the fight ends instantly.
                                        successfulChoice = True
                                        enemiesLeft = False
                                    else:
                                        print("Attempt to flee failed!") # Otherwise, enemies get their turn and we skip the player's. This is standard in most RPG videogames with this mechanic.

                                if successfulChoice == True and mainMenuChoice != 4:
                                    selectTargetChoice = self.selectTarget(self.turnOrder, fighter) # If you successfully choose a weapon/spell/item from 1/2/3, you choose your target here.
                                    if selectTargetChoice == None:
                                        raise Exception("No Targets!") #Combat should end if no targets exist.
                                        # NOTE: Normally in 5e there could be exceptions to this, but it's only at high levels; there's no levelling system implemented (or proposed in the specification).
                                        # furthermore, 5e is balanced around parties of 4 so we only fight the weakest of enemies in the current adventure (challenge rating 1/4, where CR1 = 4 level 1 players).
                                        # in summary, we won't face against anything that can make itself untargetable.
                                        # as such this assumption remains for the scope of this assignment.
                                    elif selectTargetChoice == False:
                                        successfulChoice = False
                                    else:
                                        fighter.attack(fightMenuChoice, selectTargetChoice) # If everything goes well, the player attacks their chosen target.
                            except:
                                print("Choose an option in the list.") # Just informs player they need to make a correct choice and 'resets' their turn.
                                successfulChoice = False
                                pass
                    else: # If it's an enemy's turn:
                        enemiesLeft = True # Go back on base assumption that enemies are dead (so we don't end combat as soon as the player's turn ends) and have them attack the player.
                        fighter.attack(playerCharacter)

    def turnMainMenu(self, playerCharacter): # Simply returns a formatted string.
            return (("""
                        {}'s Turn!

                        HP: {}/{}
                            
                        Fight: 1
                        Cast a Spell: 2
                        Use an Item: 3
                        Flee: 4
            """).format(playerCharacter.Name, playerCharacter.HP, playerCharacter.maxHP))

    def fightMenu(self, playerCharacter): # Construct a weapons list from what weapons the player has on them.
            fightMenuList = ("""
            Weapons:\n""")
            listedWeapons = []
            wepNum = 1
            for i in playerCharacter.playerEquipment.equipmentList:
                    if isinstance(i, inventory.weapon) == True:
                            fightMenuList += ("{}: ").format(wepNum) + str(i.itemName) + (" ({} + {})").format(i.dmgDice, i.enchantLevel)
                            listedWeapons.append(i)
                    if len(listedWeapons) == 0:
                            print("No weapons!")
                            return None #No weapons in list
            fightMenuList += ("\n{}: Go Back").format(len(listedWeapons)+1)
            try: # If an input error is detected, inform the user and continue with the program.
                fightChoice = int(input(fightMenuList + "\nPlease choose an option: "))
            except:
                print("Input error has been detected! the rest of the program might not run correctly!")
                pass # This will likely crash the program somewhere down the line.
            
            if fightChoice == len(listedWeapons)+1:
                    return False # Player chooses to go back
            elif fightChoice in range(1, len(listedWeapons)) or (fightChoice and len(listedWeapons)) == 1:
                    return listedWeapons[fightChoice-1] # Player chooses a valid option
            else:
                raise Exception # If, somehow, invalid option gets through, raise exception

    def selectTarget(self, turnOrder, playerCharacter): # Same as fightMenu, just with targets. Constructed from living enemies.
            targetMenuList = "\nTargets:\n"
            validTargets = []
            for i in turnOrder:
                    if isinstance(i, stats.player) == False and i.isDead == False:
                            validTargets.append(i)
                            targetMenuList += ("\n{}: {}").format((validTargets.index(i)+1), i.Name)
            if len(validTargets) == 0:
                    print("No valid targets!")
                    return None # If no valid targets
            targetMenuList += ("\n{}: Go Back").format(len(validTargets)+1)
            try:
                targetChoice = int(input(targetMenuList + "\nPlease choose an option: "))
            except:
                print("Input error has been detected! the rest of the program might not run correctly!")
                pass
            
            if targetChoice == len(validTargets)+1:
                    return False # If player chooses to go back
            elif targetChoice in range(1, len(validTargets)) or (targetChoice and len(validTargets)) == 1:
                    return validTargets[targetChoice-1]
            else:
                raise Exception

    def spellMenu(self, playerCharacter): # Construct a string of all the available spells the player has available to them and return it.
        SpellMenuStr = """
        Spells:\n"""
        listedSpells = []
        spellNum = 0
        if playerCharacter.spellList == None: # If player isn't playing a spellcasting class, just return None and let rest of the program handle it as shown before.
            return None
        else:
            for i in playerCharacter.spellList:
                    SpellMenuStr += i.Name + " " + i.castTime + " " + i.Duration + (": {}\n").format(spellNum)
                    listedSpells.append(i)
            if spellNum == 0:
                return None
            else:
                SpellMenuStr.append += ("\n{}: Go Back").format(spellNum+1)
                return SpellMenuStr

    def itemMenu(self, playerCharacter): # Same here but for items
            ItemMenuStr = """
            Items:\n"""
            itemNum = 0
            # NOTE: no check for if playerCharacter.playerInventory == None here because everyone has an inventory regardless of class.
            for i in playerCharacter.playerInventory.inventoryList:
                    if isinstance(i, inventory.item):
                            itemNum += 1
                            ItemMenuStr += i.Name + " " + i.Weight + " " + i.Cost + (": {}\n").format(itemNum)
                    if itemNum == 0:
                            return None
            ItemMenuStr += ("\n{}: Go Back").format(itemNum+1)
            return ItemMenuStr

    def Flee(self, playerCharacter, enemyPassivePerceptions): # Makes a check for each enemy to see if you beat their passive perception.
        successfulFlee = True
        for i in range(0, (len(enemyPassivePerceptions)-1)):
            if playerCharacter.makeCheck(playerCharacter.Dexterity, enemyPassivePerceptions[i]) == False:
                successfulFlee = False
        return successfulFlee
        # NOTE: This function is based off 5e's hide mechanic, although in that case you only roll once and compare to each enemy's passive perception instead of rolling for each enemy as I've done here.
        # It seemed to be the easiest fit for fleeing a battle as it's not listed as a mechanic in 5e.
    
def newCharacter(): # Function that goes through the character creation process.
    try:
        Name = str(input("Enter the new character's name: "))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    try:
        methodChosen = int(input("""
        How do you want your stats to be handed?
        1 - Point Buy (27 points to spend across all 6 stats; max 15, lowest 8) 
        Difficulty: Easy

        2 - Standard Array (allocate 15, 14, 13, 12, 10, 8 to one stat each)
        Difficulty: Medium

        3 - Dice Roll (for each stat roll 4d6, drop lowest; total is sum of rest. You then allocate your 'values' accordingly.) 
        Difficulty: Hard
        
        enter your response here: """))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass
    
    if methodChosen == 1: # If you do point buy
            statVals = pointBuy()
            Strength = statVals[0]
            Dexterity = statVals[1]
            Constitution = statVals[2]
            Intelligence = statVals[3]
            Wisdom = statVals[4]
            Charisma = statVals[5]
            
    elif methodChosen == 2: # If you choose standard array
            statVals = stdAry()
            Strength = statVals[0]
            Dexterity = statVals[1]
            Constitution = statVals[2]
            Intelligence = statVals[3]
            Wisdom = statVals[4]
            Charisma = statVals[5]
            
    elif methodChosen == 3: # If you choose to roll
            statRolls = []
            for i in range(6):
                statRolls.append(statRoll())
            statVals = stdAry(statRolls) # We reuse the standard array code for point buy, since in this case we just have an array of randomly rolled values.
            Strength = statVals[0]
            Dexterity = statVals[1]
            Constitution = statVals[2]
            Intelligence = statVals[3]
            Wisdom = statVals[4]
            Charisma = statVals[5]    

    try: 
        raceChoice = int(input("""
        Choose which race you want to be:
        1 - Human
        2 - Dwarf
        3 - Elf

        enter your response here: """))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    if raceChoice == 1:
        raceChoice = "Human"
    elif raceChoice == 2:
        raceChoice = "Dwarf"
    elif raceChoice == 3:
        raceChoice = "Elf"

    try:
        classChoice = int(input("""
        Choose which class you want to be:
        1 - Fighter (Pick this for testing purposes)
        2 - Wizard (Raises TypeError due to no implemented spellList functionality)
        3 - Ranger (Raises TypeError due to no implemented spellList functionality)

        enter your response here: """))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    if classChoice == 1:
        classChoice = classes.fighter("Fighter", 10, inventory.weapon("Flail", 2, inventory.currency(10, 0, 0), "d8", None, Equipped = True), inventory.weapon("lightCrossbow", 5, inventory.currency(25, 0, 0), "d8", None, Equipped = True), baseArmor = inventory.armor("chainMail", 55, inventory.currency(75, 0, 0), 16, 13, "heavy", Equipped = True), baseShield = inventory.shield("Shield", 6, inventory.currency(10, 0, 0), 2, Equipped = True))
    elif classChoice == 2:
        classChoice = classes.wizard("Wizard", 6, inventory.weapon("Quarterstaff", 4, inventory.currency(0, 2, 0), "d6", None, Equipped = True))
    elif classChoice == 3:
        classChoice = classes.ranger("Ranger", 10, inventory.weapon("shortsword", 2, inventory.currency(10, 0, 0), "d6", None, Equipped = False), inventory.weapon("shortsword", 2, inventory.currency(10, 0, 0), "d6", None, Equipped = False), inventory.weapon("Longbow", 2, inventory.currency(50, 0, 0), "d8", "two-handed", Equipped = True)) 
    # NOTE: Classes are only referenced by name in this build due to time constraints (each player has the same starting equipment).
    # Originally each class starts with their own equipment which would then be added to the player's basic equipment.

    playerCharacter = stats.player(Name, 
                                10, 
                                Strength,
                                Dexterity,
                                Constitution,
                                Intelligence,
                                Wisdom,
                                Charisma,
                                inventory.weapon("longsword", 3, inventory.currency(15, 0, 0), "d8", [None], Equipped = True),
                                initArmor = inventory.armor("studdedLeather", 8, inventory.currency(5, 0, 0), 12, None, "light", Equipped = True),
                                initShield = inventory.shield("Shield", 6, inventory.currency(10, 0, 0), 2, Equipped = True), 
                                Race = raceChoice, 
                                Class = classChoice)
    return playerCharacter

def loadCharacter(file):
    fileCharacterList = []
    fileToParse = shelve.open(file, "r")
    for i in fileToParse.keys(): # Find each dictionary definition in fileToParse
        playerCharacterDetails = fileToParse[i] # Dump each definition into this array.
        playerCharacterName = playerCharacterDetails[0] # These are all in the form [name1, name2, name3].
        playerCharacterHP = playerCharacterDetails[1]   # We're separating them into different array variables to make it all easier to manage
        playerCharacterStats = playerCharacterDetails[2] 
        playerBaseWeapons = playerCharacterDetails[3] # Otherwise we'd have to use four(?) dimensions of array when accessing equipment data in the following code
        playerBaseArmor = playerCharacterDetails[4]
        playerBaseShield = playerCharacterDetails[5]
        playerRace = playerCharacterDetails[6]
        playerClass = playerCharacterDetails[7]
        fileCharacterList.append([playerCharacterName, #Then, we just dump it all into one array of arrays (i.e. [[name, stats, [weapons], [armor], [shield], race, class], ...)
                                playerCharacterHP,
                                playerCharacterStats,
                                playerBaseWeapons,
                                playerBaseArmor,
                                playerBaseShield,
                                playerRace,
                                playerClass])
    fileToParse.close()

    characterListNames = []
    characterListHPs = []
    characterListRaces = []
    characterListClasses = []
    characterListStrengths = []
    characterListDexterities = []
    characterListConstitutions = []
    characterListIntelligences = []
    characterListWisdoms = []
    characterListCharismas = []

    characterListWepArys = []
    characterListArmrArys = []
    characterListShldArys = []

    for i in fileCharacterList:
        characterListNames.append(i[0]) #Here we basically take what we've parsed and put them in a set of single-dimension arrays all with the same length
        characterListHPs.append(i[1]) # It would allow us to basically take a character from position [0] by creating one with name characterListNames[0], Strength characterListStrengths[0], and so on.

        characterListStrengths.append(i[2][0])
        characterListDexterities.append(i[2][1])
        characterListConstitutions.append(i[2][2])
        characterListIntelligences.append(i[2][3])
        characterListWisdoms.append(i[2][4])
        characterListCharismas.append(i[2][5])

        characterListWepArys.append(i[3]) # These are an exception. for example, here we get [[<weapon object1>, <weapon object2>], [<weapon object3>]] for example. Not easy to parse.
        characterListArmrArys.append(i[4])
        characterListShldArys.append(i[5])

        characterListRaces.append(i[6])
        characterListClasses.append(i[7])
    
    parsedChrLstWeps = [] # NOTE: Here an attempt was made to split equipment information into something easily placeable into a formatted string, and recreatable into relevant equipment when loading a character.
    for i in characterListWepArys: # pick an element array of weapon objects from the characterListWepArys array.
        for j in i: # go through each element of that array you just chose as part of i:
            chunkedChrLstArgs = [] # Make a temporary array
            chunkedChrLstArgs.append(j.itemName) 
            chunkedChrLstArgs.append(j.Weight)
            chunkedChrLstArgs.append(j.Cost)
            chunkedChrLstArgs.append(j.enchantLevel) # for all these .append statements, dump the element's properties into this temporary array...
            chunkedChrLstArgs.append(j.isItemEquipped)
            chunkedChrLstArgs.append(j.dmgDice)
            chunkedChrLstArgs.append(j.wepDmg),
            chunkedChrLstArgs.append(j.weaponProperties)
            parsedChrLstWeps.append(chunkedChrLstArgs) # and add it to parsedChrLstWeps.
            # NOTE: Eventually, parsedChrLstWeps would end up in a format similar to  [["broadsword", 5, <currency object>, 0, ...], [...]]
            # Something easier for us to parse as we can more easily iterate through things like properties and bring equipment closer to the same format as character Names, HP, Stats, etc.
            # So that adding back equipment when 'recreating' a character would be a far more drag-and-drop affair.

    parsedChrLstArmrs = [] # The same is done with armors...
    for i in characterListArmrArys:
        for j in i:
            chunkedChrLstArgs = []
            chunkedChrLstArgs.append(j.itemName)
            chunkedChrLstArgs.append(j.Weight)
            chunkedChrLstArgs.append(j.Cost)
            chunkedChrLstArgs.append(j.enchantLevel)
            chunkedChrLstArgs.append(j.isItemEquipped)
            chunkedChrLstArgs.append(j.baseAC)
            chunkedChrLstArgs.append(j.strReq)
            chunkedChrLstArgs.append(j.armorType)
            parsedChrLstArmrs.append(chunkedChrLstArgs)
    
    parsedChrLstShlds = [] # and shields.
    for i in characterListShldArys:
        for j in i:
            chunkedChrLstArgs = []
            chunkedChrLstArgs.append(j.itemName)
            chunkedChrLstArgs.append(j.Weight)
            chunkedChrLstArgs.append(j.Cost)
            chunkedChrLstArgs.append(j.enchantLevel)
            chunkedChrLstArgs.append(j.isItemEquipped)
            chunkedChrLstArgs.append(j.baseAC)
            chunkedChrLstArgs.append(j.handsRequired)
            parsedChrLstShlds.append(chunkedChrLstArgs)
    
    del chunkedChrLstArgs # We remove the temporary array afterwards just for housekeeping.

    # NOTE: The above section of code isn't used when recreating a character as time left was extremely short at this point.
    # Adding onto this, since each created character uses the same equipment due to classes (where equipment originally comes from) not being fully implemented,
    # this became a section of code of questionable importance over making a functional character loader
    # since in every instance we can just make an assumption about what equipment that character had, since there's no variation as stated before.

    choiceStr = "" #Take our extracted information and add a formatted string including it for every character 'loaded' in:
    for i in range(0,len(characterListNames)):
        choiceStr += ("""Character {}:
                
                Name:   {}
                HP:     {}

                Race:   {}
                Class:  {}

                Strength:       {}
                Dexterity:      {}
                Constituiton:   {}
                Intelligence:   {}
                Wisdom:         {}
                Charisma:       {}
                 
                """).format((i+1), 
                    characterListNames[i], 
                    characterListHPs[i],
                    characterListRaces[i],
                    characterListClasses[i],
                    characterListStrengths[i],
                    characterListDexterities[i],
                    characterListConstitutions[i],
                    characterListIntelligences[i],
                    characterListWisdoms[i],
                    characterListCharismas[i])
    try:
        characterChoice = int(input(choiceStr + "\nPlease choose a character: ")) # We pick our character
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    loadedCharacter = stats.player(characterListNames[characterChoice-1], #Chosen character is then recreated from the arrays we created.
                                characterListHPs[characterChoice-1],
                                characterListStrengths[characterChoice-1],
                                characterListDexterities[characterChoice-1],
                                characterListConstitutions[characterChoice-1],
                                characterListIntelligences[characterChoice-1],
                                characterListWisdoms[characterChoice-1],
                                characterListCharismas[characterChoice-1],
                                inventory.weapon("longsword", 3, inventory.currency(15, 0, 0), "d8", [None], Equipped = True),
                                initArmor = inventory.armor("studdedLeather", 8, inventory.currency(5, 0, 0), 12, None, "light", Equipped = True),
                                initShield = inventory.shield("Shield", 6, inventory.currency(10, 0, 0), 2, Equipped = True), 
                                Race = characterListRaces[characterChoice-1], 
                                Class = characterListClasses[characterChoice-1])
    
    return loadedCharacter

def statChoice(strVal, dexVal, conVal, intVal, wisVal, chaVal): # Function that returns an integer choice for player stats, used in character creation.
    try:
        statChoice = int(input(("""
                            1 - Strength 		    ({})
                            2 - Dexterity		    ({})
                            3 - Constitution	    ({})
                            4 - Intelligence	    ({})
                            5 - Wisdom		        ({})
                            6 - Charisma		    ({})

                            Choose a stat: """).format(strVal, dexVal, conVal, intVal, wisVal, chaVal)))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    return statChoice
	
def subVal(pointsLeft, statVal): # Function that removes points from value during point-buy process, ensuring that valid changes are being made.
        while True:
            try:
                valToSub = int((input(("State the amount of points to remove (currently have {} left): ").format(pointsLeft))))
            except:
                print("Input error has been detected! the rest of the program might not run correctly!")
                pass

            if (valToSub < 0) or ((statVal - valToSub) < 8):
                print("Invalid input entered (point value below 0 or new stat value below 8)")
            else:
                newStatVal = statVal - valToSub
                newPointsLeft = pointsLeft + valToSub
                return newStatVal, newPointsLeft

def addVal(pointsLeft, statVal): # Same as above, but with adding points instead.
    while True:
        try:
            valToAdd = int((input(("State the amount of points to add (currently have {} left): ").format(pointsLeft))))
        except:
            print("Input error has been detected! the rest of the program might not run correctly!")
            pass

        if (valToAdd > pointsLeft) or ((valToAdd + statVal) > 15):
            print("Invalid input entered (not enough points or new stat value above 15)")
        else:
            newStatVal = statVal + valToAdd
            newPointsLeft = pointsLeft - valToAdd
            return newStatVal, newPointsLeft
			
def pointBuy(): # Initialising point-buy process.
    statVals = [8] * 6
    pointsLeft = 27
    choice = 0
    confirm = "0"
    
    while confirm != "Y":
        try:
            choice = int(input(("""
                                    Strength        {}
                                    Dexterity       {}
                                    Constitution    {}
                                    Intelligence    {}
                                    Wisdom          {}
                                    Charisma        {}
                                    
                                    Points left:    {}
                                    
                                    Options:
                                    1 - Invest points
                                    2 - Remove points
                                    3 - Finish
                                    
                                    Choose an option: """).format(statVals[0], statVals[1], statVals[2], statVals[3], statVals[4], statVals[5], pointsLeft)))
        except:
            print("Input error has been detected! the rest of the program might not run correctly!")
            pass

        if choice == 1:
            if pointsLeft == 0:
                print("No points left!")
                break
            else:
                chosenStat = statChoice(statVals[0], statVals[1], statVals[2], statVals[3], statVals[4], statVals[5])

                if chosenStat == 1: #Strength
                    statVals[0], pointsLeft = addVal(pointsLeft, statVals[0])

                elif chosenStat == 2: #Dexterity
                    statVals[1], pointsLeft = addVal(pointsLeft, statVals[1])

                elif chosenStat == 3: #Constitution
                    statVals[2], pointsLeft = addVal(pointsLeft, statVals[2])

                elif chosenStat == 4: #Intelligence
                    statVals[3], pointsLeft = addVal(pointsLeft, statVals[3])

                elif chosenStat == 5: #Wisdom
                    statVals[4], pointsLeft = addVal(pointsLeft, statVals[4])

                elif chosenStat == 6: #Charisma
                    statVals[5], pointsLeft = addVal(pointsLeft, statVals[5])

        elif choice == 2:
            if pointsLeft == 27:
                print("No points spent!")
                break
            else:
                chosenStat = statChoice(statVals[0], statVals[1], statVals[2], statVals[3], statVals[4], statVals[5])
            
                if chosenStat == 1:
                    statVals[0], pointsLeft = subVal(pointsLeft, statVals[0])
                    
                elif chosenStat == 2:
                    statVals[1], pointsLeft = subVal(pointsLeft, statVals[1])
                    
                elif chosenStat == 3:
                    statVals[2], pointsLeft = subVal(pointsLeft, statVals[2])
                    
                elif chosenStat == 4:
                    statVals[3], pointsLeft = subVal(pointsLeft, statVals[3])
                    
                elif chosenStat == 5:
                    statVals[4], pointsLeft = subVal(pointsLeft, statVals[4])
                    
                elif chosenStat == 6:
                    statVals[5], pointsLeft = subVal(pointsLeft, statVals[5])
        
        elif choice == 3:
            pointsUsed = 0
            for i in range(len(statVals)): # Calculating whether player has spent all their points before allowing them to confirm exit.
                pointsUsed += statVals[i] - 8

            if pointsUsed < 27:
                print("Not all points used!")
            elif pointsUsed == 27:
                while (confirm != "Y") and (confirm != "N"):
                    confirm = input("Confirm exit (Y/N): "); confirm = confirm.upper().strip()
                if confirm == "N":
                    confirm = "0"

    return statVals

def addStdAryVal(stdAryVals, statVals, statChosenVal): # Adds a value from an array to a stat.
    availableStdAryVals = stdAryVals
    valChoice = None
    stdAryStr = "Available Standard Array Values:\n"
    for i in availableStdAryVals: #Checking to see which haven't already been assigned
        stdAryStr += (str(i) + "\n")
    while (valChoice not in availableStdAryVals) == True:
        if (len(availableStdAryVals)) == 0:
            print("No values left to assign!") # Goes back to stdAry main menu if no values available based on stat method chosen
            return statChosenVal, availableStdAryVals
        else:
            try:
                valChoice = int(input(stdAryStr + "Choose a value: "))
            except:
                print("Input error has been detected! the rest of the program might not run correctly!")
                pass

            if valChoice not in availableStdAryVals:
                print("choice not in available options.")
            else:
                if statChosenVal != None: # If stat already allocated we let user know and just return the value that stat already had, and don't remove any array values.
                    print("Stat already allocated!")
                    valChoice = statChosenVal
                    return valChoice, availableStdAryVals
                else: # Otherwise we overwrite 'None' with the new value, and replace the former array values with those left.
                    availableStdAryVals.remove(valChoice)
                    return valChoice, availableStdAryVals   

def rmvStdAryVal(stdAryVals, statVals, statChosenVal): # Removes a value from a stat, adding it back to the array.
    usedStdAryVals = []
    for i in range(len(statVals)):
        if statVals[i] != None: # if a stat doesn't have 'none' as a value, we add its value to a list of 'used' values:
            usedStdAryVals.append(statVals[i])
        for i in range(len(statVals)):
            if statChosenVal == statVals[i]: # If our chosen value is the same as the value of the stat we chose, we replace the stat value with 'None' and add the value chosen to our list of array values.
                statVals[i] = None
                stdAryVals.append(statChosenVal)
                return statVals[i], stdAryVals
				    
def stdAry(stdAryValsInput = [15,14,13,12,10,8]): # Initialises standard array/dice roll menu.
    stdAryVals = stdAryValsInput
    statVals = [None] * 6
    confirm = "0"
    while confirm != "Y":
        inputStr = (""" 
            Strength        {}
            Dexterity       {}
            Constitution    {}
            Intelligence    {}
            Wisdom          {}
            Charisma        {}
            
            Values left:\n""").format(*statVals)
        for i in range(len(stdAryVals)):
            inputStr += ("{}\n").format(stdAryVals[i])
        try: #Recieve main menu choice from user
            choice = int(input(inputStr + """
                Options:
                1 - Use value
                2 - Remove value
                3 - Finish
                
                Choose an option: """))
        except:
            print("Input error has been detected! the rest of the program might not run correctly!")
            pass
        
        if choice == 1: # If we use a value, we choose a stat and go through the motions described prior
            chosenStat = statChoice(statVals[0], statVals[1], statVals[2], statVals[3], statVals[4], statVals[5])
            if chosenStat == 1:
                statVals[0], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[0])
            elif chosenStat == 2:
                statVals[1], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[1])
            elif chosenStat == 3:
                statVals[2], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[2])
            elif chosenStat == 4:
                statVals[3], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[3])
            elif chosenStat == 5:
                statVals[4], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[4])
            elif chosenStat == 6:
                statVals[5], stdAryVals = addStdAryVal(stdAryVals, statVals, statVals[5])
                                
        elif choice == 2: # Same here when removing a value.
            chosenStat = statChoice(statVals[0], statVals[1], statVals[2], statVals[3], statVals[4], statVals[5])
            if chosenStat == 1:
                statVals[0], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[0])
            elif chosenStat == 2:
                statVals[1], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[1])
            elif chosenStat == 3:
                statVals[2], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[2])
            elif chosenStat == 4:
                statVals[3], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[3])
            elif chosenStat == 5:
                statVals[4], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[4])
            elif chosenStat == 6:
                statVals[5], stdAryVals = rmvStdAryVal(stdAryVals, statVals, statVals[5])
            
        elif choice == 3: # We check to see if all values have been used before we allow user to confirm exiting character creation.
            allValuesUsed = True
            for i in range(len(statVals)):
                if statVals[i] == None:
                    allValuesUsed = False
            if allValuesUsed == True:
                while (confirm != "Y") and (confirm != "N"):
                    confirm = input("Confirm exit (Y/N): "); confirm = confirm.upper().strip()
                if confirm == "N":
                    confirm = "0"
    return statVals

def statRoll(): # Simple function that just rolls 4d6, discards the lowest and returns the sum of the rest.
    rolls = []
    lowestRoll = 7
    for i in range(4):
        rolls.append(dice.d6())
        if rolls[i] < lowestRoll:
            lowestRoll = rolls[i]
    rolls.pop(rolls.index(lowestRoll))
    return sum(rolls)
    
def StartGame():
    global playerCharacter
    try: #Main menu
        choice = int(input("""
        Welcome to a text-based rendition of Dungeons and Dragons 5th Edition!

        This game plays a bit like a choose-your-own-adventure story with some
        RPG combat sequences. The system reference document for 5th edition has
        been used as reference for various mechanics here.

        Do you want to create a new character or load a previously made one?
        1 - New character
        2 - Use previously made character
        3 - Exit game

        enter your response here: """))
    except:
        print("Input error has been detected! the rest of the program might not run correctly!")
        pass

    if choice == 1: # Make new character
        playerCharacter = newCharacter()
        characterList = shelve.open("characters.dat", "c")
        playerCharacterName = playerCharacter.Name
        playerCharacterHP = playerCharacter.HP
        playerCharacterStats = [playerCharacter.Strength,
                                playerCharacter.Dexterity,
                                playerCharacter.Constitution,
                                playerCharacter.Intelligence,
                                playerCharacter.Wisdom,
                                playerCharacter.Charisma]

        playerBaseWeapons = []
        playerBaseArmor = []
        playerBaseShield = []
        for i in playerCharacter.playerEquipment.equipmentList:
            if type(i) == inventory.weapon:
                    playerBaseWeapons.append(i)
            elif type(i) == inventory.armor:
                    playerBaseArmor.append(i)
            elif type(i) == inventory.shield:
                    playerBaseShield.append(i)
            else:
                raise TypeError
        
        playerCharacterRace = playerCharacter.Race
        playerCharacterClass = playerCharacter.Class.className

        characterList[str(len(list(characterList.keys()))+1)] = [playerCharacterName, playerCharacterHP, playerCharacterStats, playerBaseWeapons, playerBaseArmor, playerBaseShield, playerCharacterRace, playerCharacterClass]
        characterList.sync()
        characterList.close()
        del characterList, playerCharacterName, playerCharacterHP, playerCharacterStats, playerBaseWeapons, playerBaseArmor, playerBaseShield, playerCharacterRace, playerCharacterClass

    elif choice == 2: # Load old character
        playerCharacter = loadCharacter("characters.dat")

    if choice == 3: # Exit program
        print("Exiting now...")
    else:
        # This part is the adventure
        try:
            forestChoice = int(input("""
            You wake up in the middle of a forest, unsure of how you got there. A sign points to a town called Hemsberg in the distance; your head hurts a ton though, and you're not sure whether you want to make the journey yet.

            What do you do?
            1 - Stay where you are and recuperate 
            2 - Decide to travel immediately

            Type your answer here: """)) # First option available to player
        except:
            print("Input error has been detected! the rest of the program might not run correctly!")
            pass

        if forestChoice == 1: # Fight occurs
                print("""You decide to stay where you are for a bit, but just as you decide to lay your head down, a duo of Jackals decide to attack! You ready yourself for a fight.""")
                fight = combat(playerCharacter, (stats.enemy("Jackal 1", 
                                                            3, 
                                                            8, 
                                                            15, 
                                                            11, 
                                                            3, 
                                                            12, 
                                                            6, 
                                                            inventory.weapon("Bite", None, None, "d4", [None], Equipped = True),
                                                            armorClass = 12)),
                                                (stats.enemy("Jackal 2", 
                                                            3, 
                                                            8, 
                                                            15, 
                                                            11, 
                                                            3, 
                                                            12, 
                                                            6,
                                                            inventory.weapon("Bite", None, None, "d4", [None], Equipped = True), 
                                                            armorClass = 12,
                                                            )))
                fight.begin()
                print("\nFollowing the fight with the jackals, you think it a better idea to just go to Hemsberg after all. Hopefully you can get some rest as soon as possible.\n")
        elif forestChoice == 2: # Player skips fight with jackals
            print("""
            Since you're in uncharted territory (at least for you), you think it best to get to civilization as soon as possible and find an inn to rest at.""")
            
        commonersConvinced = False
        try:
            shakedownChoice = int(input("""When you get to Hemsberg, a pair of commoners appear to try and shake you down for money.

            You can:
            1 - Attempt to reason with them (Charisma check)
            2 - Get this over with (Fight)
    
            What will you do?: """))
        except:
            print("Input error has been detected! the rest of the program might not run correctly!")
            pass

        if shakedownChoice == 1: # Attempt to avoid confrontation
            commonersConvinced = playerCharacter.makeCheck(playerCharacter.Charisma, 10)
            if commonersConvinced == True: # check passed
                print("""
                Somehow you manage to convince them to bother someone else and that you're not worth it - they look you up and down then skulk off into an alleyway.
                Whether they were sizing you up or figured you weren't worth the hassle, you have no idea, but they're no longer a problem.""")

                print("""
                    You find yourself the nearest inn, hoping to get off the streets. 
                    It's a small tavern and the owner cheerfully offers you a comfortable room for an appreciable sum.""")
            else: # check failed, fight happens.
                print("""
                They're having none of it, and draw their weapons. Looks like you'll have to do this the hard way - you prepare yourself and get into a fighting stance.""")
        elif shakedownChoice == 2: # Go straight into fight
                print("""Looking to end this quickly, you draw your weapon, ready for a scuffle!""")
        
        if commonersConvinced == False: 
            fight = combat(playerCharacter, 
                            stats.enemy("Commoner 1", 
                                        4, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        inventory.weapon("Club", None, None, "d4", [None], Equipped = True), 
                                        armorClass = 10), 
                            stats.enemy("Commoner 2", 
                                        4, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        10, 
                                        inventory.weapon("Club", None, None, "d4", [None], Equipped = True), 
                                        armorClass = 10))
            fight.begin()
            print("""After your fight, a few members of the town guard show up. you open your mouth to explain yourself, but one of the group - a tall man with an unkempt mustache - holds his hand up and speaks before you get the chance.
                    
                    \"No need to explain. Those two have been terrorizing passersby for a while now, yet always escaped our grasp. In fact...\" 
                    His words begin to trail off.""")
            if playerCharacter.makeCheck(playerCharacter.Wisdom, 12) == True: #Perception check.
                    print("""With your keen sense of hearing, you discern that the man says something to the effect of \'done us all a favor\'.
                            
                            Evidently, those two you took down were a pain in this guy's side - and the town as a whole.""")
            
            print("""
                    He starts talking again.
                    
                    \"Nevermind all that, anyway. you look exhausted. I can't give you a spot at an inn or anything, but our barracks are comfortable and warm.\"""")
            if forestChoice == 1: # You fought the jackals
                print("""
                    \"Honestly, I'm surprised you're still standing,\" another guardsman of significantly smaller stature says.
                    \"Not to be rude or anything, but I think I saw you come in earlier, and you looked like you'd been fighting rabid jackals or something.\"
                    
                    The tall guardsman coughs and clears his throat, glancing sideways with not-so-subtle expectation.
                    The smaller fellow blinks. \"Ah, sorry. T'was a bit out of line.\"
                    You shake your head, easing his concerns.""")
                
            print("""
                Taking up the offer of who you can only presume to be the captain of these guards, you follow them up to the barracks,
                getting your wounds treated and a decent night's sleep for your troubles.""")