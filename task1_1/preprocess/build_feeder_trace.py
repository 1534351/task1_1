import pandas as pd
import os


CSV_DIR="./CSV"

OUT="./processed/feeder_power_trace.csv"



def read_csv(name):

    path=os.path.join(
        CSV_DIR,
        name
    )

    df=pd.read_csv(
        path,
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



# =========================
# 读取
# =========================


pw_equip=read_csv(
    "EQUIP_JBS_PWEQUIPINFO.csv"
)


pw_feeder=read_csv(
    "EQUIP_JBS_PWFEEDERLINE.csv"
)


pw_terminal=read_csv(
    "EQUIP_JBS_PWTERMINAL.csv"
)


main_terminal=read_csv(
    "EQUIP_JBS_ZWTERMINAL.csv"
)



print(
    "配网设备:",
    len(pw_equip)
)


print(
    "配网端子:",
    len(pw_terminal)
)


print(
    "主网端子:",
    len(main_terminal)
)



# =========================
# 主网节点集合
# =========================


main_nodes=set(

    main_terminal[
        "CONNECTIVITYNODE_ID"
    ]

)


print(
    "主网连接节点:",
    len(main_nodes)
)



# =========================
# 配网设备 -> 节点
# =========================


pw_node_map=(

    pw_terminal[
        [
            "EQUIP_ID",
            "CONNECTIVITYNODE_ID"
        ]
    ]

    .drop_duplicates()

)



equip_nodes={}



for _,r in pw_node_map.iterrows():

    eid=r["EQUIP_ID"]

    node=r["CONNECTIVITYNODE_ID"]


    if eid not in equip_nodes:

        equip_nodes[eid]=set()


    equip_nodes[eid].add(node)



# =========================
# 馈线设备关系
# =========================


feeder_devices=(

    pw_equip[
        [
            "FEEDER_ID",
            "EQUIP_ID"
        ]
    ]

    .drop_duplicates()

)



# =========================
# 馈线追踪
# =========================


results=[]



for feeder,group in feeder_devices.groupby(
    "FEEDER_ID"
):


    devices=set(
        group["EQUIP_ID"]
    )


    feeder_nodes=set()


    for eid in devices:


        if eid in equip_nodes:

            feeder_nodes.update(
                equip_nodes[eid]
            )



    # 是否连接主网

    connect_nodes=(

        feeder_nodes

        &

        main_nodes

    )


    has_main=(
        len(connect_nodes)>0
    )


    results.append({

        "FEEDER_ID":
        feeder,

        "馈线设备数量":
        len(devices),

        "端子节点数量":
        len(feeder_nodes),

        "匹配主网节点数量":
        len(connect_nodes),

        "是否连接主网":
        1 if has_main else 0,

        "状态":
        "正常电源路径"
        if has_main
        else
        "未发现主网入口"

    })



# =========================
# 输出
# =========================


result=pd.DataFrame(results)


result.to_csv(
    OUT,
    index=False,
    encoding="utf-8-sig"
)



print("================")

print(
    "生成:",
    OUT
)


print(
    result["是否连接主网"]
    .value_counts()
)
