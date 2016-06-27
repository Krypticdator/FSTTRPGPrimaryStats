from traits.api import *
from traitsui.api import *

import models
from fsttrpgcharloader.traitsmodels import list_of_actors, CharacterName
from db import DBManager

class RandomStatsConfiguration(HasTraits):
    character_point_limit = Range(-1, 100, mode='spinner')
    character_point_min = Range(-1, 100, mode='spinner')
    number_of_ones_allowed = Int(default_value=0)
    number_of_tens_allowed = Int(default_value=1)


class Stats(HasTraits):
    configure_random = Instance(RandomStatsConfiguration, ())
    intelligence = Range(1, 10, mode='spinner')
    reflexes = Range(1, 10, mode='spinner')
    technique = Range(1, 10, mode='spinner')
    dexterity = Range(1, 10, mode='spinner')
    strength = Range(1, 10, mode='spinner')
    constitution = Range(1, 10, mode='spinner')
    presense = Range(1, 10, mode='spinner')
    body = Range(1, 10, mode='spinner')
    move = Range(1, 10, mode='spinner')
    willpower = Range(1, 10, mode='spinner')

    luck = Int()
    humanity = Int()
    recovery = Int()
    endurance = Int()
    run = Int()
    sprint = Int()
    swim = Int()
    leap = Int()
    hits = Int()
    stun = Int()
    stun_defense = Int()
    resistance = Int()


    roll_random_stats = Button()

    character_points_allocated = Int()

    full_view = View(
        Group(
            Item('configure_random'),
            Item('roll_random_stats', show_label=False),
        ),
        Item('character_points_allocated', style='readonly'),
        HGroup(
            Group(
                Item('intelligence'),
                Item('reflexes'),
                Item('technique'),
                Item('dexterity'),
                Item('presense'),
                Item('willpower'),
                Item('strength'),
                Item('constitution'),
                Item('move'),
                Item('body')
            ),
            Group(
                Item('luck', style='readonly'),
                Item('humanity', style='readonly'),
                Item('endurance', style='readonly'),
                Item('recovery', style='readonly'),
                Item('run', style='readonly'),
                Item('sprint', style='readonly'),
                Item('swim', style='readonly'),
                Item('leap', style='readonly'),
                Item('hits', style='readonly'),
                Item('stun', style='readonly'),
                Item('stun_defense', style='readonly'),
                Item('resistance', style='readonly')

            )
        )
    )

    def _roll_random_stats_fired(self):
        max_points = self.configure_random.character_point_limit
        min_points = self.configure_random.character_point_min
        tens = self.configure_random.number_of_tens_allowed
        ones = self.configure_random.number_of_ones_allowed
        random_stats = models.randomize(max_points=max_points, min_points=min_points, limit_tens=tens, limit_ones=ones)
        self.intelligence = random_stats.pop()
        self.reflexes = random_stats.pop()
        self.technique = random_stats.pop()
        self.dexterity = random_stats.pop()
        self.presense = random_stats.pop()
        self.strength = random_stats.pop()
        self.constitution = random_stats.pop()
        self.willpower = random_stats.pop()
        self.body = random_stats.pop()
        self.move = random_stats.pop()
    def calculate_luck(self):
        self.luck = (self.intelligence + self.reflexes) / 2

    def calculate_humanity(self):
        self.humanity = self.willpower * 10

    def calculate_resistance(self):
        self.resistance = self.willpower * 3

    def calculate_move_base(self):
        self.run = self.move * 2
        self.sprint = self.move * 3
        self.leap = self.move
        self.swim = self.move

    def calculate_endurance(self):
        self.endurance = self.constitution * 2

    def calculate_recovery(self):
        self.recovery = (self.strength + self.constitution) / 2

    def calculate_body_based(self):
        self.hits = self.body * 5
        self.stun = self.body * 5

    def _intelligence_changed(self):
        self.calculate_luck()
        self.recalculate_cpoints()

    def _reflexes_changed(self):
        self.calculate_luck()
        self.recalculate_cpoints()

    def _tech_changed(self):
        self.recalculate_cpoints()

    def _dexterity_changed(self):
        self.recalculate_cpoints()

    def _willpower_changed(self):
        self.calculate_humanity()
        self.calculate_resistance()
        self.recalculate_cpoints()

    def _body_changed(self):
        self.calculate_body_based()
        self.recalculate_cpoints()

    def _constitution_changed(self):
        self.calculate_endurance()
        self.calculate_recovery()
        self.recalculate_cpoints()

    def _strength_changed(self):
        self.calculate_recovery()
        self.recalculate_cpoints()

    def _move_changed(self):
        self.calculate_move_base()
        self.recalculate_cpoints()

    def recalculate_cpoints(self):
        self.character_points_allocated = self.intelligence + self.reflexes + self.technique + self.dexterity + \
                                          self.presense + self.strength + self.constitution + self.willpower + \
                                          self.body + self.move

class StandaloneContainer(HasTraits):
    character_name = Instance(CharacterName, ())
    transfer_character = Button()
    stats = Instance(Stats, ())
    upload = Button()

    def _transfer_character_fired(self):
        self.name = self.character_name.name.name
        self.role = list_of_actors.get_optional_value(actor=self.name, valuename='role')
        try:
            stats = list_of_actors.get_optional_value(actor=self.name, valuename='stats')
            if stats:
                self.stats.intelligence = stats['intelligence']
                self.stats.reflexes = stats['reflexes']
                self.stats.technique = stats['technique']
                self.stats.dexterity = stats['dexterity']
                self.stats.presense = stats['presense']
                self.stats.strength = stats['strength']
                self.stats.constitution = stats['constitution']
                self.stats.willpower = stats['willpower']
                self.stats.body = stats['body']
                self.stats.move = stats['move']
        except Exception as e:
            print('error retrieving stats')
            print(str(e))


    def _upload_fired(self):
        intelligence = self.stats.intelligence
        reflexes = self.stats.reflexes
        technique = self.stats.technique
        dexterity = self.stats.dexterity
        presense = self.stats.presense
        strength = self.stats.strength
        constitution = self.stats.constitution
        willpower = self.stats.willpower
        body = self.stats.body
        move = self.stats.move
        packed_stats = {'int':intelligence, 'ref':reflexes, 'tech':technique, 'dex':dexterity, 'pre':presense,
                        'str':strength, 'con':constitution, 'will':willpower, 'body':body, 'move':move}
        models.upload_to_aws(name=self.name, role=self.role, packed_stats=packed_stats)
        db_mgr = DBManager()
        db_mgr.table_primary_stats.save_character(character_name=self.name, role=self.role, intelligence=intelligence,
                                                  reflexes=reflexes, technique=technique, dexterity=dexterity,
                                                  presense=presense, strength=strength, constitution=constitution,
                                                  willpower=willpower, body=body, move=move)


    view = View(
        Item('character_name', style='custom', show_label=False),
        HGroup(
            Item('transfer_character', show_label=False)
        ),

        Item('stats', style='custom'),
        Item('upload', show_label=False)
    )

if __name__ == '__main__':
    s = StandaloneContainer()
    db_mgr = DBManager()

    s.configure_traits()