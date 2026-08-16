import argparse
import os
import pandas as pd


def uuid_from_uri(series: pd.Series) -> pd.Series:
    return series.str.rsplit("/", n=1).str[-1]


def build_occupations(esco_dir: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(esco_dir, "occupations_en.csv"), dtype=str)
    df["esco_uuid"] = uuid_from_uri(df["conceptUri"])
    df["regulated"] = (
        df["regulatedProfessionNote"]
        .fillna("")
        .str.strip()
        .str.endswith("/regulated")
    )
    out = df[["esco_uuid", "code", "iscoGroup", "preferredLabel", "regulated"]].rename(
        columns={"iscoGroup": "isco_group", "preferredLabel": "label"}
    )
    return out


def build_occupation_skills(esco_dir: str) -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(esco_dir, "occupationSkillRelations_en.csv"), dtype=str
    )
    df["esco_uuid"] = uuid_from_uri(df["occupationUri"])
    df["skill_uuid"] = uuid_from_uri(df["skillUri"])
    out = df[
        ["esco_uuid", "skill_uuid", "skillLabel", "relationType", "skillType"]
    ].rename(
        columns={
            "skillLabel": "skill_label",
            "relationType": "relation",
            "skillType": "skill_type",
        }
    )
    return out


def build_mapping(esco_dir: str) -> pd.DataFrame:
    
    df = pd.read_csv(
        os.path.join(esco_dir, "EURESmapping_occs_FR.csv"),
        sep=";",
        skiprows=16,
        encoding="latin-1",
        dtype=str,
    )
    df.columns = [
        "esco_uri", "esco_id", "esco_label", "esco_url",
        "rome_uri", "rome_appellation_id", "rome_label", "rome_url",
        "skos", "note",
    ]
    df["esco_uuid"] = uuid_from_uri(df["esco_uri"])
    df["skos_match"] = df["skos"].str.replace("skos:", "", regex=False)
    out = df[["rome_appellation_id", "esco_uuid", "rome_label", "skos_match"]].dropna(
        subset=["rome_appellation_id", "esco_uuid"]
    )
    return out


def sanity_check(occ, skills, mapping):
    print("\n=== SANITY CHECK: ROME appellation -> ESCO -> essential skills ===")
    sample = mapping[mapping["skos_match"] == "exactMatch"].iloc[0]
    rome_id, uuid = sample["rome_appellation_id"], sample["esco_uuid"]
    label = occ.loc[occ["esco_uuid"] == uuid, "label"]
    label = label.iloc[0] if len(label) else "(unmapped)"
    print(f"ROME appellation {rome_id}  ->  ESCO {uuid}  ({label})")

    ess = skills[(skills["esco_uuid"] == uuid) & (skills["relation"] == "essential")]
    print(f"essential skills ({len(ess)}):")
    for s in ess["skill_label"].head(10):
        print("   -", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--esco-dir", default="./esco")
    ap.add_argument("--out", default="./out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    occ = build_occupations(args.esco_dir)
    skills = build_occupation_skills(args.esco_dir)
    mapping = build_mapping(args.esco_dir)

    occ.to_csv(os.path.join(args.out, "esco_occupations.csv"), index=False)
    skills.to_csv(os.path.join(args.out, "esco_occupation_skills.csv"), index=False)
    mapping.to_csv(os.path.join(args.out, "mapping_rome_esco.csv"), index=False)

    print("Tables written to", args.out)
    print(f"  esco_occupations       : {len(occ):>7,} rows "
          f"({occ['regulated'].sum()} regulated)")
    print(f"  esco_occupation_skills : {len(skills):>7,} rows")
    print(f"  mapping_rome_esco      : {len(mapping):>7,} rows "
          f"({mapping['esco_uuid'].nunique()} ESCO occs covered)")

    sanity_check(occ, skills, mapping)


if __name__ == "__main__":
    main()
