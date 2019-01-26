import yaml as yml
import os
import re
import itertools
import copy
import math
config_path = "/".join([os.getcwd(), "configs", "simulations.yml"])


def get_groups(config):
    return [config[x] for x in config]


def set_defaults(group):
    defaults = group.get("defaults")
    result = [group[x] for x in group if x != "defaults"]

    if defaults is not None:
        for default_key in defaults:
            for e in result:
                if e.get(default_key) is None:
                    e.update({default_key: defaults.get(default_key)})

    return result


def load_config(cfg_file = None):
    if cfg_file is not None:
        config = yml.load(open(cfg_file, "r")).get("simulation_settings")
    else:
        config = yml.load(open(config_path, "r")).get("simulation_settings")
    result = []

    for group in get_groups(config):
        result += set_defaults(group)

    return result

def save_config(config, file):
    """

    :param config: assumed to be the config for one run, not a group
    :param file:
    :return:
    """
    yml.dump({"simulation_settings":{'group':{'config':config}}},open(file, "w"))


regex_float_lit_str = '\d+(\.\d+)?'
regex_range_identifier = re.compile('^range.*')
regex_range = re.compile('^range\((?P<first>'+regex_float_lit_str+'):(?P<step>'+regex_float_lit_str+'):(?P<last>'+regex_float_lit_str+')\)$')
regex_list_identifier = re.compile('^list.*')
regex_list = re.compile('^list\((?P<items>(.+,?)*)\)$')

def config_generator(config, iterator_keys, combinations):
    while True:
        try:
            inst = next(combinations)
            for pos, key in enumerate(iterator_keys):
                config[key] = inst[pos]
            yield config
        except StopIteration:
            return

def get_iteration_steps(config):
    # 1. find all iterator commands
    iterator_params = _findIterators(config)
    iterables = [_build_iterable(it_param[1]) for it_param in iterator_params]

    return config_generator(config, [it_param[0] for it_param in iterator_params], itertools.product(*iterables))

# interators are returned alphabetically ordered with respect to the key
def _findIterators(configDict):
    iterator_keys = []
    iterator_strings = []
    for key, value in configDict.items():
        if type(value) == type({}):
            iterator_keys_, iterator_strings_ = _findIterators(value)
            iterator_keys += iterator_keys_
            iterator_strings += iterator_strings_
        elif type(value) == type(''):
            range_match = regex_range.fullmatch(value)
            list_match = regex_list.fullmatch(value)
            if range_match is not None or list_match is not None:
                iterator_keys.append(key)
                iterator_strings.append(value)

    return sorted(zip(iterator_keys, iterator_strings), key=itemgetter(0))

def _build_iterable(it_str):
    range_match = regex_range.fullmatch(it_str)
    list_match = regex_list.fullmatch(it_str)

    if range_match is not None:
        first = float(range_match.group('first'))
        step = float(range_match.group('step'))
        last = float(range_match.group('last'))
        return range_it(first, last, step)
    elif list_match is not None:
        list = list_match.group('items').split(':')
        return list_it(list)

# form the list to list of integers or floats if possible
def list_it(_list):
    isNumber = False
    try:
        f = float(_list[0]) # if no exception => is float => expect all members to be numbers
        isNumber = True
    except ValueError:
        pass
    list = None
    if isNumber:
        try:
            list = [int(v) for v in _list] # try to read integers
        except ValueError:
            list = [float(v) for v in _list] # else expect floats, raise error if something is not a number
    else:
        list = _list
    for v in list:
        yield v
    return

def range_it(first, last, step):
    is_integer = math.remainder(first,1) < 1e-10 and math.remainder(last,1) < 1e-10 and math.remainder(step,1) < 1e-10
    n = 0
    while first + n*step <= last:
        yield first + n*step if not is_integer else int(first + n*step)
        n += 1
    return
