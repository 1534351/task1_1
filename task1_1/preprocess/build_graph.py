import pandas as pd
import networkx as nx
import os


DATA_DIR="./processed"

OUTPUT="task1_1_result.xlsx"

DEBUG="task1_component_debug.csv"


# ==========================
# CSV读取
# ==========================

def load_csv(filename):

    path=os.path.join(
        DATA_DIR,
        filename
    )

    df=pd.read_csv(
        path,
        dtype=str,
        encoding="utf-8-sig"
    )


    # 清洗三引号

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
            "None",
            ""
        ],
        "",
        inplace=True
    )


    return df



# ==========================
# 数据读取
# ==========================


equipment=load_csv(
    "equipment_clean.csv"
)


node=load_csv(
    "node.csv"
)


edge=load_csv(
    "edge.csv"
)


terminal=load_csv(
    "terminal_clean.csv"
)


power=load_csv(
    "power_source.csv"
)



# ==========================
# 设备信息
# ==========================


equipment_dict=(

    equipment
    .set_index(
        "EQUIP_ID"
    )
    .to_dict(
        "index"
    )

)



valid_devices=set(
    equipment_dict.keys()
)



# ==========================
# 类型规则
# ==========================


# 比赛给出的末端豁免

END_TYPES={

    "1703",
    "1707",
    "1713",
    "1719",
    "1714"

}



# 不参与一次拓扑

IGNORE_TYPES={

    "1720"

}



def get_type(eid):

    if eid not in equipment_dict:

        return ""

    return str(
        equipment_dict[eid]
        .get(
            "EQUIP_TYPE",
            ""
        )
    )



def is_non_terminal(eid):


    t=get_type(eid)


    if t in END_TYPES:

        return False


    if t in IGNORE_TYPES:

        return False


    return True




def info(eid):

    return equipment_dict.get(
        eid,
        {}
    )



# ==========================
# 建立设备拓扑
# ==========================


G=nx.Graph()


for eid in valid_devices:

    G.add_node(eid)



edge=edge[

    edge["SOURCE"].isin(valid_devices)

    &

    edge["TARGET"].isin(valid_devices)

]



for _,r in edge.iterrows():

    G.add_edge(

        r["SOURCE"],

        r["TARGET"]

    )



print(
    "设备:",
    G.number_of_nodes()
)

print(
    "连接:",
    G.number_of_edges()
)



# ==========================
# 电源馈线
# ==========================


power_feeders=set(

    power["LINE_ID"]

)



# ==========================
# 结果
# ==========================


result=[]



def append_result(
    eid,
    reason
):


    d=info(eid)


    result.append({

        "二级分类":
        "1.1 设备拓扑悬空检测任务",


        "问题设备id":
        eid,


        "问题设备名称":
        d.get(
            "EQUIP_NAME",
            ""
        ),


        "所属馈线":
        d.get(
            "FEEDER_ID",
            ""
        ),


        "所属厂站":
        d.get(
            "DSUBSTATION_ID",
            ""
        ),


        "问题说明":
        reason

    })



# ==================================================
# 异常1：单端悬空
# ==================================================


for eid in G.nodes:


    if not is_non_terminal(eid):

        continue



    degree=G.degree(eid)


    if degree<=1:


        append_result(

            eid,

            "该设备为非末端设备，仅存在单侧拓扑连接，存在悬空端点"

        )





# ==================================================
# 连通区域分析
# ==================================================


components=list(

    nx.connected_components(G)

)



debug=[]



# ==================================================
# 异常2、异常3
# ==================================================


for idx,comp in enumerate(components):


    devices=[]


    feeders=set()


    for eid in comp:


        if eid not in equipment_dict:

            continue


        if is_non_terminal(eid):

            devices.append(eid)


        feeder=info(eid).get(
            "FEEDER_ID",
            ""
        )


        if feeder:

            feeders.add(
                feeder
            )



    has_power=bool(

        feeders
        &
        power_feeders

    )



    debug.append({

        "component":
        idx,

        "设备数量":
        len(comp),

        "非末端数量":
        len(devices),

        "馈线":
        ",".join(feeders),

        "是否有电源":
        has_power

    })



    if has_power:

        continue



    # -----------------------
    # 异常2
    # -----------------------


    if len(devices)>=2:


        for eid in devices:


            append_result(

                eid,

                "多个非末端设备形成连片拓扑区域，但无法追溯有效馈线电源"

            )



    # -----------------------
    # 异常3
    # -----------------------


    elif len(devices)==1:


        append_result(

            devices[0],

            "所在拓扑区域无有效馈线电源来源，疑似无母线接入拓扑孤岛"

        )





# ==========================
# 输出
# ==========================


result_df=pd.DataFrame(
    result
)



result_df.drop_duplicates(
    inplace=True
)



result_df.to_excel(
    OUTPUT,
    index=False
)



pd.DataFrame(
    debug
).to_csv(
    DEBUG,
    index=False,
    encoding="utf-8-sig"
)



print("================")

print(
    "异常数量:",
    len(result_df)
)


print(
    "输出:",
    OUTPUT
)


print(
    "调试:",
    DEBUG
)