#!/usr/bin/env python3
"""
build_route.py — emits public/data/route.json for the Kingdom Hearts Final Mix
100% tracker, and validates it.

Source of truth: cR0Ck's GameFAQs "100% Story" walkthrough for Kingdom Hearts
HD I.5+II.5 ReMIX (KH1 Final Mix), v4 (2023-09-07). Spoiler-free linear route.

Model mirrors zelda-oot-100-tracker:
  route = { meta, categories, phases:[ {id,title,era,blurb,steps:[ {id,title,loc,do,
           missable?,missableNote?, items:[ {id,cat,label,conf?} | tally ] } ] } ] }

Granularity choice: every completion-relevant collectible is itemized individually
(99 Dalmatians as 33 triad chests, 46 Trinities, 13 Ansem's Reports, 9 Postcards,
6 Summons, key Keyblades/abilities, all Olympus Cup challenges, 5 Pooh pages +
minigames, 7 White Mushroom masters, 12 Clock Tower rewards, Gummi blueprints,
Synthesis recipe milestones, the FM superbosses). Generic per-world chest grinds
are represented by a per-chapter "all N treasures swept" checkbox so the player can
confirm a clean sweep without 280 potion rows. The in-game Journal % is final truth.
"""
import json, os, sys, re

PHASES = []

def phase(pid, title, era, blurb):
    p = {"id": pid, "title": title, "era": era, "blurb": blurb, "steps": []}
    PHASES.append(p)
    return p

def step(p, sid, title, loc="", do="", items=None, missable=False, missableNote=None, tip=None):
    s = {"id": sid, "title": title, "loc": loc, "do": do, "items": items or []}
    if missable:
        s["missable"] = True
    if missableNote:
        s["missableNote"] = missableNote
    if tip:
        s["tip"] = tip
    p["steps"].append(s)
    return s

def chk(iid, cat, label, conf=None):
    it = {"id": iid, "cat": cat, "label": label}
    if conf:
        it["conf"] = conf
    return it

def opt(iid, label, conf=None):
    """An optional-but-beneficial activity (free EXP, power gear, money/heal tricks)."""
    return chk("opt-" + iid, "optional", label, conf)

def pups(triad_lo, loc_label):
    """A Dalmatian triad chest. triad_lo is the lowest puppy number (e.g. 16 -> 16,17,18)."""
    a = triad_lo
    return {"id": f"pup-{a}", "cat": "puppy",
            "label": f"Dalmatians {a}, {a+1}, {a+2} — {loc_label}"}

def sweep(world, n):
    return {"id": f"sweep-{world}", "cat": "treasure",
            "label": f"All {n} treasure chests in this world swept"}

# ======================================================================
# 1. THE DREAM START — Destiny Islands
# ======================================================================
p = phase("ch01", "1 · The Dream Start", "Destiny Islands", "Tutorial island. The two PERMANENT character-build choices live here (weapon + growth speed), plus Kairi's fetch quests, Riku's race, free EXP, and the first Keyblade.")
step(p, "s1-weapon", "1.1 Weapon choice — PERMANENT, pick Staff + drop Sword", "Dive to the Heart",
     "You're shown three weapons — Sword (power), Staff (magic), Shield (defense) — and asked which to TAKE (1st choice) and which to GIVE UP. This is locked for the whole game. The weapon you TAKE sets your endgame MP; the one you GIVE UP shifts when Sora learns abilities.",
     [chk("s1-weapon-staff", "story", "TOOK the Staff (1st choice) — locks in 10 MP at endgame"),
      chk("s1-weapon-drop-sword", "story", "GAVE UP the Sword")],
     tip=("Take the STAFF, give up the SWORD. Why it matters: taking the Staff is the ONLY way to "
          "reach 10 MP at level 100 — taking Sword or Shield caps you at 8 MP forever, and MP can't "
          "be raised any other way. KH1's hardest fights (the superbosses, the Hades Cup) lean hard "
          "on magic, so those 2 extra permanent MP are a big deal. Staff(take)/Sword(drop) gives a "
          "balanced Lv100 spread (HP 84 · MP 10 · AP 51 · Atk 46 · Def 48 · 6 item / 3 accessory "
          "slots) and a good ability-learning order. Don't overthink it — this is the single most "
          "important menu in the game."))
step(p, "s1-growth", "1.1 Growth choice — answer mostly OPTION 3", "Destiny Islands — seashore",
     "Talk to Wakka, Selphie and Tidus; each asks a question. Your answers set your leveling CURVE for the whole game (also permanent).",
     [chk("s1-growth-opt3", "story", "Answered the 3 questions mostly Option 3 (fast 41–99)")],
     tip=("Pick mostly OPTION 3. The pattern: mostly Option 1 = level fast from 1–40 but slow 41–99; "
          "Option 2 = even but medium-high requirements the whole way (the worst overall); Option 3 = "
          "slower 1–40 but faster 41–99. Because there are far MORE levels between 41 and 99 than 1–40, "
          "Option 3 gets you to high levels fastest over a full 100% run. (cR0Ck uses Option 3.)"))
step(p, "s1-items", "1.2–1.5 Kairi's item quests", "Destiny Islands",
     "Gather logs, cloth, rope, mushrooms, coconuts, fish, water, seagull egg for Kairi.",
     [chk("s1-protect-chain", "treasure", "Protect Chain accessory (run-area cave)"),
      chk("s1-items-done", "story", "Delivered all of Kairi's items")])
step(p, "s1-race", "1.3 Riku's race (optional — reward: Pretty Stone)", "Destiny Islands — beach",
     "Riku challenges you to a race: touch the yellow star at the far end, then run all the way back to the start. Win to get the Pretty Stone.",
     [chk("s1-pretty-stone", "treasure", "Pretty Stone (win Riku's race)")],
     tip=("Don't chase Riku — take the shortcut. The moment it starts, drop straight off the ledge and "
          "hug the RIGHT side of the beach all the way to the end. Go slightly upstairs, then jump "
          "LEFT four times to reach the yellow star. Touch it and run back along the exact same path "
          "in reverse. Beating him this way is far easier than racing head-on."))
step(p, "s1-spar", "1.2 Optional: free EXP sparring (Ch.1 ONLY)", "Destiny Islands — seashore",
     "Before the island falls, fight the gang for REAL, permanent EXP. Grind to about Lv6 to make Traverse Town and Wonderland noticeably easier — you can never come back here.",
     [opt("dream-exp", "Sparred Wakka/Selphie/Tidus + Riku for free EXP (~Lv6)")],
     missable=True,
     missableNote="Destiny Islands is gone for good after Ch.1 — this free, permanent EXP is only available now.",
     tip=("Per-opponent: WAKKA — hit the balls he throws (1 EXP each, 2 if you knock one back in mid-air; "
          "a return hit stuns him for a few throws). SELPHIE / TIDUS — parry by hitting them as they "
          "swing (1 / 2 EXP). After beating all three, talk to Tidus again to fight all three at once "
          "(reward: a Potion). RIKU — just mash X to rack up parries; a win gives 5 EXP and a Potion. "
          "Equip Stun Impact once you hit Lv6 to speed up the next fights."))
step(p, "s1-keyblade", "1.6 The Keyblade", "Destiny Islands (night)",
     "Storm hits; Sora gets the Keyblade and clears the first bosses.",
     [chk("s1-keyblade-done", "story", "Obtained the Keyblade · world falls")])

# ======================================================================
# 2. TRAVERSE TOWN
# ======================================================================
p = phase("ch02", "2 · Traverse Town", "Hub", "First hub. Postcards #1–6, Blue Trinity intro, Leon, Dalmatians house quest begins. [19 treasures]")
step(p, "s2-postcards-1", "2.1 District 1 & 2 postcards", "Districts 1–2",
     "Climb behind the Accessories shop and hit the Items-shop fan; mail at the red mailbox. Enter the Dalmatians house to start the 99-puppy quest.",
     [chk("pc-1", "postcard", "Postcard #1 (atop Accessories shop) → Cottage"),
      chk("pc-2", "postcard", "Postcard #2 (Items-shop ceiling fan) → Mythril Shard"),
      chk("pc-3", "postcard", "Postcard #3 (District 2 entrance) → Mega-Potion")])
step(p, "s2-leon", "2.3 Fight Leon (win it — reward: Elixir)", "District 1 — Accessories shop",
     "Save with Cid, exit, and you're thrown into a boss fight with Leon. Talk to Yuffie afterward for the keyhole lesson; hit the clock to 7:00 for a rare Mythril chest.",
     [chk("s2-leon-done", "story", "Beat Leon (he gifts an Elixir in District 3 later)"),
      opt("tt-clock-mythril", "Hit the clock to 7:00 → rare Mythril chest (easy to miss)"),
      opt("tt-weapons", "Buy Morning Star (Donald) + Smasher (Goofy) from the Items shop")],
     tip=("Be sure to WIN. The fight is technically scripted — even if you lose, the story continues — "
          "but if you lose you forfeit the Elixir Leon hands you back in District 3 after Guard Armor. "
          "You don't have Dodge Roll yet, so assign Potions to Sora beforehand, keep attacking, and "
          "heal whenever you dip low. (The on-table Elixir and the 7:00 clock Mythril are yours "
          "regardless of the result.)"))
step(p, "s2-guard-armor", "2.4 Guard Armor", "District 3",
     "Cutscene boss. Donald/Goofy join; Sora learns Fire, Goofy teaches Dodge Roll.",
     [chk("s2-brave-warrior", "treasure", "Brave Warrior accessory (boss drop)"),
      chk("s2-guard-armor-done", "story", "Defeated Guard Armor · party formed")])
step(p, "s2-bluetrinity", "2.5 Blue Trinity sweep", "All districts",
     "Learn Trinity Jump; grab the remaining postcards and sweep the world.",
     [chk("pc-4", "postcard", "Postcard #4 (Blue Trinity, District 1) → Mega-Ether"),
      chk("pc-5", "postcard", "Postcard #5 (blue safe, District 1) → Mythril"),
      chk("pc-6", "postcard", "Postcard #6 (District 3 balcony) → Elixir"),
      chk("s2-merlin", "story", "Opened Merlin's house (Fire on the door)"),
      sweep("traverse", 19)])

# ======================================================================
# 3. WONDERLAND
# ======================================================================
p = phase("ch03", "3 · Wonderland", "Difficulty 1", "Trickmaster, Blizzard, White-Mushroom Fire/Blizzard/Thunder masters begin. [18 treasures]")
step(p, "s3-trial", "3.1 Prove Alice innocent", "Lotus Forest / Bizarre Room",
     "Collect 4 evidences; navigate the scrambled Bizarre Rooms. Grab Blizzard.",
     [pups(16, "Lotus Forest, on the lilies"),
      pups(13, "Queen's Court special area (via the pond)"),
      chk("s3-blizzard", "ability", "Blizzard magic"),
      chk("s3-darkmatter", "treasure", "Dark Matter (Tea Garden balcony)")])
step(p, "s3-trickmaster", "3.1 Trickmaster", "Bizarre Room",
     "Boss. Use Fire. Reward: Ifrit's Horn accessory + Navi-G piece.",
     [chk("s3-ifrit-horn", "treasure", "Ifrit's Horn accessory (boss drop)"),
      chk("s3-trickmaster-done", "story", "Defeated Trickmaster")])
step(p, "s3-back-traverse", "3.2 Back in Traverse", "Traverse Town District 1",
     "With Blizzard, douse the entrance candles for a Defense Up. Sweep Wonderland.",
     [opt("megapotion-loop", "Infinite cheap Mega-Potions: give a flower a Potion → Hi-Potion, then the red flower → Mega-Potion (exit/re-enter to reset)"),
      sweep("wonderland", 18)])

# ======================================================================
# 4. OLYMPUS COLISEUM
# ======================================================================
p = phase("ch04", "4 · Olympus Coliseum", "Difficulty 2", "Phil Cup, Cerberus, Hero License, Cloud. [8 treasures]")
step(p, "s4-entrance", "4.1 Coliseum entrance", "Olympus — Open area",
     "Blue Trinities flank the entrance.",
     [pups(22, "Olympus entrance (Blue Trinity, right)"),
      chk("s4-thunder", "ability", "Thunder magic (Phil's trials)")])
step(p, "s4-cerberus", "4.1 Cerberus", "Coliseum",
     "Clear matches 1–6 (no heals), skip/lose match 7 (Cloud), then beat Cerberus. Get Hero License + Sonic Blade.",
     [chk("s4-inferno-band", "treasure", "Inferno Band accessory (Cerberus)"),
      chk("s4-sonic-blade", "ability", "Sonic Blade ability (Cloud scene)"),
      chk("s4-cerberus-done", "story", "Defeated Cerberus · Hero License")])
step(p, "s4-optional", "4.2–4.3 Thunder/Gizmo optionals", "Traverse Town / Wonderland",
     "Thunder the District 3 wire to power the Gizmo shop → Postcards #7–8. Thunder the Wonderland bells for puppies.",
     [chk("pc-7", "postcard", "Postcard #7 (Gizmo clock) → Megalixir"),
      chk("pc-8", "postcard", "Postcard #8 (Gizmo clock) → Orichalcum"),
      pups(58, "Wonderland hidden flower area (Thunder the bells)"),
      opt("obsidian-ring", "Buy Obsidian Ring(s) in Traverse (Dark def stacks, Atk/Def +1) before the cups"),
      sweep("olympus", 8)])

# ======================================================================
# 5. DEEP JUNGLE
# ======================================================================
p = phase("ch05", "5 · Deep Jungle", "Difficulty 3", "Tarzan, Sabor, Clayton/Stealth Sneak, Red Trinity, Cure, Jungle Slider + Vine-Jump minigames. [30 treasures]")
step(p, "s5-story", "5.1 Through the jungle", "Treehouse → Camp → Vines → Grotto",
     "Slide-puzzle of areas; gather puppies, learn Cure after Clayton.",
     [pups(34, "Camp (Blue Trinity)"),
      pups(25, "Hippos area"),
      pups(28, "Vines-2 area"),
      pups(31, "Waterfall Grotto"),
      chk("s5-white-fang", "treasure", "White Fang accessory (Sabor)"),
      chk("s5-cure", "ability", "Cure magic (after Clayton/Stealth Sneak)"),
      chk("s5-jungle-king", "keyblade", "Jungle King Keyblade (world cleared)"),
      chk("s5-red-trinity", "ability", "Red Trinity power (world cleared)")])
step(p, "s5-traverse", "5.2 Traverse Town — new Gummi", "Traverse Town",
     "Red Trinity alley puppies; Secret Waterway opens (Leon, Earthshine Gem → Simba). Bell puzzle → Opposite Armor → Aero. Synthesis still locked.",
     [pups(4, "District 1 alley (Red Trinity)"),
      pups(10, "Secret Waterway (behind Leon's stairs)"),
      chk("s5-earthshine", "treasure", "Earthshine Gem (Leon) → Simba summon"),
      chk("s5-aero", "ability", "Aero magic (Opposite Armor)"),
      chk("s5-tt-keyhole", "story", "Locked the Traverse Town keyhole")])
step(p, "s5-simba", "5.2 Simba summon", "Merlin's house",
     "Give Cid the Old Book → deliver to Merlin → learn Simba from the fairy. 100 Acre Wood Part 1 now available.",
     [chk("s5-simba-summon", "summon", "Simba summon")])
step(p, "s5-minigames", "5.3 Jungle Slider + Vine Jump", "Deep Jungle (Tunnel / Vines)",
     "Slider levels 1–5 give Elixir/AP+/Dark Matter/DIF+/ATT+. Win ≥1 Vine-Jump round — REQUIRED for the Journal/secret ending.",
     [chk("s5-slider", "story", "Jungle Slider levels 1–5 cleared (perma-boost rewards)"),
      chk("s5-vinejump", "story", "Vine-Jump minigame entered in Journal (win ≥1)"),
      sweep("jungle", 30)],
     missable=True,
     missableNote="The Vine-Jump minigame must be played at least once or the Journal can't hit 100% (and on Standard the secret ending won't unlock).")

# ======================================================================
# 6. AGRABAH
# ======================================================================
p = phase("ch06", "6 · Agrabah", "Difficulty 4", "Cave of Wonders, Jafar/Genie Jafar, Ansem's Report 1, Green Trinity → Synthesis unlocks, Genie summon. [41 treasures]")
step(p, "s6-cave", "6.1 Cave of Wonders", "Agrabah / Cave of Wonders",
     "Pot Centipede, Abu statue puzzles, the first Pooh Torn Page, Jafar then Genie Jafar.",
     [pups(37, "Cave of Wonders — Treasure Room"),
      chk("s6-ray-of-light", "treasure", "Ray of Light accessory (Pot Centipede)"),
      chk("s6-torn-page-1", "story", "Torn Page (Dark Chamber) — 100 Acre Wood"),
      chk("rep-1", "report", "Ansem's Report 1 (Genie Jafar)"),
      chk("s6-genie", "summon", "Genie summon"),
      chk("s6-three-wishes", "keyblade", "Three Wishes Keyblade"),
      chk("s6-green-trinity", "ability", "Green Trinity power")],
     missableNote="Push the rock off the Bottomless-Hall cliff and into the Relic Chamber to reach the rare Mythril; the Silent Chamber door needs a later jump upgrade.")
step(p, "s6-synthesis", "6.2 Synthesis unlocks", "Traverse Town — Moguri shop",
     "Green Trinity opens the Moguri Synthesis shop. Postcard #9. Pooh Part 2 → Naturespark → Bambi summon.",
     [pups(7, "Synthesis room (behind the Moogle)"),
      chk("pc-9", "postcard", "Postcard #9 (synthesis-room flier) → AP Up"),
      chk("s6-bambi", "summon", "Bambi summon (Naturespark → fairy)"),
      chk("s6-synth-open", "story", "Moguri Synthesis shop opened"),
      sweep("agrabah", 41)])

# ======================================================================
# 7. MONSTRO
# ======================================================================
p = phase("ch07", "7 · Monstro", "Difficulty 5", "Parasite Cage ×2, High Jump, Stop, Geppetto's Gummi blueprints, Dumbo summon. [29 treasures]")
step(p, "s7-inside", "7.1 Inside the whale", "Chambers 1–6 / The Bowels",
     "Parasite Cage → Cheer; then learn High Jump from the chest by Geppetto.",
     [pups(55, "Chamber 3 (higher level)"),
      pups(76, "Chamber 6 (stairs room)"),
      pups(79, "Chamber 6 (low, blue platforms)"),
      pups(73, "Outside, by Geppetto's boat"),
      chk("s7-torn-page-2", "story", "Torn Page (Chamber 6 blue platforms)"),
      chk("s7-high-jump", "ability", "High Jump (group ability)"),
      chk("s7-stop", "ability", "Stop magic (2nd Parasite Cage)")])
step(p, "s7-agrabah-hj", "7.x Agrabah w/ High Jump", "Agrabah / Cave of Wonders",
     "Return for the high-jump puppies and chests.",
     [pups(52, "Agrabah Palace gates (High Jump)"),
      pups(49, "Cave of Wonders entrance (barrel + jump)"),
      pups(46, "Dark Chamber statue room (High Jump)")])
step(p, "s7-traverse", "7.x Geppetto & Dumbo", "Traverse Town",
     "Geppetto's home → Gummi blueprints (enter 30× → Chocobo; more by mob-kill count). Merlin → Spellbinder Keyblade + Dumbo summon. Buy Magus Staff / Gigas Fist.",
     [chk("s7-dumbo", "summon", "Dumbo summon"),
      chk("s7-spellbinder", "keyblade", "Spellbinder Keyblade (all base spells)"),
      sweep("monstro", 29)])

# ======================================================================
# 8. ATLANTICA
# ======================================================================
p = phase("ch08", "8 · Atlantica", "Difficulty 5", "Swimming world. Ursula ×2, Mermaid Kick, Ansem's Report 3, Crabclaw. [23 treasures]")
step(p, "s8-explore", "8.1 Undersea search", "Triton's Palace / Sunken Ship",
     "Crystal Trident quest, Shark, the Pooh Torn Page in Ariel's grotto, Ursula in her cove → Mermaid Kick.",
     [chk("s8-torn-page-3", "story", "Torn Page (Ariel's Grotto) — grab it"),
      chk("s8-mermaid-kick", "ability", "Mermaid Kick (group ability, Ursula)")])
step(p, "s8-ursula", "8.1 Ursula (rematch)", "??? against the current",
     "Final Ursula. Thundara upgrade, Report 3, then Crabclaw on locking the world.",
     [chk("rep-3", "report", "Ansem's Report 3 (Ursula rematch)"),
      chk("s8-crabclaw", "keyblade", "Crabclaw Keyblade (world locked)"),
      sweep("atlantica", 23)])

# ======================================================================
# 9. HALLOWEEN TOWN
# ======================================================================
p = phase("ch09", "9 · Halloween Town", "Difficulty 6", "Lock/Shock/Barrel, Oogie Boogie ×2, Ansem's Report 7, Aero White-Mushroom master, Dream Shield. [11 treasures]")
step(p, "s9-oogie", "9.1 Oogie's Manor", "Halloween Town",
     "Jack joins. Torn Page in the lab. Lock/Shock/Barrel, then Oogie Boogie and his Manor.",
     [chk("s9-torn-page-4", "story", "Torn Page (Laboratory library)"),
      chk("s9-holy-circlet", "treasure", "Holy Circlet accessory (Oogie)"),
      chk("rep-7", "report", "Ansem's Report 7 (Oogie Boogie)"),
      chk("s9-pumpkinhead", "keyblade", "Pumpkinhead Keyblade (Oogie's Manor)")])
step(p, "s9-redtrinity", "9.x Red Trinity puppies", "Oogie's Manor",
     "Bring Donald+Goofy for the Red Trinity, then grab the guillotine-pit puppies.",
     [pups(40, "Oogie's Manor (Red Trinity arc + guillotine pit)")])
step(p, "s9-dreamshield", "9.x Dream Shield", "Traverse Town — Merlin's",
     "Last Pooh page available. If all 7 White-Mushroom masters are collected, Merlin gives the Dream Shield (Goofy).",
     [chk("s9-dream-shield", "treasure", "Dream Shield (all White-Mushroom masters)", "verify"),
      sweep("halloween", 11)])

# ======================================================================
# 10. NEVERLAND
# ======================================================================
p = phase("ch10", "10 · Neverland", "Difficulty 7", "Anti-Sora, Captain Hook, Glide, Report 9, Tinker Bell, Clock Tower opens, Hercules Cup → Yellow Trinity. [28 treasures]")
step(p, "s10-ship", "10.1 Captain Hook's ship", "The hold → deck → clock tower",
     "Anti-Sora, fix the clock, Hook. Glide + Tinker Bell + Fairy Harp + Report 9.",
     [pups(88, "Captain's room (green chest)"),
      pups(82, "The hold (fly to the roof beam)"),
      chk("rep-9", "report", "Ansem's Report 9 (Captain Hook)"),
      chk("s10-tinkerbell", "summon", "Tinker Bell summon"),
      chk("s10-fairy-harp", "keyblade", "Fairy Harp Keyblade"),
      chk("s10-glide", "ability", "Glide (group ability)")])
step(p, "s10-hercules", "10.x Hercules Cup → Yellow Trinity", "Olympus Coliseum",
     "Clear Pegasus then Hercules Cup (beat Hercules) to earn Olympia + the Yellow Trinity. Lock the Coliseum keyhole (Yellow Trinity by Phil).",
     [chk("s10-olympia", "keyblade", "Olympia Keyblade (Hercules Cup)"),
      chk("s10-yellow-trinity", "ability", "Yellow Trinity power"),
      chk("s10-herc-shield", "treasure", "Herc's Shield (Hercules Cup normal)")])
step(p, "s10-glide-sweep", "10.x Glide / Yellow-Trinity sweep", "Wonderland / Jungle / Halloween / Agrabah / Neverland / Traverse",
     "Use Glide + Yellow Trinity to mop up puppies and chests across worlds; the 81-puppy Dalmatians reward is Ultima-G.",
     [pups(19, "Wonderland tea garden (Glide)"),
      pups(70, "Halloween — above the laboratory (Glide)"),
      pups(64, "Halloween — pumpkin graveyard secret (Glide)"),
      pups(85, "Neverland hold secret room (Yellow Trinity)"),
      pups(1, "Traverse — behind Merlin's house (Glide)"),
      sweep("neverland", 28)])
step(p, "s10-clock", "10.x Clock Tower rewards", "Neverland — Clock Tower (world-select Option 3)",
     "Time-gated perma-boosts; the door matching your play-hour glows. See the Clock Tower checklist phase — keep checking it after every world.",
     [chk("s10-clock-started", "story", "Started collecting Clock Tower rewards")])

# ======================================================================
# 11. 100% MASTERY PART 1 — MOGURI CRAFT
# ======================================================================
p = phase("ch11", "11 · Mastery Pt 1 · Moguri Craft", "Mastery", "Farm every synthesis material BEFORE the next world floods old worlds with tougher mobs. Unlock Encounter Plus at 15 crafts.")
step(p, "s11-farm", "Material farming sweep", "All worlds (per the guide's checklist)",
     "Collect the full shard/stone/gem set the guide lists, then craft all available items once (16 crafts → Encounter Plus).",
     [chk("s11-materials", "story", "All Ch.11 synthesis materials farmed (shards/stones/gems)"),
      chk("s11-lucky-strike", "ability", "Lucky Strike on Sora/Donald/Goofy (rare-drop boost)"),
      chk("s11-encounter-plus", "ability", "Encounter Plus unlocked (15 crafts)")],
     missable=True,
     missableNote="The guide farms here because after Hollow Bastion, stronger Heartless mix into earlier worlds and make material farming far more tedious. Not blocked — just much faster now.")

# ======================================================================
# 12. HOLLOW BASTION PART 1
# ======================================================================
p = phase("ch12", "12 · Hollow Bastion Pt 1", "Difficulty 9", "Riku, Maleficent (+Dragon), Riku-Ansem, White Trinity, library puzzle, Report 5, Oathkeeper, Mushu. [35 treasures]")
step(p, "s12-fortress", "12.1 Into the fortress", "Entrance / Waterway / Library",
     "Crystal-lift puzzles + the library book puzzle. White Trinity from Riku; puppies along the way.",
     [pups(91, "Entrance ice platforms"),
      pups(97, "Library — Lift Stop (Gravira the platform)"),
      pups(94, "Outside area 16 (Gravira the caged chest)"),
      chk("s12-white-trinity", "ability", "White Trinity (Trinity Detect) — beat Riku"),
      chk("s12-ramuh-crystal", "story", "Turned the High-Tower red crystal blue (unlocks Ramuh Belt later)", "verify")],
     missableNote="Turn the High-Tower red crystal blue now, or you can't reach the Ramuh Belt in the library on the 2nd visit.")
step(p, "s12-bosses", "12.x Maleficent & Riku-Ansem", "Chapel / Grand Hall",
     "Maleficent → Dragon Maleficent (Fireglow → Mushu), Report 5, Riku-Ansem → Ragnarok.",
     [chk("rep-5", "report", "Ansem's Report 5 (Maleficent)"),
      chk("s12-fireglow", "summon", "Mushu summon (Fireglow gem)"),
      chk("s12-ragnarok", "ability", "Ragnarok ability (Riku-Ansem)")])
step(p, "s12-kairi", "12.x Traverse — Oathkeeper", "Traverse Town — Secret Waterway",
     "White Trinity Orichalcum, story scenes → Oathkeeper Keyblade, Lord Fortune for Donald.",
     [chk("s12-oathkeeper", "keyblade", "Oathkeeper Keyblade"),
      opt("fortress-weapons", "Farm the Fortress Heartless for Defender (Goofy, Atk +15) and Wizard's Relic (Donald, Atk +8/MP +2) — better than their ultimate weapons (0.2% drop, 0.5% w/ 3× Lucky Strike)"),
      opt("stealth-soldier", "Stealth Soldier (invisible; Stop it) drops Energy Stones — best farmed at the Grand Hall in Ch.14"),
      sweep("bastion1", 35)])

# ======================================================================
# 13. 100% MASTERY PART 2 — TRINITIES AROUND THE WORLD
# ======================================================================
p = phase("ch13", "13 · Mastery Pt 2 · World Trinities", "Mastery", "White-Trinity sweep across all worlds (now that you have it) + Lady Luck Keyblade. Last puppies hide here too.")
step(p, "s13-sweep", "White Trinity world sweep", "All worlds",
     "Hit every White Trinity for unique items/keyblades. See the Trinity checklist phase to tick each one.",
     [pups(67, "Halloween pumpkin graveyard (White Trinity)"),
      pups(43, "Neverland ship deck (White Trinity)"),
      chk("s13-lady-luck", "keyblade", "Lady Luck Keyblade (Wonderland White Trinity)")])

# ======================================================================
# 14. HOLLOW BASTION PART 2
# ======================================================================
p = phase("ch14", "14 · Hollow Bastion Pt 2", "Difficulty 9", "Behemoth, Divine Rose, last Dalmatians, Aerith's 4 Reports + Report 8 (Hades Cup), Shiva Belt. [9 treasures]")
step(p, "s14-return", "14.x Second descent", "Fortress / Grand Hall",
     "Trinity quest completes (all 46). Ramuh Belt, Divine Rose from Belle, last puppies, Behemoth → Omega Arts.",
     [pups(61, "Grand Hall (last triad — Glide to it)"),
      chk("s14-divine-rose", "keyblade", "Divine Rose Keyblade (Belle)"),
      chk("s14-oblivion", "keyblade", "Oblivion Keyblade (Grand Hall, Glide)"),
      chk("s14-omega-arts", "treasure", "Omega Arts accessory (Behemoth)"),
      chk("s14-all-puppies", "story", "All 99 Dalmatians freed (Full Gummi Set + Aeroga)")])
step(p, "s14-aerith", "14.x Aerith's reports", "Library",
     "Aerith hands over Reports 2, 4, 6, 10 and upgrades Cure→Curaga.",
     [chk("rep-2", "report", "Ansem's Report 2 (Aerith)"),
      chk("rep-4", "report", "Ansem's Report 4 (Aerith)"),
      chk("rep-6", "report", "Ansem's Report 6 (Aerith)"),
      chk("rep-10", "report", "Ansem's Report 10 (Aerith)")])
step(p, "s14-hades", "14.x Hades Cup", "Olympus Coliseum",
     "The Hades Cup (unlocks now). Match 10 Hades → Report 8 + Antimaga. Winning the cup = the Proud secret-ending requirement. Blizzaga torches → Shiva Belt.",
     [chk("rep-8", "report", "Ansem's Report 8 (Hades, Hades Cup match 10)"),
      chk("s14-hades-cup", "story", "Hades Cup cleared (Proud secret-ending requirement)"),
      chk("s14-shiva-belt", "treasure", "Shiva Belt (Blizzaga torches at Olympus)"),
      opt("hades-cup-gear", "Hades Cup challenge gear: Genju Shield (Atk +10, match 44), Save the Queen (Donald, Solo) & Save the King (Goofy, Atk +11/MP +2 — best shield, Time Trial)"),
      sweep("bastion2", 9)])

# ======================================================================
# 15. END OF THE WORLD PART 1
# ======================================================================
p = phase("ch15", "15 · End of the World Pt 1", "Difficulty 10", "Invisible labyrinth, Terminus linked-worlds, Chernabog, Superglide. STOP before the Final Rest door. [28 treasures]")
step(p, "s15-explore", "15.x Through End of the World", "Labyrinth / Terminus / Final Rest",
     "Behemoth gauntlets, the per-world gem chests, Mighty Shield, Chernabog → Superglide. Then the LAST farming spot (Gale / Stormy Stone / final White Mushroom).",
     [chk("s15-mighty-shield", "treasure", "Mighty Shield (Neverland door, Terminus)"),
      chk("s15-superglide", "ability", "Superglide (Chernabog)"),
      chk("s15-final-farm", "story", "Final-area materials farmed (Gale, Stormy Stone)"),
      sweep("eotw", 28)],
     missable=True,
     missableNote="⚠ POINT OF NO RETURN: opening the graceful door in Final Rest starts the unskippable endgame. Do ALL side quests (Ch.16) and a full Journal audit FIRST.")

# ======================================================================
# 16. 100% MASTERY PART 3 — SUPERBOSSES & FINAL SYNTHESIS  (Endgame tier)
# ======================================================================
p = phase("ch16", "16 · Mastery Pt 3 · Superbosses & Ultima", "★ Endgame", "The hardest content: all FM superbosses, Ultima Weapon synthesis (33/33), and the final Journal audit. This is real 100%.")
step(p, "s16-craft", "Craft everything (33/33)", "Traverse Town — Moguri shop",
     "Buy enough Orichalcum to finish, craft all 33 recipes including the EXP Bracelet, Fantasista, Seven Elements, and the Ultima Weapon.",
     [chk("s16-synth-33", "story", "All 33 synthesis recipes crafted"),
      chk("s16-ultima", "keyblade", "★ Ultima Weapon synthesized")])
step(p, "s16-superbosses", "The Final Mix superbosses", "Neverland / Deep Jungle / Agrabah / Hollow Bastion / Olympus",
     "Each is its own Journal entry — all required for true 100%.",
     [chk("boss-phantom", "boss", "★ Phantom (Neverland Clock Tower) → Stopga + Clock Tower reopens"),
      chk("boss-kurtzisa", "boss", "★ Kurt Zisa (Agrabah, talk to Carpet) → Report 11"),
      chk("rep-11", "report", "Ansem's Report 11 (Kurt Zisa)"),
      chk("boss-unknown", "boss", "★ Unknown / Xemnas (Hollow Bastion chapel) → Report 13"),
      chk("rep-13", "report", "Ansem's Report 13 (Unknown / Xemnas)"),
      chk("boss-icetitan", "boss", "★ Ice Titan (Olympus Gold Match)"),
      chk("boss-sephiroth", "boss", "★ Sephiroth (Olympus Platinum Match) → Report 12"),
      chk("rep-12", "report", "Ansem's Report 12 (Sephiroth)"),
      chk("boss-potscorpion", "boss", "Pot Scorpion (Agrabah Palace gates) — Mythril Stone farm")],
     missableNote="Phantom must be beaten to re-open the Neverland Clock Tower. Win the Hades Cup (Ch.14) for the Proud secret ending.")
step(p, "s16-audit", "Final Journal audit", "Menu → Jiminy's Journal",
     "Before the finale: 99 Dalmatians, 46 Trinities, 13 Reports, all postcards mailed, all Cups, 100 Acre Wood done, White Mushroom masters, Clock Tower rewards, Gummi blueprints, Synthesis 33/33, all summons. Confirm Journal reads 100%.",
     [chk("s16-audit-done", "story", "Jiminy's Journal confirmed at 100%")],
     missable=True,
     missableNote="Last checkpoint before the point of no return. Anything not done here is far harder (or impossible) to finish after the finale.")

# ======================================================================
# 17. END OF THE WORLD PART 2 — FINALE
# ======================================================================
p = phase("ch17", "17 · End of the World Pt 2", "Finale", "The final boss gauntlet and the secret movie.")
step(p, "s17-finale", "17.x The final door", "Final Rest → World of Chaos",
     "Ansem, Darkside, Ansem, then World of Chaos (7 rounds). Lock the final door. Watch the secret movie after the credits.",
     [chk("s17-finale-done", "story", "Beat the World of Chaos · KH locked"),
      chk("s17-secret-movie", "story", "★ Watched the secret movie (Proud / 100% Journal)")])

# ======================================================================
# REFERENCE CHECKLIST PHASES (aggregate Journal systems)
# ======================================================================

# --- Trinity Marks (46) ---
p = phase("ref-trinity", "✓ Trinity Marks (46)", "Checklist",
          "Every Trinity in the game, per cR0Ck's Trinity reference. Blue×17, Red×6, Green×9, Yellow×4, White×10. Many are story-required; tick each as you use it.")
TRIN = [
    # (color, count, [labels])
    ("Blue", 17, [
        "Traverse — Postcard #4 (District 1)", "Traverse — 60 Munny (near world exit)",
        "Traverse — Postcard #5 (near District 2)", "Traverse — Merlin's house (Camping set)",
        "Wonderland — Lotus Forest entrance", "Wonderland — Lotus Forest (pond area)",
        "Olympus — left of entrance (Mythril Shard)", "Olympus — right of entrance (Dalmatians 22–24)",
        "Deep Jungle — Camp (Dalmatians 34–36)", "Deep Jungle — Upper tree area",
        "Agrabah — Bazaar", "Agrabah — under the Bottomless Hall",
        "Monstro — Chamber 5", "Monstro — outside (2 Potions + Cottage)",
        "Monstro — The Throat", "Hollow Bastion — Waterway small room",
        "Hollow Bastion — Waterway Up"]),
    ("Red", 6, [
        "Traverse — District 1 alley (Dalmatians 4–6)", "Traverse — Secret Waterway (story)",
        "Traverse — above Gizmo building (bell)", "Agrabah — Cave Treasure Room",
        "Halloween — Oogie's Manor", "Hollow Bastion — Hall upper level (story)"]),
    ("Green", 9, [
        "Traverse — Accessories shop (opens Synthesis)", "Wonderland — Rabbit Hole (Elixir)",
        "Wonderland — Bizarre Room chimney (shrink)", "Olympus — near world exit (Mythril)",
        "Deep Jungle — above the Tunnel", "Agrabah — Storage room (AP+)",
        "Monstro — atop Geppetto's boat (High Jump)", "Neverland — pirate-flag room (story)",
        "Hollow Bastion — Library (yellow book, story)"]),
    ("Yellow", 4, [
        "Traverse — behind Merlin's house (AP+)", "Olympus — inside, by Phil (locks world)",
        "Agrabah — Cave Hall floor", "Neverland — hold secret room (Dalmatians 85–87 etc.)"]),
    ("White", 10, [
        "Traverse — Secret Waterway (Orichalcum)", "Wonderland — Scrambled-2 secret garden (Lady Luck)",
        "Olympus — center of plaza (Violetta)", "Deep Jungle — Cavern of Hearts (Orichalcum)",
        "Agrabah — first Cave room (Ifrit Belt)", "Monstro — Chamber 6 (Dark Matter)",
        "Halloween — pumpkin graveyard (Dalmatians 67–69)", "Atlantica — Triton's Palace (Orichalcum)",
        "Neverland — ship deck (Dalmatians 43–45)", "Hollow Bastion — icy entrance (Thundaga-G)"]),
]
for color, cnt, labels in TRIN:
    assert len(labels) == cnt, (color, len(labels))
    items = [chk(f"tri-{color.lower()}-{i+1}", "trinity", f"{color} Trinity — {lab}")
             for i, lab in enumerate(labels)]
    step(p, f"tri-{color.lower()}", f"{color} Trinity ({cnt})", "", "", items)

# --- Olympus Cups ---
p = phase("ref-cups", "✓ Olympus Cups", "Checklist",
          "Each cup has Normal / Sora-Alone / Time-Trial challenges. The Hades Cup win is the Proud secret-ending requirement; Gold/Platinum matches are the Ice Titan/Sephiroth superbosses (tracked in Ch.16).")
step(p, "cup-strategy", "How to win the cups (general)", "Olympus Coliseum", "Read before grinding cups.",
     [chk("cup-strategy-read", "story", "Read the general cup strategy")],
     tip=("There are NO heals between matches — what you bring is all you get. So: fill Sora's entire "
          "ITEM inventory with Ethers (Mega-Ethers for the Hades Cup), and put Thunder + Cure in "
          "quick-slots (Menu → Modify). Stand in the middle of a group and cast Thunder — but NOT when "
          "yellow Thunder-absorbing mages are present (kill those first). Equip your highest-Attack "
          "weapon and accessories. The Time-Trial challenge is the toughest of the three — that's where "
          "the Ethers really matter. Note: Combo Plus slows your chain (4 hits instead of 3), which "
          "hurts in Time-Trials — unequip it there."))
CUP_TIPS = {
    "phil": ("Matches 1–6 run with no heals between them. Match 7 is CLOUD — you do NOT need to win it "
             "(it's very hard) and losing costs nothing, so don't stress. Then Cerberus for the Hero License."),
    "pegasus": ("Match 9 is Yuffie + Squall. Kill YUFFIE first: deflect her shurikens — a return hit "
                "stuns her — then dodge Squall's jump and combo him. Cast Aero on Sora when fighting solo."),
    "hercules": ("You fight HERCULES solo in every challenge. While he glows with a yellow aura he's "
                 "invincible — pick up a barrel and THROW it at him to break the aura, then attack. "
                 "Don't try to hit him while he's spinning."),
    "hades": ("Match 10 is HADES: when he stands center and spins a ring of fire, follow him and rotate "
              "WITH him staying very close — do NOT jump (jumping gets you killed). The match-1 finale is "
              "Rock Titan: hit his legs to topple him, then jump up and hit his faces. Winning the Hades "
              "Cup is the Proud secret-ending requirement."),
}
for cup, unlock in [("Phil Cup", "after Deep Jungle"), ("Pegasus Cup", "after Monstro"),
                    ("Hercules Cup", "after Neverland"), ("Hades Cup", "after Hollow Bastion Pt 2")]:
    cid = cup.split()[0].lower()
    step(p, f"cup-{cid}", f"{cup} ({unlock})", "", "",
         [chk(f"cup-{cid}-normal", "cup", f"{cup} — Normal"),
          chk(f"cup-{cid}-solo", "cup", f"{cup} — Sora Alone"),
          chk(f"cup-{cid}-time", "cup", f"{cup} — Time Trial")],
         tip=CUP_TIPS[cid])

# --- 100 Acre Wood ---
p = phase("ref-pooh", "✓ 100 Acre Wood", "Checklist",
          "Restore 5 torn pages (found across worlds) and clear each minigame's score goal; finish for the EXP Ring and the final Cheer reward.")
step(p, "pooh-pages", "5 Torn Pages restored", "", "Pages: Agrabah, Monstro, Traverse (51 puppies), Atlantica, Halloween.",
     [chk("pooh-page-agrabah", "pooh", "Page 1 — Agrabah (Dark Chamber)"),
      chk("pooh-page-monstro", "pooh", "Page 2 — Monstro (Chamber 6)"),
      chk("pooh-page-traverse", "pooh", "Page 3 — Traverse (51 Dalmatians)"),
      chk("pooh-page-atlantica", "pooh", "Page 4 — Atlantica (Ariel's room)"),
      chk("pooh-page-halloween", "pooh", "Page 5 — Halloween (Laboratory)")])
step(p, "pooh-games", "Minigames cleared", "", "Hit each score goal for the page reward.",
     [chk("pooh-mg-bees", "pooh", "Bee-jump (Pooh) — 100+ pts"),
      chk("pooh-mg-carrots", "pooh", "Defend carrots (Tigger) — 150+ pts"),
      chk("pooh-mg-swing", "pooh", "Owl swing — 40+ m"),
      chk("pooh-mg-baseball", "pooh", "Roo baseball — 20 pts < 30s + all 5 Rare Nuts"),
      chk("pooh-mg-hide", "pooh", "Find-them-all (night) < 5 min"),
      chk("pooh-final", "pooh", "Firewood + all minigames → Cheer (Owl)")])

# --- White Mushrooms / special Heartless ---
p = phase("ref-mushroom", "✓ Mushrooms & rare Heartless", "Checklist",
          "Master each magic on a White Mushroom (→ Dream Shield), and the bounce/secret-Heartless extras the Journal tracks.")
step(p, "mush-masters", "White Mushroom — 7 magic masters", "", "Cast the matching spell 3× by location.",
     [chk("mush-fire", "mushroom", "Master of Fire (Wonderland Lotus Forest)"),
      chk("mush-blizzard", "mushroom", "Master of Blizzard (Wonderland)"),
      chk("mush-thunder", "mushroom", "Master of Thunder (Wonderland)"),
      chk("mush-cure", "mushroom", "Master of Cure (Deep Jungle camp)"),
      chk("mush-gravity", "mushroom", "Master of Gravity (Agrabah Treasure Room)"),
      chk("mush-stop", "mushroom", "Master of Stop (Atlantica, inside the ship)"),
      chk("mush-aero", "mushroom", "Master of Aero (Halloween graveyard)")])
step(p, "mush-extra", "Bounce & rare-Heartless extras", "", "Optional Journal flavour + farm bosses.",
     [chk("mush-truffle-50", "mushroom", "Rare Truffle — 50 bounces (Shiitake rank)"),
      chk("mush-truffle-100", "mushroom", "Rare Truffle — 100 bounces (Matsutake rank)"),
      chk("mush-agaricus", "mushroom", "Pink Agaricus farmed (Serenity Power)")])

# --- Clock Tower ---
p = phase("ref-clock", "✓ Neverland Clock Tower (12)", "Checklist",
          "Open the door matching your in-game play-hour for a reward; one per hour 1–12. Locks while you're between Ch.11 and beating Phantom — keep coming back.")
clock_rewards = {1:"Orichalcum",2:"Power Up",3:"Mythril Shard",4:"Power Up",5:"AP Up",6:"Mythril",
                 7:"AP Up",8:"Defense Up",9:"Orichalcum",10:"Defense Up",11:"Mythril Shard",12:"Megalixir"}
step(p, "clock-doors", "12 time-gated doors", "Neverland — Clock Tower (Option 3)", "",
     [chk(f"clock-{h}", "clock", f"{h}:00 door — {clock_rewards[h]}") for h in range(1,13)])

# --- Gummi blueprints ---
p = phase("ref-gummi", "✓ Gummi Blueprints (Geppetto)", "Checklist",
          "Geppetto rewards blueprints by total Heartless defeated. Enter his house 30× then talk to Pinocchio for Chocobo.")
gummi = [("Geppetto","1st visit"),("Chocobo","enter house 30×"),("Cid","500+ kills"),
         ("Cactuar","1000+ kills"),("Yuffie","1500+ kills"),("Aerith","3000+ kills"),
         ("Leon","4000+ kills"),("Hyperion","5000+ kills")]
step(p, "gummi-list", "8 ship blueprints", "Traverse Town — Geppetto's house", "",
     [chk(f"gummi-{name.lower()}", "gummi", f"{name} blueprint ({cond})") for name, cond in gummi])

# --- Synthesis milestones ---
p = phase("ref-synth", "✓ Synthesis (Moguri)", "Checklist",
          "Craft each recipe once; tiers unlock in groups. 15 crafts → Encounter Plus, 30 → final tier, 33 → Ultima Weapon. (Items also itemized in Ch.11/16.)")
step(p, "synth-milestones", "Crafting milestones", "Traverse Town — Moguri shop", "",
     [chk("synth-open", "synth", "Synthesis unlocked (Green Trinity)"),
      chk("synth-15", "synth", "15 recipes crafted → Encounter Plus"),
      chk("synth-30", "synth", "30 recipes crafted → final tier unlocks"),
      chk("synth-33", "synth", "33 recipes crafted → Ultima Weapon available")])

# --- Optional boosts & leveling ---
p = phase("ref-optional", "✓ Optional boosts & leveling", "Checklist",
          "Not required for 100%, but strong quality-of-life: free/efficient EXP, EXP-boosting gear, money/heal tricks, and the best optional weapons to chase. Each is also flagged in-route where it first applies.")
step(p, "opt-exp", "Free & efficient EXP", "", "",
     [opt("dream-exp-ref", "Destiny Islands sparring (Ch.1) — free permanent EXP to ~Lv6 before you ever leave"),
      opt("exp-gear", "Equip EXP gear while grinding: EXP Ring (100 Acre Wood), EXP Bracelet (synthesis), EXP Necklace (Unknown/Xemnas)"),
      opt("level-hades", "Level 1→100: chill repeats of the Hades Cup"),
      opt("level-rock-titan", "Rock Titan = ~8000 EXP per kill"),
      opt("level-ice-titan", "Ice Titan + Tech Boost ability = 125 EXP per deflected stalactite")])
step(p, "opt-econ", "Money & healing tricks", "", "",
     [opt("megapotion-loop-ref", "Wonderland flower loop → endless cheap Mega-Potions"),
      opt("bambi-synth", "Summon Bambi to rain HP + synthesis items (drops vary by world)"),
      opt("black-mushroom", "Black/Gravity-weak mobs drop sellable items for easy Munny")])
step(p, "opt-gear", "Best optional weapons & accessories", "", "",
     [opt("defender-shield", "Defender (Goofy, Atk +15) — Hollow Bastion Heartless"),
      opt("wizards-relic", "Wizard's Relic (Donald, Atk +8/MP +2) — Hollow Bastion Heartless"),
      opt("save-the-king-queen", "Save the King (Goofy) + Save the Queen (Donald) — Hades Cup challenges"),
      opt("genji-shield", "Genju Shield (Atk +10) — Hades Cup match 44"),
      opt("titan-chains", "Craft 3× Titan Chain (Atk +4/Def +2 each) for the Sephiroth fight")])

# ======================================================================
# CATEGORIES + META
# ======================================================================
CATEGORIES = {
    "treasure": {"icon": "🎁", "label": "Treasure sweeps"},
    "puppy":    {"icon": "🐕", "label": "Dalmatians"},
    "trinity":  {"icon": "🔱", "label": "Trinities"},
    "report":   {"icon": "📕", "label": "Ansem's Reports"},
    "postcard": {"icon": "✉️", "label": "Postcards"},
    "cup":      {"icon": "🏆", "label": "Olympus Cups"},
    "pooh":     {"icon": "🍯", "label": "100 Acre Wood"},
    "mushroom": {"icon": "🍄", "label": "Mushrooms"},
    "clock":    {"icon": "🕛", "label": "Clock Tower"},
    "gummi":    {"icon": "🚀", "label": "Gummi blueprints"},
    "synth":    {"icon": "🔨", "label": "Synthesis"},
    "summon":   {"icon": "✨", "label": "Summons"},
    "optional": {"icon": "💪", "label": "Optional boosts"},
    "boss":     {"icon": "💀", "label": "Superbosses"},
    "keyblade": {"icon": "🗝", "label": "Keyblades"},
    "ability":  {"icon": "⚡", "label": "Abilities & magic"},
    "story":    {"icon": "📖", "label": "Story / milestones"},
    "misc":     {"icon": "•",  "label": "misc"},
}

META = {
    "game": "Kingdom Hearts Final Mix (KH1) — Switch 2",
    "subtitle": "First-playthrough · 100% Jiminy's Journal in one route · Proud",
    "version": "0.1.0",
    "difficulty": "Proud",
    "scope": ("Mirrors cR0Ck's spoiler-free GameFAQs '100% Story' walkthrough (KH HD I.5+II.5 "
              "ReMIX, v4) chapter-for-chapter: 17 story chapters plus checklist phases for the "
              "aggregate Journal systems. Targets full Journal 100% on Proud — 99 Dalmatians, "
              "46 Trinities, 13 Ansem's Reports, all postcards, Olympus Cups, 100 Acre Wood, "
              "White Mushroom masters, Clock Tower, Gummi blueprints, Synthesis (incl. Ultima "
              "Weapon), and every Final Mix superboss."),
    "secretEnding": ("Proud: win the Hades Cup. Standard: free all 99 Dalmatians AND complete the "
                     "whole Journal (incl. all Trinities/minigames). Beginner: secret ending is "
                     "impossible. This tracker targets Proud."),
    "confidencePolicy": ("Route order, collectible placement and missable callouts follow cR0Ck's "
                         "walkthrough. The in-game Jiminy's Journal % is the ultimate source of "
                         "truth — trust it over any wording here."),
    "remakeNote": ("Built pre-release on the HD Final Mix (1.5) baseline. Patch in any Switch 2 "
                   "remaster changes on launch night — all data lives in this one JSON file."),
}

route = {"meta": META, "categories": CATEGORIES, "phases": PHASES}

# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------
def validate(route):
    errs = []
    ids = {}
    cat_counts = {}
    for ph in route["phases"]:
        for st in ph["steps"]:
            for it in st["items"]:
                iid = it["id"]
                if iid in ids:
                    errs.append(f"duplicate id: {iid} (also in {ids[iid]})")
                ids[iid] = ph["id"]
                if it["cat"] not in route["categories"]:
                    errs.append(f"unknown category '{it['cat']}' on {iid}")
                cat_counts[it["cat"]] = cat_counts.get(it["cat"], 0) + 1

    # puppies: 33 triads -> 99
    pup_ids = sorted(int(i.split("-")[1]) for i in ids if i.startswith("pup-"))
    if pup_ids != list(range(1, 99, 3)):
        errs.append(f"puppy triads wrong: got {pup_ids}")
    # reports 1..13 each once
    reps = sorted(int(i.split("-")[1]) for i in ids if re.fullmatch(r"rep-\d+", i))
    if reps != list(range(1, 14)):
        errs.append(f"reports wrong: got {reps}")
    # trinities 46
    if cat_counts.get("trinity", 0) != 46:
        errs.append(f"trinity count != 46: {cat_counts.get('trinity')}")
    # clock 12
    clock = sum(1 for i in ids if re.fullmatch(r"clock-\d+", i))
    if clock != 12:
        errs.append(f"clock doors != 12: {clock}")
    # postcards 9
    pc = sum(1 for i in ids if re.fullmatch(r"pc-\d+", i))
    if pc != 9:
        errs.append(f"postcards != 9: {pc}")
    return errs, cat_counts, len(ids)

errs, cat_counts, total = validate(route)
out = os.path.join(os.path.dirname(__file__), "public", "data", "route.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(route, f, ensure_ascii=False, indent=1)

print(f"phases: {len(PHASES)}  items: {total}")
print("category counts:", {k: cat_counts.get(k, 0) for k in CATEGORIES})
print(f"puppies(/99): {sum(1 for ph in PHASES for st in ph['steps'] for it in st['items'] if it['cat']=='puppy')*3}")
if errs:
    print("\nVALIDATION ERRORS:")
    for e in errs:
        print("  -", e)
    sys.exit(1)
print("\nOK — wrote", out)
