import rdflib

# 補助関数：URI からローカル名を抽出
def local_name(uri):
    return str(uri).split("#")[-1]

# RDFのTurtleデータ
rdf_data = """
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

# RDFLibでグラフをパース
g = rdflib.Graph()
g.parse(data=rdf_data, format="turtle")

nodes = {}  # {ノード名: ラベル}
edges = []  # (出発ノード, 関係, 到達ノード)

# RDFトリプルの走査
for s, p, o in g:
    # 型情報の取得 (rdf:type)
    if p == rdflib.RDF.type:
        s_name = local_name(s)
        label = local_name(o)
        nodes[s_name] = label
    else:
        s_name = local_name(s)
        predicate = local_name(p)
        if isinstance(o, rdflib.URIRef):
            o_name = local_name(o)
            edges.append((s_name, predicate, o_name))
        else:
            # リテラルの場合はプロパティとして扱えますが、ここでは除外
            pass

# Cypherクエリの生成（ノード作成）
print("// ノードの作成")
for node, label in nodes.items():
    # MERGE で重複作成を防止
    print(f"MERGE ({node}:{label} {{name:'{node}'}});")

print("\n// リレーションシップの作成")
# Cypherクエリの生成（リレーションシップ作成）
for s, pred, o in edges:
    # すでにノードは MERGE で作成済みなので、MERGE でリレーションシップを作成
    print(f"MERGE ({s}) MERGE ({o}) MERGE ({s})-[:{pred}]->({o});")
