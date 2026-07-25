import pandas as pd
import os


# ============================
# 路径配置
# ============================

DATA_DIR = "./csv"

OUTPUT_DIR = "./processed"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================
# CSV读取函数
# ============================

def read_csv(filename):

    path = os.path.join(
        DATA_DIR,
        filename
    )


    if not os.path.exists(path):

        print(
            "文件不存在:",
            path
        )

        return pd.DataFrame()


    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype=str
    )


    # 字段清洗

    df.columns = [
        str(c)
        .replace('"',"")
        .strip()
        for c in df.columns
    ]


    # 内容清洗

    for col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace('"',"")
            .str.strip()
        )


    # 空值统一

    df.replace(
        [
            "",
            "NULL",
            "null",
            "nan",
            "None"
        ],
        pd.NA,
        inplace=True
    )


    return df



# ============================
# 1. 设备表处理
# ============================


print("\n=====设备表处理=====")


equip = read_csv(
    "EQUIP_JBS_PWEQUIPINFO.csv"
)


need_cols = [
    "EQUIP_ID",
    "EQUIP_NAME",
    "EQUIP_TYPE",
    "VOLTAGE_TYPE",
    "FEEDER_ID",
    "DSUBSTATION_ID",
    "COMPOSITESWITCH"
]


# 保留需要字段

equip = equip[
    [
        c for c in need_cols
        if c in equip.columns
    ]
]


# ID异常检查

quality=[]



for col in [
    "EQUIP_ID",
    "FEEDER_ID",
    "DSUBSTATION_ID"
]:

    if col in equip.columns:

        count = (
            equip[col]
            .isna()
            .sum()
        )


        quality.append(
            {
                "table":"equipment",
                "check":col+"缺失",
                "number":count
            }
        )


# ID重复

duplicate = (
    equip["EQUIP_ID"]
    .duplicated()
    .sum()
)


quality.append(
    {
        "table":"equipment",
        "check":"EQUIP_ID重复",
        "number":duplicate
    }
)



equip.to_csv(
    OUTPUT_DIR+
    "/equipment_clean.csv",
    index=False,
    encoding="utf-8-sig"
)



# ============================
# 2. 拓扑表处理
# ============================


print("\n=====拓扑表处理=====")


terminal = read_csv(
    "EQUIP_JBS_PWTERMINAL.csv"
)



terminal_cols=[
    "ID",
    "EQUIP_ID",
    "CONNECTIVITYNODE_ID"
]


terminal=terminal[
    [
        c for c in terminal_cols
        if c in terminal.columns
    ]
]



# 删除无设备连接

before=len(terminal)


terminal.dropna(
    subset=[
        "EQUIP_ID",
        "CONNECTIVITYNODE_ID"
    ],
    inplace=True
)


after=len(terminal)


quality.append(
    {
        "table":"terminal",
        "check":"拓扑连接缺失",
        "number":before-after
    }
)



terminal.to_csv(
    OUTPUT_DIR+
    "/terminal_clean.csv",
    index=False,
    encoding="utf-8-sig"
)



# ============================
# 3. 类型字典处理
# ============================


print("\n=====类型映射=====")


obj = read_csv(
    "JBS_ZD_OBJECT.csv"
)



if not obj.empty:


    obj=obj[
        [
            "OBJ_CODE",
            "OBJ_CNNAME"
        ]
    ]



    equip = equip.merge(
        obj,
        left_on="EQUIP_TYPE",
        right_on="OBJ_CODE",
        how="left"
    )



    equip.rename(
        columns={
            "OBJ_CNNAME":
            "EQUIP_TYPE"
        },
        inplace=True
    )



    equip.to_csv(
        OUTPUT_DIR+
        "/equipment_clean.csv",
        index=False,
        encoding="utf-8-sig"
    )



# ============================
# 4. 构建设备节点表
# ============================


print("\n=====节点生成=====")



node=equip[
    [
        "EQUIP_ID",
        "EQUIP_NAME",
        "EQUIP_TYPE"
    ]
]


node.to_csv(
    OUTPUT_DIR+
    "/node.csv",
    index=False,
    encoding="utf-8-sig"
)



# ============================
# 5. 构建设备连接边
# ============================


print("\n=====边生成=====")



node_map={}



for _,row in terminal.iterrows():

    n=row["CONNECTIVITYNODE_ID"]

    e=row["EQUIP_ID"]


    if n not in node_map:

        node_map[n]=[]


    node_map[n].append(e)



edges=[]



for n,devices in node_map.items():


    # 同一连接节点设备两两连接

    for i in range(len(devices)):

        for j in range(
            i+1,
            len(devices)
        ):

            edges.append(
                {
                    "SOURCE":
                    devices[i],

                    "TARGET":
                    devices[j],

                    "CONNECTIVITYNODE":
                    n
                }
            )



edge=pd.DataFrame(edges)



edge.to_csv(
    OUTPUT_DIR+
    "/edge.csv",
    index=False,
    encoding="utf-8-sig"
)



# ============================
# 6. 保存质量报告
# ============================


pd.DataFrame(
    quality
).to_csv(
    OUTPUT_DIR+
    "/quality_report.csv",
    index=False,
    encoding="utf-8-sig"
)



print("\n=====处理完成=====")

print(
    "设备数量:",
    len(node)
)

print(
    "连接数量:",
    len(edge)
)