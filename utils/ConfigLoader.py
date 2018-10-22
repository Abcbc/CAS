config_path = "\\".join([os.getcwd(), "configs", "simulations.yml"])

def get_groups(config):
	return [config[x] for x in config]
	
def set_defaults(group):
	defaults = group.get("defaults")
	result = [group[x] for x in group if x != "defaults"]
    
	for default_key in defaults:
        print(default_key)
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
