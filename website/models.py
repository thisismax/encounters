from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from random import choice, randint

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    combats = db.relationship("Combat")

    username = db.Column(db.String(150), unique=True)
    # password_hash = db.Column(db.String(150))

    # @staticmethod
    # def set_password(password):
    #      return generate_password_hash(password)

    # def verify_password(self, password):
    #     return check_password_hash(self.password_hash, password)


class Combat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combat_key = db.Column(db.String(8), unique=True)
    combatName = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    combatants = db.relationship("Combatant")

    @staticmethod
    def set_combat_key():
        letters = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        key = ""
        for i in range(8):
            key += choice(letters)
        return key

    # used to make sure combat has combatants before querying database
    def getCombatCount(self):
        return Combatant.query.filter(Combatant.combat_id==self.id).count()

    def getFirstPosition(self):
        return (Combatant
            .query
            .filter_by(combat_id=self.id)
            .order_by(Combatant.combatPosition.desc())
            .first()
        )

    def getLastPosition(self):
        return (Combatant
            .query
            .filter_by(combat_id=self.id)
            .order_by(Combatant.combatPosition)
            .first()
        )

    # getNextPosition and getPrevPosition could probably be combined if I were cleverer
    def getPrevPosition(self,currentPosition):
        
        if self.getCombatCount() == 1:
            return Combatant.query.filter_by(combat_id=self.id).first()
        
        nextCombatant = (Combatant.query.filter(
                Combatant.combat_id==self.id,
                Combatant.combatPosition>currentPosition
            )
            .order_by(Combatant.combatPosition)
            .first()
        )

        if nextCombatant:
            return nextCombatant
        else:
            return None
    
    def getNextPosition(self,currentPosition):
        
        if self.getCombatCount() == 1:
            return Combatant.query.filter_by(combat_id=self.id).first()

        nextCombatant = (Combatant.query.filter(
                Combatant.combat_id==self.id,
                Combatant.combatPosition<currentPosition
            )
            .order_by(Combatant.combatPosition.desc())
            .first()
        )

        if nextCombatant:
            return nextCombatant
        else:
            return self.getFirstPosition()

    def getActiveCombatant(self):
        
        return (Combatant.query.filter(
            Combatant.combat_id==self.id,
            Combatant.active==True,
            ).first()
        )

    def newCombatantPosition(self):

        if not self.getCombatCount():
            return 0
        else:
            return self.getFirstPosition().combatPosition+1

    def rollInitiative(self):
        
        if not self.getCombatCount():
            return False
        
        combatants = Combatant.query.filter_by(combat_id=self.id).all()

        rolls = []

        for combatant in combatants:
            combatant.rollInitiative()

            for i in range(10):
                if combatant.combatPosition in rolls:
                    combatant.combatPosition += (10**-i)*choice([-1,1])
                    continue
                break

            rolls.append(combatant.combatPosition)

        # agh this is redundant code with "getFirstPosition"
        #firstCombatant = Combatant.query.filter_by(combat_id=self.id).order_by(Combatant.combatPosition.desc()).first()
        firstCombatant = self.getFirstPosition()
        firstCombatant.active = True
    
    def nextCombatant(self):

        # check that there are combatants
        if not self.getCombatCount():
            return None

        currentCombatant = self.getActiveCombatant()
        print(currentCombatant.combatantName, currentCombatant.active)

        if currentCombatant:
            nextCombatant = self.getNextPosition(currentCombatant.combatPosition)
            print(nextCombatant.combatantName, nextCombatant.active)

            currentCombatant.active = False
            nextCombatant.active = True
        else:
            self.getFirstPosition().active = True


        

class Combatant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combat_id = db.Column(db.Integer, db.ForeignKey('combat.id'))

    combatantName = db.Column(db.String(150))
    initiativeBonus = db.Column(db.Integer)
    damage = db.Column(db.Integer)
    randomInitiative = db.Column(db.Boolean)
    combatPosition = db.Column(db.Float)
    active = db.Column(db.Boolean)

    def rollInitiative(self):
        self.active = False
        if self.randomInitiative:
            self.combatPosition = randint(1,20)+self.initiativeBonus
            
        return self.combatPosition