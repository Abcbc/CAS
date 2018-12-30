import yaml as yml
import os
import re
import itertools
import copy
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


def load_config():
    config = yml.load(open(config_path, "r")).get("simulation_settings")
    result = []

    for group in get_groups(config):
        result += set_defaults(group)

    return result

regex_float_lit_str = '\d+(\.\d+)?'
regex_range_identifier = re.compile('^range.*')
regex_range = re.compile('^range\((?P<first>'+regex_float_lit_str+'):(?P<step>'+regex_float_lit_str+'):(?P<last>'+regex_float_lit_str+')\)$')
regex_list_identifier = re.compile('^list.*')
regex_list = re.compile('^list\((?P<items>(.+,?)*)\)$')

def get_iteration_steps(config):
    step_configs = []

    # 1. find all iterator commands
    iterator_keys, iterator_strings = _findIterators(config)
    iterables = [_build_iterable(it_str) for it_str in iterator_strings]

    # 2. iterate through  all iterator commands
    for combination in itertools.product(*iterables):
        _config = copy.deepcopy(config)
        for pos, key in enumerate(iterator_keys):
            _config[key] = combination[pos]
        step_configs.append(_config)

    return step_configs

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

    return iterator_keys, iterator_strings

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
        return list

def range_it(first, last, step):
        n = 0
        while first + n*step <= last:
            yield first + n*step
            n += 1
        return
