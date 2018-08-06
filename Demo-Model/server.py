from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import MoneyModel

def agent_portrayal(agent):
    if agent.type == 1:
        portrayal = {
            "Shape": "circle",
            "Color": "red",
            "Filled": "true",
            "Layer": 0,
            "r": 0.5,
            }
    else:
        portrayal = {
            "Shape": "rect",
            "Color": "blue",
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1,
            }
    return portrayal

grid = CanvasGrid(agent_portrayal, 30, 30, 600, 600)

server = ModularServer(MoneyModel, [grid], "Demo Model", {"N": 100})
