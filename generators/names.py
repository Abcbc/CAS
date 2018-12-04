import os
import random as r

first_name_path = "\\".join([os.getcwd(), "configs", "first_names.txt"])
last_name_path = "\\".join([os.getcwd(), "configs", "last_names.txt"])

last_name = []
first_name = []

def load_names():
    global last_names, first_names
    last_name = [x for x in open(last_name_path, "r")]
    first_name = [x for x in open(first_name_path, "r")]

def generate_name():
    return "{} {}".format(r.choice(first_name), r.choice(last_name))

