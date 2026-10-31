from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "playset" / "source_playset.json"
PLAYSET_OUT = ROOT / "playset" / "Josheyer_Historical.json"
ORDER_OUT = ROOT / "playset" / "collection_order.txt"
DESCRIPTION_OUT = ROOT / "description.txt"

REPO = "Josheyerr/josheyer-historical-collection"
IMG = f"https://raw.githubusercontent.com/{REPO}/main/images"
JSON_PAGE = f"https://github.com/{REPO}/blob/main/playset/Josheyer_Historical.json"
DISCORD = "https://discord.gg/rwdGCanWpA"
MAX_DESCRIPTION = 8000
FIXES_ID = "3797139319"
HOLY_DEPOSITION = {"displayName": "Holy Deposition", "steamId": "3830498440"}

CATEGORIES = [
    (
        "core",
        "Foundation and Fixes",
        "The base everything stands on: the community bug-fix patch, plus two mods made for this "
        "playset. Holy Deposition adds a crusade-style war for adventurers, and the fixes mod glues "
        "the whole pack together.",
        ["3797139319", "3830498440", "2871648329"],
    ),
    (
        "realm",
        "Realm and Vassals",
        "Deeper feudal politics: contracts you can renegotiate, vassals with agency, crown authority "
        "that matters, legitimacy that builds over time and realistic succession.",
        [
            "3305687550", "3604729196", "3351630685", "3499199200", "2779619112", "2712590542",
            "2692957667", "3006877184", "3595280210", "3766246044", "2650385452", "3194153945",
            "3361162762", "3442769560", "3340544163",
        ],
    ),
    (
        "war",
        "Warfare",
        "Historic invasions arrive on time, armies get regional men-at-arms, commanders matter more "
        "and battles look and feel bigger.",
        [
            "2837398670", "3599748822", "3461530706", "3567954900", "3101905160", "3716251917",
            "3200520888", "2429466948", "2818979385", "3817429748",
        ],
    ),
    (
        "court",
        "Court, Characters and Events",
        "Living courts and believable families: hundreds of new events, smarter AI education and "
        "marriage, new lifestyles, court positions and character traits.",
        [
            "2893554112", "3655093103", "2654374260", "2657499830", "2751980550", "3045026915",
            "3597166528", "3433842378", "3157170996", "3593415435", "3678529052", "2662352702",
            "3596393244", "2875403237", "3158566134", "3602600136", "2756456587", "3360676953",
            "2753934263", "3616853064", "2748508571", "2721974781", "3445721977", "3571752592",
            "3548614933", "2677152091", "2478202444", "2227658180", "3729520553", "3822387325",
            "3813479895",
        ],
    ),
    (
        "faith",
        "Religion and Culture",
        "Richer faiths, traditions and cultures across Europe, Africa and the Middle East, plus "
        "historical titles and coats of arms.",
        [
            "3107648868", "2893793966", "2241658518", "3827420629", "2829397295", "3798537678",
            "3800861092", "3823057506",
        ],
    ),
    (
        "art",
        "Portraits and Graphics",
        "Expanded ethnicities, clothing, hairstyles and eyes, new holding and building art, "
        "illustrations and loading screens.",
        [
            "2227406359", "2220098919", "2507209632", "3546414558", "2996881191", "2452585382",
            "2509797306", "2764329234", "3360781295", "3765421308", "2553043828", "3186143971",
            "3255992492", "2783349674", "3599447506", "3828759915", "3150612985", "2986496756",
            "3788376803", "3809288964",
        ],
    ),
    (
        "ui",
        "Interface and Quality of Life",
        "Better search, camera, notifications, battle and struggle views, and nicer designers.",
        [
            "3084203091", "2243723476", "2261468688", "3077627057", "3030427202", "2766055258",
            "2427934113", "2636170225", "2220326926", "3350459101",
        ],
    ),
]


def load_order() -> list[dict]:
    mods = json.loads(SOURCE.read_text(encoding="utf-8"))["mods"]
    enabled = [m for m in sorted(mods, key=lambda m: m["position"]) if m["enabled"]]
    if not any(m["steamId"] == HOLY_DEPOSITION["steamId"] for m in enabled):
        fixes_index = next(i for i, m in enumerate(enabled) if m["steamId"] == FIXES_ID)
        enabled.insert(fixes_index, {**HOLY_DEPOSITION, "enabled": True})
    return [{**m, "position": i} for i, m in enumerate(enabled)]


def check_categories(order: list[dict]) -> None:
    ids = [i for _, _, _, cat in CATEGORIES for i in cat]
    in_order = {m["steamId"] for m in order}
    missing = in_order - set(ids)
    extra = set(ids) - in_order
    dupes = {i for i in ids if ids.count(i) > 1}
    if missing or extra or dupes:
        raise SystemExit(f"category mismatch: missing={missing} extra={extra} dupes={dupes}")


def description(order: list[dict]) -> str:
    names = {m["steamId"]: m["displayName"] for m in order}
    count = len(order)
    out = [
        f"[img]{IMG}/banner.jpg[/img]",
        "",
        f"[i]{count} hand-picked mods for a grounded, historical Crusader Kings III. The full load "
        "order is included as a ready-made playset file, conflicts are patched, and everything is "
        "tested together on 1.20.[/i]",
        "",
        f"[img]{IMG}/box_summary.png[/img]",
        "",
        f"[url={DISCORD}][img]{IMG}/discord.png[/img][/url]",
        f"Questions, crashes or suggestions? Ask on the [url={DISCORD}]Discord[/url].",
        "",
        f"[img]{IMG}/header_install.png[/img]",
        "[olist]",
        "[*][b]Subscribe to all[/b] with the green button above, and let Steam finish downloading.",
        f"[*]Download the playset file: [url={JSON_PAGE}]Josheyer_Historical.json[/url] (use the download button on that page).",
        "[*]In the Paradox launcher, open [b]Playsets[/b], then [b]Import playset[/b], and choose the file. "
        "Every mod lands in the right order, with the right ones enabled.",
        "[*]Start a [b]new game[/b]. This setup is not save-compatible.",
        "[/olist]",
        "",
        f"[img]{IMG}/header_load.png[/img]",
        "[list]",
        "[*][b]Unofficial Patch[/b] loads first.",
        "[*]Gameplay mods follow, then culture and religion, then portraits, graphics and interface.",
        "[*][b]Holy Deposition[/b] loads second to last.",
        "[*][b]Josheyer Historical Modpack Fixes[/b] loads [b]last[/b], always. It repairs title creation, "
        "hairstyles and culture conflicts between the mods above.",
        "[/list]",
        "",
    ]
    for key, title, blurb, ids in CATEGORIES:
        out += [
            f"[img]{IMG}/header_{key}.png[/img]",
            f"[img]{IMG}/icon_{key}.png[/img] {blurb}",
            "[list]",
            *[f"[*]{names[i]}" for i in sorted(ids, key=lambda i: [m['steamId'] for m in order].index(i))],
            "[/list]",
            "",
        ]
    out += [
        f"[img]{IMG}/header_notes.png[/img]",
        "[list]",
        "[*]Supported version: [b]1.20.*[/b].",
        "[*]Holy Deposition's war needs the [i]Roads to Power[/i] DLC. Everything else runs without it.",
        "[*]RICE, Africa Plus, More Holding Graphics, Historical Accuracy and a few older patches are "
        "intentionally left out. The fixes mod covers what their compatches leave behind.",
        "[*]If you add your own mods, keep them above the fixes mod.",
        f"[*]Bug reports and support: [url={DISCORD}]Discord[/url].",
        "[/list]",
        "",
        "[i]Every mod here belongs to its author. Please rate and support the original mods.[/i]",
    ]
    return "\n".join(out) + "\n"


def main() -> None:
    order = load_order()
    check_categories(order)
    PLAYSET_OUT.write_text(
        json.dumps({"game": "ck3", "name": "Josheyer Historical", "mods": order}, indent=2) + "\n",
        encoding="utf-8",
    )
    ORDER_OUT.write_text("\n".join(m["steamId"] for m in order) + "\n", encoding="utf-8")
    text = description(order)
    if len(text.encode("utf-8")) > MAX_DESCRIPTION:
        raise SystemExit(f"description is {len(text.encode('utf-8'))} bytes, Steam allows {MAX_DESCRIPTION}")
    DESCRIPTION_OUT.write_text(text, encoding="utf-8")
    print(f"{len(order)} mods, description {len(text)} chars")


if __name__ == "__main__":
    main()
