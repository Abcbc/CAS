import random as r


class Actors:
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
        "BALANCED": [-1 if x%2==0 else 1 for x in range[DEFAULT_COMPLEXITY]],
        "INVERTED_BALANCE": [1 if x%2==0 else -1 for x in range[DEFAULT_COMPLEXITY]]
    }

    @staticmethod
    def create(opinions):
        return {Actors.KEY_OPINIONS: opinions}

    @staticmethod
    def create(c_type=0, complexity=DEFAULT_COMPLEXITY,):
        if c_type == Actors.TYPES['RANDOM']:
            return Actors.create([r.choice([-1,0,1]) for x in range(complexity)])

    @staticmethod
    def create(negative_weight, postive_weight, neutral_weight, complexity=DEFAULT_COMPLEXITY):
        """
        Creates an actor with opinions.
        :param negative_weight:
        :param postive_weight:
        :param neutral_weight:
        :param complexity: length of the opinions
        :return: A Actor with relative opinions to the weights you've sets at randome positions.
        """
        distribution_list = Actors.create_distribution_list(negative_weight, postive_weight, neutral_weight, complexity)

        opinions = [None for x in range(complexity)]
        indices = [x for x in range(complexity)]
        while not distribution_list:
            idx = indices.pop(r.choice(indices))
            opinions[idx] = distribution_list.pop()

        return Actors.create(opinions=[0 if x is None else x for x in opinions])

    @staticmethod
    def create_distribution_list(negative_weight, postive_weight, neutral_weight, complexity=DEFAULT_COMPLEXITY):
        steps = (negative_weight + postive_weight + neutral_weight) / complexity
        return [-1 for x in range(int(negative_weight / steps))] + \
                [1 for x in range(int(postive_weight / steps))] + \
                 [0 for x in range(int(negative_weight / steps))]


    @staticmethod
    def breed(actorA={}, actorB={}, breed_method = ""):
        return {}

    @staticmethod
    def breed(actor, deviation):
        """

        :param actor: An Actor which is used as an orgin
        :param deviation: is a value between 0.f and 1.f
        :return: an Actor with a defined deviation to its orgin
        """

        origin = actor[Actors.KEY_OPINIONS]
        complexity = len(range(origin))
        alter_steps =int(complexity/deviation)
        result = [None for x in range(complexity)]
        indices = [x for x in range(complexity)]

        while indices:
            idx = indices.pop(r.choice(indices))
            if alter_steps >= 0:
                result[idx] = r.choice([x for x in range(-1,1) if x != origin[idx]])
                alter_steps-=1
            else:
                result[idx] = origin[idx]
        return Actors.create(opinions=result)




    @staticmethod
    def getArchitype(archetype):
        return Actors.ARCHETYPES[archetype]

    @staticmethod
    def createTroll(actor):
        return Actors.create([Actors.__invert(x) for x in actor[Actors.KEY_OPINIONS] ])

    @staticmethod
    def __invert( value):
        return r.choice([1,-1]) if value== 0 else value*-1