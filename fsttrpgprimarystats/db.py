from peewee import *
database = SqliteDatabase('stats.db')


class PrimaryStats(Model):
    character_name = CharField(unique=True)
    role = CharField()
    intelligence = IntegerField()
    reflexes = IntegerField()
    technique = IntegerField()
    dexterity = IntegerField()
    presense = IntegerField()
    willpower = IntegerField()
    constitution = IntegerField()
    strength = IntegerField()
    body = IntegerField()
    move = IntegerField()

    def save_character(self, character_name, role, intelligence, reflexes, technique, dexterity, presense, willpower,
                      constitution, strength, body, move):
        new_character, created = PrimaryStats.get_or_create(character_name=character_name,
                                                            role=role,
                                                            defaults={'intelligence':intelligence,
                                                                      'reflexes':reflexes,
                                                                      'technique':technique,
                                                                      'dexterity':dexterity,
                                                                      'presense':presense,
                                                                      'willpower':willpower,
                                                                      'constitution':constitution,
                                                                      'strength':strength,
                                                                      'body':body,
                                                                      'move':move})

        if created:
            print('created new character')
        else:
            print('modifying character')
            new_character.intelligence = intelligence
            new_character.reflexes = reflexes
            new_character.technique = technique
            new_character.dexterity = dexterity
            new_character.presense = presense
            new_character.willpower = willpower
            new_character.constitution = constitution
            new_character.strength = strength
            new_character.body = body
            new_character.move = move
            new_character.save()

    def get_character(self, name):
        return PrimaryStats.get(PrimaryStats.character_name==name)

    class Meta:
        database = database

class DBManager(object):
    def __init__(self):
        super(DBManager, self).__init__()
        database.connect()
        database.create_tables([PrimaryStats], safe=True)
        self.table_primary_stats = PrimaryStats()

    def __del__(self):
        database.close()