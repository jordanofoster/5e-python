class playerClass(object): #Object that makes up the common attributed of classes in 5e: that is, name, given HP and equipment.
	def __init__(self, className, baseHP, *baseWeapons, baseArmor = None, baseShield = None):
		self.className = className
		self.baseHP = baseHP
		self.baseWeapons = baseWeapons
		self.baseArmor = baseArmor
		self.baseShield = baseShield

#All three of these specific class instances have been left unfinished due to time constraints.
#The 'fighter' class doesn't cause any issues when chosen during character creation.
#The other two classes cause an exception to be raised since spells have not been implemented.
#They have been left here to show evidence of having started on these specification points.

class fighter(playerClass): #Unfinished. Should include class features such as 'fighting style' (which provides bonuses such as increased AC based on which is chosen).
    def __init__(self, className, baseHP, *baseWeapons, baseArmor = None, baseShield = None):
        super(fighter, self).__init__(className, baseHP, baseWeapons, baseArmor, baseShield)

class wizard(playerClass):
    def __init__(self, className, baseHP, *baseWeapons, baseArmor = None, baseShield = None, spellList = None):
        super(wizard, self).__init__(className, baseHP, baseWeapons, baseArmor, baseShield)
        if type(spellList) == list:
                self.spellList = spellList
        else:
            raise TypeError("SpellList not of Type List!")

class ranger(playerClass):
    def __init__(self, className, baseHP, *baseWeapons, baseArmor = None, baseShield = None, spellList = None):
        super(ranger, self).__init__(className, baseHP, *baseWeapons, baseArmor = None, baseShield = None)
        if type(spellList) == list:
            self.spellList = spellList
        else:
            raise TypeError("SpellList not of Type List!")