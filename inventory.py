import dice

class currency(object): #Object that represents value of item in gold, silver and copper pieces.
    def __init__(self, gp, sp, cp):
        self.GP = gp
        self.SP = sp
        self.CP = cp
    def __str__(self):
        return(("""
                gp:         {}
                sp:         {}
                cp:         {}
                """).format(self.GP, self.SP, self.CP))
        
class inventoryObj(object): #Object that represents an individual's inventory.

    def __init__(self, *initItems): #Initialise inventory array and add any pre-existing items.
        self.inventoryList = []
        for i in initItems:
            self.addItem(i)

    def addItem(self, *itemsToAdd): #add given item(s) to inventory array.
        for i in itemsToAdd:
            self.inventoryList.append(i)

    def removeItem(self, *itemsToRemove): #remove given item(s) from inventory array.
        for i in itemsToRemove:
            self.inventoryList.remove(i)

class equippedItems(object): #Object that represents list of items an individual has equipped (weapons, armor, shield)
    
    def __init__(self, weapons, initEquipArmor = None, initEquipShield = None): # Add initial weapons, armor and shield to equipment inventory, checking for types and if something can be equipped.
            if type(weapons) != tuple:
                raise TypeError
            else:
                self.equipmentList = []
                for i in weapons:
                        if (len(weapons) > 2) or (len(weapons) > 1 and shield != None):
                            raise Exception # Can't equip this item (not enough hands left, i.e. two handed weapon with shield or sword + existing sword & shield.)
                        else:
                            self.addEquipment(i)
                if initEquipArmor != None and isinstance(initEquipArmor, armor) == True: # Adding armor and shields separately since they are treated differently to weapons.
                    self.addEquipment(initEquipArmor)
                if initEquipShield != None and isinstance(initEquipShield, shield) == True:
                    self.addEquipment(initEquipShield)

    def addEquipment(self, *itemsToEquip): # Add given item(s) to equipment array.
            for i in itemsToEquip:
                    self.equipmentList.append(i)

    def removeEquipment(self, *itemsToUnequip): # Remove given item(s) from equipment array.
            for i in itemsToUnequip:
                    self.equipmentList.remove(i)

    def __str__(self): 
            equipListStr = ""
            for item in self.equipmentList:
                    equipListStr += str(item)
            return equipListStr


class item(object): #Object that represents basic features that make up an item in 5e: Name, Weight and Value.
    def __init__(self, Name, Weight, currency):
        self.itemName = Name
        self.Weight = Weight
        self.Cost = currency

class equippableItem(item): #Object that represents common features amongst all equippable items. Their enchantment level, and whether they're equipped (in inclusion to above).
	def __init__(self, Name, Weight, currency, enchantLevel = 0, Equipped = False):
		if type(Equipped) != bool:
			raise TypeError
		else:
			super(equippableItem, self).__init__(Name, Weight, currency)
			self.isItemEquipped = Equipped
			self.enchantLevel = enchantLevel
			
class weapon(equippableItem): #Weapon class for their specific properties - damage and weapon properties such as 'two-handed'.
    def __init__(self, Name, Weight, currency, dmgDice, *Properties, enchantLevel = 0, Equipped = False):
        super(weapon, self).__init__(Name, Weight, currency, enchantLevel, Equipped)
        self.dmgDice = dmgDice
        self.wepDmg = (eval("dice." + dmgDice + "()") + self.enchantLevel)
        self.weaponProperties = []
        for i in Properties:
            self.weaponProperties.append(i)
            if "two-handed" in self.weaponProperties:
                self.handsRequired = 2
            else:
                self.handsRequired = 1
    
    def __str__(self):
        return str(("""
                    Name:       {}
                    Weight: 	{}
                    Value:		{}
                    Damage:	    {}
                    Properties: {}
                    Equipped:	{}
                    """).format((self.itemName + " +" + str(self.enchantLevel)), self.Weight, self.Cost, (self.dmgDice + " +" + str(self.enchantLevel)), self.weaponProperties, self.isItemEquipped))

class armor(equippableItem): #Armor class. Includes properties like AC, strength requirement, type of armor (light/medium/heavy).
    def __init__(self, Name, Weight, currency, baseAC, strReq, armorType, enchantLevel = 0, Equipped = False):
        super(armor, self).__init__(Name, Weight, currency, enchantLevel, Equipped)
        self.baseAC = baseAC + self.enchantLevel
        self.strReq = strReq
        self.armorType = armorType
	
    def __str__(self):
        if self.armorType == "light":
                ACDexMod = " + Dex modifier"
        elif self.armorType == "medium":
                ACDexMod = " + Dex modifier (max 2)"
        elif self.armorType == "heavy":
                ACDexMod = ""
        else:
                raise Exception

        return(("""
                Name:		                {}
                Weight:		                {}
                Value:			            {}
                Type:			            {}
                Armor Class: 		        {}
                Strength Requirement:	    {}
                Equipped:		            {}
                """).format((self.itemName + " +" + str(self.enchantLevel)), self.Weight, self.Cost, self.armorType, (str(self.baseAC) + ACDexMod), self.strReq, self.isItemEquipped))

class shield(equippableItem): #Shield class, contains AC and free hands required to equip the item.
	def __init__(self, Name, Weight, currency, baseAC, enchantLevel = 0, Equipped = False):
		super(shield, self).__init__(Name, Weight, currency, enchantLevel, Equipped)
		self.baseAC = baseAC + self.enchantLevel
		self.handsRequired = 1
	
	def __str__(self):
		return(("""
			    Name:           {}
			    Weight:			{}
			    Value:			{}
			    Armor Class:	{}
			    Equipped:		{}
			    """).format((self.itemName + " +" + str(self.enchantLevel)), self.Weight, self.Cost, (str(self.baseAC) + " + " + str(self.enchantLevel)), self.isItemEquipped))