import networkx as nx

from networkx.readwrite.graphml import write_graphml, read_graphml
import json
from fuzzywuzzy import fuzz

def create_network(year):
    #Load data set
    with open(f"data/courses_{year}.json","r") as f:
        courses = json.load(f)
    with open(f"data/areas.json","r") as f:
        areas = json.load(f)
        
    #Build network    
    G = nx.Graph(year=year)
    for c in courses:
        for code in c["edges"].keys():
            G.add_edge(f'{c["faculty"]["code"]}_{c["code"]}',code,weight = c["edges"][code],weight_1 = 1/c["edges"][code])
    for c in courses:
        try:
            area = [a for a,b in areas.items() if c["name"] in b][0]
        except IndexError as e:
            area = [max([fuzz.ratio(x.lower().split("(")[0].strip(), c["name"].lower().split("(")[0].strip()) for x in a]) for a in areas.values()]
            area = list(areas.keys())[area.index(max(area))]
            # print(f'{c["name"]}, {c["faculty"]["code"]}{c["code"]} not found')
        G.add_node(f'{c["faculty"]["code"]}_{c["code"]}',name=c["name"],
                       faculty_name=c["faculty"]["name"],faculty_type=c["faculty"]["type"],
                       candidates=c["candidates"],accepted=c["Accepted"],vagas=c["vagas"],
                       grade=c["grade"], area=area)
    #Drop isolates
    G.remove_nodes_from([n for n,x in G.nodes(data=True) if x and x['grade']==0])
    return G

def export_network(G):
    if year := G.graph["year"]:
        write_graphml(G,f"networks/graph_{year}.graphml")
        
def import_networks():
    networks = []
    for year in range(2018,2022):
        G = read_graphml(f"networks/graph_{year}.graphml")
        G.graph["year"] = year
        networks.append(G)
    return networks