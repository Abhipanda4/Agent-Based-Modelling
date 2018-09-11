from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import World

def agent_portrayal(agent):
    if agent.type == "explorer":
        return {
                "Shape": "circle",
                "Filled": "true",
                "Layer": 0.2,
                "Color": "blue",
                "r": 0.8,
                }
    elif agent.type == "exploiter":
        return {
                "Shape": "circle",
                "Filled": "true",
                "Layer": 0.2,
                "Color": "red",
                "r": 0.5,
                }
    else:
        return {
                "Shape": "rect",
                "Filled": "true",
                "Layer": 0,
                "Color": "green",
                "w": 1,
                "h": 1,
                }

grid = CanvasGrid(agent_portrayal, 100, 100, 800, 800)
server = ModularServer(World, [grid], "Demo", {"N": 100, "coop": 0.5, "e_prob": 0.5})
