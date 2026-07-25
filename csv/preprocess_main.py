import pandas as pd
import os


DATA_DIR="./CSV"
OUT_DIR="./processed"

os.makedirs(
    OUT_DIR,
    exist_ok=True
)



def read_clean(filename):

    path=os.path.join(
        DATA_DIR,
        filename
    )


    df=pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype=str
    )


    # 清洗三引号表头
    df.columns=[
        c.replace('"',"")
        .strip()
        for c in df.columns
    ]


    # 清洗数据
    for c in df.columns:

        df[c]=(
            df[c]
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



# =========================
# 1 主网设备
# =========================


zw_equip=read_clean(
    "EQUIP_JBS_ZWEQUIPINFO.csv"
)



zw_equip.to_csv(
    OUT_DIR+
    "/main_equipment_clean.csv",
    index=False,
    encoding="utf-8-sig"
)



# =========================
# 2 主网拓扑
# =========================


zw_terminal=read_clean(
    "EQUIP_JBS_ZWTERMINAL.csv"
)



zw_terminal=zw_terminal[
    [
        "ID",
        "EQUIP_ID",
        "CONNECTIVITYNODE_ID"
    ]
]



zw_terminal.dropna(
    subset=[
        "EQUIP_ID",
        "CONNECTIVITYNODE_ID"
    ],
    inplace=True
)



zw_terminal.to_csv(
    OUT_DIR+
    "/main_terminal_clean.csv",
    index=False,
    encoding="utf-8-sig"
)



# =========================
# 3 生成主网电源节点
# =========================


# 主网设备类型暂全部保留
# 后续通过OBJ字典映射


source=[]



for _,row in zw_equip.iterrows():


    source.append(
        {
            "EQUIP_ID":
            row["EQUIP_ID"],

            "EQUIP_TYPE":
            row["EQUIP_TYPE"],

            "ST_ID":
            row["ST_ID"]
        }
    )



source_df=pd.DataFrame(source)



source_df.to_csv(
    OUT_DIR+
    "/main_source_candidate.csv",
    index=False,
    encoding="utf-8-sig"
)



print(
    "主网处理完成"
)

print(
    "主网设备:",
    len(zw_equip)
)

print(
    "主网拓扑:",
    len(zw_terminal)
)