import pandas as pd
import os


CSV_DIR="./CSV"

OUT="./processed/power_source.csv"



# =========================
# 读取函数
# =========================

def read_csv(file):

    path=os.path.join(
        CSV_DIR,
        file
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
            "",
            "NULL",
            "nan",
            "None"
        ],
        pd.NA,
        inplace=True
    )


    return df




# =========================
# 读取数据
# =========================


main_equipment=read_csv(
    "EQUIP_JBS_ZWEQUIPINFO.csv"
)


main_terminal=read_csv(
    "EQUIP_JBS_ZWTERMINAL.csv"
)


pw_equipment=read_csv(
    "EQUIP_JBS_PWEQUIPINFO.csv"
)


pw_terminal=read_csv(
    "EQUIP_JBS_PWTERMINAL.csv"
)


pw_feeder=read_csv(
    "EQUIP_JBS_PWFEEDERLINE.csv"
)



print(
    "主网设备:",
    len(main_equipment)
)


print(
    "主网端子:",
    len(main_terminal)
)


print(
    "配网端子:",
    len(pw_terminal)
)



# =========================
# 1. 主网电源设备
# =========================


MAIN_SOURCE_TYPES={

    "1301",   # 母线

    "1321"    # 断路器

}



main_source=main_equipment[

    main_equipment["EQUIP_TYPE"]
    .isin(
        MAIN_SOURCE_TYPES
    )

]



source_ids=set(

    main_source["EQUIP_ID"]

)



print(
    "主网候选电源设备:",
    len(source_ids)
)



# =========================
# 2. 主网电源节点
# =========================


main_source_terminal=main_terminal[

    main_terminal["EQUIP_ID"]
    .isin(
        source_ids
    )

]



source_nodes=set(

    main_source_terminal[
        "CONNECTIVITYNODE_ID"
    ]

)



print(
    "主网电源连接节点:",
    len(source_nodes)
)



# =========================
# 3. 配网端子节点
# =========================


pw_terminal_valid=pw_terminal[

    pw_terminal["CONNECTIVITYNODE_ID"]
    .isin(
        source_nodes
    )

]



print(
    "匹配到主网节点的配网端子:",
    len(pw_terminal_valid)
)



# =========================
# 4. 获取配网设备
# =========================


source_pw_devices=set(

    pw_terminal_valid[
        "EQUIP_ID"
    ]

)



print(
    "配网电源入口设备:",
    len(source_pw_devices)
)



# =========================
# 5. 映射馈线
# =========================


feeder_map=pw_equipment[

    pw_equipment["EQUIP_ID"]
    .isin(
        source_pw_devices
    )

]



result=feeder_map[

    [
        "EQUIP_ID",
        "EQUIP_NAME",
        "FEEDER_ID",
        "DSUBSTATION_ID"

    ]

].drop_duplicates()



result["HAS_SOURCE"]=1


result["SOURCE_TYPE"]="MAIN_BUS"



# =========================
# 输出
# =========================


result.to_csv(

    OUT,

    index=False,

    encoding="utf-8-sig"

)



print("================")

print(
    "生成电源馈线数量:",
    len(result)
)


print(
    result.head()
)
