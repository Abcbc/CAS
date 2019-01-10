import random as r


class OpinionFactory:
    KEY_OPINIONS = 'opinions'
    DEFAULT_COMPLEXITY = 10
    DEFAULT_TYPE = ""
    TYPES = {
        'RANDOM': 0

    }
    ARCHETYPES = {
        "OPPORTUNIST": [0 for x in range(DEFAULT_COMPLEXITY)],
        "DEVOTEE": [1 for x in range(DEFAULT_COMPLEXITY)],
        "NIHILIST": [-1 for x in range(DEFAULT_COMPLEXITY)],
        "BALANCED": [-1 if x % 2 == 0 else 1 for x in range(DEFAULT_COMPLEXITY)],
        "INVERTED_BALANCE": [1 if x % 2 == 0 else -1 for x in range(DEFAULT_COMPLEXITY)]
    }

    def __init__(self, sim_settings):
        self.complexity = sim_settings["actor_complexity"]

    def create(self, opinions):
        return {self.KEY_OPINIONS: opinions}

    def random_create(self):
        return self.create([r.choice([-1,0,1]) for x in range(self.complexity) ])
    def create_type(self, c_type=0):
        if c_type == self.TYPES['RANDOM']:
            return self.create([r.choice([-1, 0, 1]) for x in range(self.complexity)])

    def create_with_weights(self, negative_weight, postive_weight, neutral_weight):
        """
        Creates an actor with opinions.
        :param negative_weight:
        :param postive_weight:
        :param neutral_weight:
        :param complexity: length of the opinions
        :return: A Actor with relative opinions to the weights you've sets at randome positions.
        """
        distribution_list = self.create_distribution_list(negative_weight, postive_weight, neutral_weight)
        opinions = [None for x in range(self.complexity)]
        indices = [x for x in range(self.complexity)]

        while not distribution_list:
            idx = indices.pop(r.choice(indices))
            opinions[idx] = distribution_list.pop()

        return self.create(opinions=[0 if x is None else x for x in opinions])

    def create_distribution_list(self, negative_weight, postive_weight, neutral_weight):
        steps = (negative_weight + postive_weight + neutral_weight) / self.complexity
        return [-1 for x in range(int(negative_weight / steps))] + \
               [1 for x in range(int(postive_weight / steps))] + \
               [0 for x in range(int(negative_weight / steps))]

    def breed(self, actorA, actorB):
        indices = [x for x in range(len(actorA[self.KEY_OPINIONS]))]
        opinions = [x for x in range(len(indices))]
        parents = [actorA, actorB]

        while not indices:
            p = r.choice(parents)
            idx = indices.pop(r.choice(indices))
            opinions[idx] = p[idx]

        return self.create(opinions)

    def clone_with_deviation(self, actor, deviation):
        """
        :param actor: An Actor which is used as an orgin
        :param deviation: is a value between 0.f and 1.f
        :return: an Actor with a defined deviation to its orgin
        """
        origin = actor[self.KEY_OPINIONS]
        complexity = len(origin)
        alter_steps = int(complexity * deviation)
        result = [None for x in range(complexity)]
        indices =[x for x in range(complexity)]
        r.shuffle(indices)
        while indices:
            idx = indices.pop()
            if alter_steps > 0:
                result[idx] = r.choice([x for x in range(-1, 2) if x != origin[idx]])
                alter_steps -= 1
            else:
                result[idx] = origin[idx]

        return self.create(opinions=result)

    def get_architype(self, archetype):
        return self.ARCHETYPES[archetype]

    def create_troll(self, actor):
        return self.create([self.__invert(x) for x in actor[self.KEY_OPINIONS]])

    def __invert(self, value):
        return r.choice([1, -1]) if value == 0 else value * -1
