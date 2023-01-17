def config(variant):
    print("Entered Local Site Config")
    config = dict()
    config["sys_prefix"] = "None"
    config["MPICC"] = "mpicc"
    return config


def init(variant):
    return ""