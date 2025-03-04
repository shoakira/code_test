import rdflib
import networkx as nx
import matplotlib.pyplot as plt

# Turtle形式のRDFデータ
turtle_data = """
@prefix : <http://example.com#>.

# オブジェクトの定義
:robot1 a :Robot.
:ball   a :Object.
:table  a :Location.
:target a :Location.

# 状態の定義
:at_ball_table a :AtState;
               :object :ball;
               :location :table.
:hand_empty_robot1 a :State;
                   :actor :robot1.
:holding_robot1_ball a :State;
                     :object :ball;
                     :actor :robot1.
:at_ball_target a :AtState;
                :object :ball;
                :location :target.

# アクションの定義と関係性
:pick_up a :Action;
         :hasPrecondition :at_ball_table, :hand_empty_robot1;
         :hasEffect :holding_robot1_ball;
         :target :ball;
         :actor :robot1.
:place a :Action;
       :hasPrecondition :holding_robot1_ball;
       :hasEffect :at_ball_target;
       :target :ball;
       :actor :robot1.
"""

# RDFLibでグラフを作成してTurtleデータをパース
g = rdflib.Graph()
g.parse(data=turtle_data, format="turtle")

# NetworkXの有向グラフを作成
G = nx.DiGraph()

# 各ノードの型を記録する辞書
node_types = {}

# URIからローカル名を抽出する補助関数
def local_name(x):
    if isinstance(x, rdflib.URIRef):
        return str(x).split("#")[-1]
    else:
        return str(x)

# RDFトリプルをネットワークグラフに変換
for s, p, o in g:
    s_name = local_name(s)
    p_name = local_name(p)
    # oがURIRefの場合のみlocal nameを取得（リテラルの場合はそのまま文字列）
    o_name = local_name(o) if isinstance(o, rdflib.URIRef) else str(o)
    
    # ノードの追加（URIRefの場合のみ）
    if isinstance(s, rdflib.URIRef) and s_name not in G:
        G.add_node(s_name)
    if isinstance(o, rdflib.URIRef) and o_name not in G:
        G.add_node(o_name)
    
    # predicate が rdf:type（"a"）の場合、型情報として保存
    if p == rdflib.RDF.type:
        node_types[s_name] = o_name
    else:
        # その他のトリプルはエッジとして追加
        G.add_edge(s_name, o_name, label=p_name)

# ノードの型に基づく色設定
color_map = {
    "Robot": "skyblue",
    "Object": "lightgreen",
    "Location": "yellow",
    "AtState": "orange",
    "State": "orange",
    "Action": "violet"
}
node_colors = []
for node in G.nodes():
    node_type = node_types.get(node, "default")
    node_colors.append(color_map.get(node_type, "lightgrey"))

# グラフのレイアウト計算と描画
pos = nx.spring_layout(G, seed=42)  # seedを固定して毎回同じ配置に
plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.axis("off")
plt.title("RDFグラフの可視化")
plt.show()
