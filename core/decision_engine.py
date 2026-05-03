def create_engine(flow):
    return {
        "flow": flow,
        "nodes": flow["nodes"],
        "current": flow["start"],
        "state": {}
    }


def get_node(engine):
    return engine["nodes"][engine["current"]]


def update_state(engine, key, value):
    engine["state"][key] = value


def eval_condition(engine, condition):
    try:
        return eval(condition, {}, engine["state"])
    except:
        return False


def next_node(engine):
    node = get_node(engine)

    for t in node.get("transitions", []):
        if eval_condition(engine, t["when"]):
            engine["current"] = t["goto"]
            return

    print("[!] No valid transition found")
