import pandas as pd
import networkx as nx
import os


DATA="./processed"

OUTPUT="task1_1_result_v3.xlsx"

DEBUG="task1_debug_v3.csv"



# =====================
# 读取
# =====================

def read_csv(name):

    df=pd.read_csv(
        os.path.join(DATA,name),
        dtype=str,
        encoding="utf-8-sig"
    )


    df.columns=[
        str(c)
        .replace('"',"")
        .strip()
        for c in df.columns
    ]


    for c in df.columns:

        df[c]=(
            df[c]
            .astype(str)
            .str.replace('"',"")
            .str.strip()
        )


    df.replace(
        [
            "nan",
            "NULL",
            "",
            "None"
        ],
        "",
        inplace=True
    )

    return df



equipment=read_csv(
    "equipment_clean.csv"
)


edge=read_csv(
    "edge.csv"
)


terminal=read_csv(
    "terminal_clean.csv"
)


power=read_csv(
    "power_source.csv"
)


feeder_trace=read_csv(
    "feeder_power_trace.csv"
)


main_terminal=read_csv(
    "main_terminal_clean.csv"
)



# =====================
# 设备信息
# =====================


equip_dict=(

equipment
.set_index(
    "EQUIP_ID"
)
.to_dict(
    "index"
)

)


devices=set(
    equip_dict.keys()
)



# =====================
# 类型规则
# =====================


END_TYPES={

"1703",
"1707",
"1713",
"1714",
"1719"

}


IGNORE_TYPES={

"1720"

}



def is_non_terminal(eid):

    t=equip_dict[eid]["EQUIP_TYPE"]

    if t in END_TYPES:
        return False

    if t in IGNORE_TYPES:
        return False

    return True



# =====================
# 建图
# =====================


G=nx.Graph()

G.add_nodes_from(
    devices
)



edge=edge[

edge["SOURCE"].isin(devices)

&
edge["TARGET"].isin(devices)

]


for _,r in edge.iterrows():

    G.add_edge(
        r["SOURCE"],
        r["TARGET"]
    )



# =====================
# 电源信息
# =====================


source_feeders=set(

power["FEEDER_ID"]

)



# 馈线主网追踪

feeder_main=dict(

zip(

feeder_trace["FEEDER_ID"],

feeder_trace["是否连接主网"]

)

)



# =====================
# 主网节点
# =====================


main_nodes=set(

main_terminal[
"CONNECTIVITYNODE_ID"
]

)



# =====================
# 主网连接辅助
# =====================


def has_main_connection(comp):


    if "CONNECTIVITYNODE_ID" not in terminal.columns:

        return False


    nodes=set(

        terminal[
            terminal["EQUIP_ID"]
            .isin(comp)
        ]["CONNECTIVITYNODE_ID"]

    )


    return bool(
        nodes
        &
        main_nodes
    )



# =====================
# 输出
# =====================


result=[]


def add_result(eid,reason,typ):

    d=equip_dict[eid]

    result.append({

        "二级分类":
        "1.1设备拓扑悬空检测任务",

        "问题设备id":
        eid,

        "问题设备名称":
        d["EQUIP_NAME"],

        "所属馈线":
        d["FEEDER_ID"],

        "所属厂站":
        d["DSUBSTATION_ID"],

        "问题说明":
        reason,

        "异常类型":
        typ,

        "修正方案":
        "",

        "修正SQL":
        ""

    })



# =====================
# 异常1
# =====================


for eid in G.nodes:


    if not is_non_terminal(eid):

        continue


    if G.degree(eid)<=1:

        add_result(

            eid,

            "非末端设备仅存在单侧拓扑连接，存在单端悬空端点",

            "单端悬空端点"

        )



# =====================
# component分析
# =====================


debug=[]



for idx,comp in enumerate(
    nx.connected_components(G)
):


    non_terms=[]

    feeders=set()



    for eid in comp:


        if is_non_terminal(eid):

            non_terms.append(eid)


        f=equip_dict[eid]["FEEDER_ID"]

        if f:

            feeders.add(f)



    if len(non_terms)==0:

        continue



    # ----------

    # 电源判断

    # ----------


    has_source=bool(

        feeders

        &

        source_feeders

    )



    # ----------

    # 主网追踪

    # ----------


    main_power=False


    for f in feeders:


        if feeder_main.get(f,"0")=="1":

            main_power=True



    debug.append({

        "component":idx,

        "设备数量":len(comp),

        "非末端数量":len(non_terms),

        "馈线数量":len(feeders),

        "馈线":",".join(feeders),

        "power_source":
        has_source,

        "feeder_trace":
        main_power

    })



    # =================
    # 异常2
    # =================


    if (

        len(non_terms)>=2

        and

        not has_source

        and

        not main_power

    ):


        for eid in non_terms:


            add_result(

                eid,

                "多个非末端设备形成连片拓扑区域，但区域所有馈线均无法追溯有效电源",

                "多设备连片悬空"

            )



    # =================
    # 异常3
    # =================


    elif (

        len(non_terms)>0

        and

        len(feeders)>0

        and

        not main_power

    ):


        for eid in non_terms:


            add_result(

                eid,

                "所属馈线无法追溯至主网母线或电源出口，无母线接入拓扑孤岛",

                "无母线接入拓扑孤岛"

            )




# =====================
# 输出
# =====================


pd.DataFrame(result)\
.drop_duplicates()\
.to_excel(

OUTPUT,

index=False

)



pd.DataFrame(debug)\
.to_csv(

DEBUG,

index=False,

encoding="utf-8-sig"

)



print("================")

print(
"异常数量:",
len(result)
)

print(
"结果:",
OUTPUT
)

print(
"调试:",
DEBUG
)
