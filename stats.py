import inventory, dice, random

class statblock(object): # Object that defines ability scores and functions relating to them
    def __init__(self, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma):
        self.Strength = Strength
        self.Dexterity = Dexterity
        self.Constitution = Constitution
        self.Intelligence = Intelligence
        self.Wisdom = Wisdom
        self.Charisma = Charisma

    def __str__(self):
        return (("""
        Strength:      {}
        Dexterity:     {}
        Constitution:  {}
        Intelligence:  {}
        Wisdom:        {}
        Charisma:      {}
        """).format(self.Strength, self.Dexterity, self.Constitution, 
		self.Intelligence, self.Wisdom, self.Charisma))

    def returnMod(self, stat): # Modifier is +1 for each 2 points you have over 10 (i.e., 12[+1], 14[+2]...), -1 for each 2 point range under 10 (i.e. 9-8[-1], 7-6[-2], 5-4[-3]...)
        return int((stat // 2) - 5)

    def makeCheck(self, stat, DC): # makes a d20 + stat modifier roll against a given difficultly level; pass if greater than or equal to DC, else fail.
        score = (dice.d20() + self.returnMod(stat))
        if score >= DC:
            return True
        elif score < DC:
            return False
    
    def rollStat(self, stat): #Returns a simple d20 + stat modifier without hard DC requirement
        return dice.d20() + self.returnMod(stat)
		
class being(statblock): # Object defines living being with statblock
    def __init__(self, Name, HP, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma):
        super(being, self).__init__(Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma)
        self.Name = Name
        self.HP = HP + self.returnMod(self.Constitution)
        self.maxHP = self.HP
        self.PassivePerception = 10 + self.returnMod(self.Wisdom) # Used to see if being passively notices something without watching for it
        self.armorClass = 10 + self.returnMod(self.Dexterity) # Value to beat to hit/deal damage when attacking this being
        self.isDead = False
            
    def __str__(self):
        return((("""
        Name:          {}
        HP:            {}/{}
        """).format(self.Name, self.HP, self.maxHP,) + super(being, self).__str__()))
    
    def attack(self, weapon, target): # Makes check against another being's DC to attack them
        print(("{} attacks {} using {}!").format(self.Name, target.Name, weapon.itemName))
        if "finesse" in weapon.weaponProperties: # finesse allows user of weapon to choose to use either their strength or dexterity mod on their attack and damage roll.
            if self.returnMod(self.Dexterity) >= self.returnMod(self.Strength): #Picks highest of the two (assume most optimal choice would always be chosen.)
                attackhits = self.makeCheck(self.Dexterity, target.armorClass)
        else: # Otherwise just use strength as it's the default
            attackhits = self.makeCheck(self.Strength, target.armorClass)
                    
        if attackhits == True: # If we hit do damage
            dmgDone = weapon.wepDmg
            target.takeDmg(self.Name, weapon.itemName, dmgDone)
            
        elif attackhits == False:
            print("The attack misses!")
        
    def takeDmg(self, attackerName, weaponName, dmgDone): # Take damage from a successful attack from another being
        print(("{}'s {} hits for {} damage!").format(attackerName, weaponName, dmgDone))
        self.HP -= dmgDone
        if self.HP <= 0:
            self.dead(attackerName)

    def dead(self, killer): # Called when being dies, be it in battle or otherwise
        print(("{}'s attack kills {}!").format(killer, self.Name))
        self.isDead = True
            
class enemy(being): # Object that defines enemy monster without inventory and limited weapons + pre-defined armor class

    def __init__(self, Name, HP, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma, *initWeapons, armorClass = None):
            super(enemy, self).__init__(Name, HP, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma)
            if armorClass != None:
                self.armorClass = armorClass
            self.enemyWeapons = initWeapons
    def __str__(self):
        return (("""
                Name: {}
                HP:   {}/{}
                """).format(self.Name, self.HP, self.maxHP))
    def attack(self, target): # Only attacks player character, not other enemies
        if isinstance(target, player) == False:
            raise Exception()
        else:
            super(enemy, self).attack(self.enemyWeapons[random.randint(0, (len(self.enemyWeapons)-1))], target) #Choose random weapon from list
            
	
class player(being, inventory.inventoryObj, inventory.equippedItems): # Player character object, includes inventory, class, race and spells
    def __init__(self, Name, HP, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma, *initWeapons, initArmor = None, initShield = None, Race = None, Class = None, spellList = None): #*initSpells, *initItems
        being.__init__(self, Name, HP, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma)
        self.Race = Race
        self.Class = Class
        self.handsFree = 2
        self.playerInventory = inventory.inventoryObj(None) #Typically *initItems, dummied out to None due to time constraints.
        self.spellList = spellList #This would normally be another object containing an array, likely based off inventoryObj - was never implemented.
        if len(initWeapons) != 0 and initArmor != None and initShield != None:
            self.playerEquipment = inventory.equippedItems(initWeapons, initEquipArmor = initArmor, initEquipShield = initShield)
		
    def __str__(self):
        stringToReturn = (("""
        Name:   {}
        Race:   {}
        Class:  {}
        HP:     {}/{}
        """).format(self.Name, self.Race, self.Class, self.HP, self.maxHP))
        stringToReturn += being.__str__(self)
        return stringToReturn

    def equipItem(self, itemToEquip):
            if itemToEquip not in self.playerInventory.inventoryList:
                    print("Item does not exist")
                    return False
            else:
                if isinstance(itemToEquip, inventory.armor) == True:
                        if itemToEquip.strReq <= self.Strength: # If we meet strength requirements of armor
                                itemToEquip.isItemEquipped = True
                                if itemToEquip.armorType == "light": # Set AC to baseAC + dexMod
                                        self.armorClass = itemToEquip.baseAC + self.returnMod(self.Dexterity) 
                                elif itemToEquip.armorType == "medium": # Set AC to baseAC + dexMod or 2, whichever is lowest
                                        if self.returnMod(self.Dexterity) >= 2:
                                                # TODO: Remember to account for shield AC when changing armor!!!!!
                                                self.armorClass = itemToEquip.baseAC + 2
                                        elif self.returnMod(self.Dexterity) < 2:
                                                self.armorClass = itemToEquip.baseAC + self.returnMod(self.Dexterity)
                                elif itemToEquip.armorType == "heavy": # No dex modifier added
                                        self.armorClass = itemToEquip.baseAC
                                self.addEquipment(itemToEquip)
                                self.removeItem(itemToEquip)
                                # TODO: check to see if armor is already equipped before attempting to equip more (so players can't just stack AC!)
                        else:
                            print("You don't meet the strength requirements to wear this armor.")
                            return False
                elif isinstance(itemToEquip, inventory.weapon) == True:
                        if itemToEquip.handsRequired > self.handsFree:
                                raise Exception # If not enough hands to hold weapon (i.e. player tries to do something outside 5e's rules on equipping items)
                        else:
                                self.addEquipment(itemToEquip)
                                self.removeItem(itemToEquip)
                                self.handsFree -= itemToEquip.handsRequired
                                
                elif isinstance(itemToEquip, inventory.shield) == True:
                        if itemToEquip.handsRequired > self.handsFree:
                                raise Exception # same here as line 105. Both should cover all 'illegal' attempts to equip stuff that shouldn't be there.
                        else:
                                self.addEquipment(itemToEquip)
                                self.armorClass += itemToEquip.baseAC
                                self.removeItem(itemToEquip)
                                self.handsFree -= itemToEquip.handsRequired
    
    def unequipItem(self, itemToUnequip):
            if itemToUnequip not in self.playerEquipment.equipmentList:
                print("Item is already unequipped or you don't own it!")
                return False
            else:
                if isinstance(itemToUnequip, inventory.armor) == True: 
                    # TODO: again, account for shield AC.
                    self.armorClass = 10 + self.returnMod(self.Dexterity)
                            
                elif isinstance(itemToUnequip, inventory.shield) == True:
                    self.armorClass -= itemToUnequip.baseAC # This should account for armor AC.
                #Additional note: I think this line does account for armor AC?
                    self.handsFree += itemToUnequip.handsRequired

                elif isinstance(itemToUnequip, inventory.weapon) == True:
                    self.handsFree += itemToUnequip.handsRequired

                else: 
                    raise Exception() # Panic
            
            self.removeEquipment(itemToUnequip)
            self.addItem(itemToUnequip)
    
    def dead(self, killer): # Special game over line when player dies
            print(("{} meets their end from {}, ending their adventure.").format(self.Name, killer))
            quit()