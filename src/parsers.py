from src.classes.System import System
from src.classes.Neuron import Neuron
from src.classes.Synapse import Synapse
from src.classes.Terminal import Terminal
from src.classes.Position import Position
from src.classes.Rule import Rule

import re


def get_symbol_value(s: str) -> int:
    if s == "0":
        return 0
    elif s == "a":
        return 1
    else:
        return int(s.replace("a", ""))


def parse_rule_xmp(s: str) -> Rule:
    result = re.match("(.*)/(\d*a)->(\d*a|0);(\d+)", s)
    regex, consumed, produced, delay = result.groups()

    consumed = int(get_symbol_value(consumed))
    produced = int(get_symbol_value(produced))
    delay = int(delay)

    return Rule(regex, consumed, produced, delay)


def parse_neuron_xmp(d: dict[str, any], to_id: dict[str, int]) -> Neuron:
    id = to_id[d["id"]]
    label = d["id"]
    position = Position(
        round(float(d["position"]["x"])), round(float(d["position"]["y"]))
    )
    rules = list(map(parse_rule_xmp, d["rules"].split())) if "rules" in d else []
    spikes = int(d["spikes"])
    downtime = int(d["delay"]) if "delay" in d else 0

    return Neuron(id, label, position, rules, spikes, downtime)


def parse_dict_xmp(d: dict[str, any], filename: str) -> System:
    to_id = {}
    current_id = 0

    for k in d.keys():
        if k in to_id:
            print("Duplicate neuron found!")
            exit()
        else:
            to_id[k] = current_id
            current_id += 1

    neurons = []
    synapses = []
    input_neurons = []
    output_neurons = []

    for v in d.values():
        neurons.append(parse_neuron_xmp(v, to_id))

    for v in d.values():
        id = to_id[v["id"]]

        if "isInput" in v and v["isInput"] == "true":
            s = v["bitstring"] if "bitstring" in v and v["bitstring"] else ""
            input_neurons.append(Terminal(id, Terminal.compress(s)))

        if "isOutput" in v and v["isOutput"] == "true":
            s = v["bitstring"] if "bitstring" in v and v["bitstring"] else ""
            output_neurons.append(Terminal(id, Terminal.compress(s)))

        if "outWeights" in v:
            for inner_k, inner_v in v["outWeights"].items():
                start = id
                end = to_id[inner_k]
                weight = int(inner_v)
                synapses.append(Synapse(start, end, weight))

    return System(filename, neurons, synapses, input_neurons, output_neurons)


def parse_position(d: dict[str, any]) -> Position:
    x = int(d["x"])
    y = int(d["y"])

    return Position(x, y)


def parse_rule(d: dict[str, any]) -> Rule:
    regex = d["regex"]
    consumed = int(d["consumed"])
    produced = int(d["produced"])
    delay = int(d["delay"])

    return Rule(regex, consumed, produced, delay)


def parse_neuron(d: dict[str, any]) -> Neuron:
    id = int(d["id"])
    label = d["label"]
    position = parse_position(d["position"])
    rules = [parse_rule(rule) for rule in d["rules"]]
    spikes = int(d["spikes"])
    downtime = int(d["downtime"])

    return Neuron(id, label, position, rules, spikes, downtime)


def parse_synapse(d: dict[str, any]) -> Neuron:
    start = int(d["from"])
    end = int(d["to"])
    weight = int(d["weight"])

    return Synapse(start, end, weight)


def parse_terminal(d: dict[str, any]) -> Terminal:
    id = int(d["id"])
    spike_times = list(map(int, d["spikeTimes"]))

    return Terminal(id, spike_times)


def parse_dict(d: dict[str, any]) -> System:
    name = d["name"]
    neurons = [parse_neuron(neuron) for neuron in d["neurons"]]
    synapses = [parse_synapse(synapse) for synapse in d["synapses"]]
    input_neurons = [parse_terminal(input_neuron) for input_neuron in d["inputNeurons"]]
    output_neurons = [
        parse_terminal(output_neuron) for output_neuron in d["outputNeurons"]
    ]

    return System(name, neurons, synapses, input_neurons, output_neurons)
