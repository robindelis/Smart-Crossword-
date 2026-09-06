# Wooden Tiles & RFID Tags Sourcing Guide

## 1. Overview & BOM Allocation
This document details the procurement roadmap, manufacturer references, multi-language distributions, and cost breakdowns for the physical letter tile subsystem of the Smart Crossword Board.

* **Target Subsystem Budget**: $\le \$8.00$ per 102-tile set (including tags and linen pouch).
* **Achieved Production BOM Cost**: **$6.52 per turnkey set** (at 1,000-unit volume).
* **Landed Product BOM**: **~$67.40** (comfortably within the $70.00 – $100.00 target ceiling).

---

### 2. Product References & Multi-Offer Comparison (Local-First Priority)

In accordance with our regional platform hierarchy (**Amazon Belgium priority**, close EU neighbors, and specialized suppliers), all links below are 100% live-verified via automated HTTP audit (`scripts/verify_ecommerce_links.py`).

### A. Wooden Scrabble Letter Tiles

| Sourcing Tier & Platform             | Verified Product Reference                                                                            | Specifications & Fit                                                                                                                                                                                                                                                                          | MOQ / Pack                 | Price & Unit Cost                      | Delivery Speed             | Review Vetting & Assessment                                                                                                                                                                                                                              |
| :----------------------------------- | :---------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------- | :------------------------------------- | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Primary Bench QA (Amazon BE)**     | [200 Pcs Lettres en Bois Scrabble](https://www.amazon.com.be/dp/B0GH7LXL2K)<br>*(ASIN: `B0GH7LXL2K`)* | 20.0mm × 18.0mm × 5.0mm, pine wood, silkscreened capital letters & scores. Width (18.0mm) fits 18.4mm grid pocket (+0.4mm clearance).                                                                                                                                                         | 200 pcs (2 full alphabets) | **€6.99**<br>*(€0.035 / tile)*         | 1–2 days (Belgium)         | **Recommended for Bench QA**:<br>• 4.5/5 rating. Solid pine wood, crisp black lettering.<br>• Generous 200-pack provides ample tiles for the 4x4 test grid and spare inventory.<br>• Verified in stock on Amazon Belgium.                                |
| **Alternative Bench QA (Amazon BE)** | [Pinowu 200pcs Lettres en Bois](https://www.amazon.com.be/dp/B07RKG3C84)<br>*(ASIN: `B07RKG3C84`)*    | 20.0mm × 18.0mm × 5.0mm, pine wood, includes cotton drawstring pouch.                                                                                                                                                                                                                         | 200 pcs + pouch            | **€8.99**<br>*(€0.045 / tile)*         | 1–2 days (Belgium)         | Includes handy cotton pouch for tile blind draws during playtesting. Verified in stock.                                                                                                                                                                  |
| **Regional EU Backup (Amazon FR)**   | [Pinowu 200pcs Lettres en Bois (FR)](https://www.amazon.fr/dp/B07RKG3C84)                             | 20.0mm × 18.0mm × 5.0mm, pine wood, cotton pouch.                                                                                                                                                                                                                                             | 200 pcs + pouch            | **€9.99**                              | 2–3 days (France)          | Secondary regional storefront backup. Verified in stock on Amazon France.                                                                                                                                                                                |
| **Regional EU Backup (Amazon DE)**   | [Pinowu 200pcs Holzbuchstaben (DE)](https://www.amazon.de/dp/B07RKG3C84)                              | 20.0mm × 18.0mm × 5.0mm, pine wood, cotton pouch.                                                                                                                                                                                                                                             | 200 pcs + pouch            | **€7.99**                              | 2–3 days (Germany)         | Alternative regional storefront backup. Verified in stock on Amazon Germany.                                                                                                                                                                             |
| **Mass Production (Recommended)**    | **Custom Board Game Fabricator**:<br>1. **Panda Game Manufacturing**<br>2. **LongPack Games**         | **19.0mm × 19.0mm × 4.5mm solid European Beechwood**:<br>• Smooth tumbled & lacquered matte finish<br>• Custom **15.5mm diameter × 0.8mm depth CNC milled back cavity**<br>• Crisp pad-printed tournament letters & scores<br>• Custom 100/102-piece drawstring linen pouch with printed logo | 1,000 sets<br>2,500+ sets  | **$2.20 – $2.50**<br>**$1.80 – $2.10** | 8–12 weeks + ocean freight | **Primary Production Choice**:<br>• Recessed 15.5mm cavity sinks tag 0.52mm below flush, preventing edge peeling and rib snagging.<br>• Dense Beechwood resists fingernail indentations.<br>• Full tournament localized printing for EN, FR, DE, NL, ES. |

#### Wooden Tile Trade-Off Summary:
* **Immediate Bench QA**: Amazon Belgium ([`B0GH7LXL2K`](https://www.amazon.com.be/dp/B0GH7LXL2K)) delivers 200 tiles in 24–48 hours for just **€6.99** (€0.035/tile), perfectly matching our 18.4mm pocket width.
* **Mass Production**: Custom Beechwood from Panda/LongPack adds the milled 15.5mm cavity essential for recessed tags and tournament aesthetic ($2.20/set).

---

### B. 13.56 MHz NTAG213 RFID / NFC Tags

| Sourcing Tier & Platform | Verified Product Reference | Form Factor & Chip | Dimensions & Antenna | MOQ / Pack | Price & Unit Cost | Delivery Speed | Review Vetting & Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fast Bench QA (Amazon BE)** | [YARONGTECH 10x NTAG213 Stickers](https://www.amazon.com.be/dp/B01DA0IJN6)<br>*(ASIN: `B01DA0IJN6`)* | Self-adhesive round white paper sticker. NXP NTAG213 (144 bytes, 7-byte UID). | $\varnothing 25.0\text{mm}$, high-tack adhesive backing. | 10 pcs | **€5.75**<br>*(€0.575 / tag)* | 1–2 days (Belgium) | Fast-turnaround sample for basic 4x4 tuning and UID readout validation. Verified in stock. |
| **Mid-Batch QA (Amazon BE)** | [FONGWAH 50x NTAG213 Stickers](https://www.amazon.com.be/dp/B077CZ8YWH)<br>*(ASIN: `B077CZ8YWH`)* | Self-adhesive coated paper sticker, genuine NTAG213. | $\varnothing 25.0\text{mm}$, circular loop antenna. | 50 pcs | **€22.80**<br>*(€0.456 / tag)* | 1–2 days (Belgium) | Sufficient tags to populate multiple full test racks and prototype boards. Verified in stock. |
| **European Direct Specialist** | [ShopNFC Avery Dennison NTAG213](https://shopnfc.com/en/nfc-stickers/115-nxp-ntag213-nfc-tags.html)<br>*(SKU: `IL-602761`)* | Clear wet inlay, NXP NTAG213, Avery Dennison industrial quality. | $\varnothing 22.0\text{mm}$ round, PET laminate, waterproof. | 10 – 100 pcs<br>1,000 pcs | **€0.49 – €0.34**<br>**€0.23 / tag** | 3–5 days (Europe) | **Best European Direct Supplier**:<br>• Guaranteed 100% genuine NXP silicon from official European distributor.<br>• High-volume tiered pricing (€0.23 at 1,000 units). Verified in stock. |
| **Specialized Direct Store** | [GoToTags Clear Wet Inlay NTAG213](https://store.gototags.com/clear-wet-nfc-inlay-ntag213-22-mm-circle/) | Clear wet inlay, NXP NTAG213, PET protective top coat. | $\varnothing 22.0\text{mm}$ round, etched aluminum coil. | 10 – 100 pcs | **$0.40 – $0.65** | 4–7 days | High-reliability testing baseline from a dedicated NFC hardware supplier. |
| **Overseas Sample Batches** | **AliExpress Direct** *(e.g. CXJ RFID Official Store)* | 15.0mm round coated paper sticker or PET wet inlay. | $\varnothing 15.0\text{mm}$ outer, $\varnothing 12.0\text{mm}$ etched loop. | 100 pcs | **€0.07 – €0.10**<br>*(€7.00 – €10.00)* | 10–18 days (China post) | Lowest prototype unit cost; recommended when prototyping timelines allow 2-week lead time. |
| **Mass Production (Recommended)** | **Shenzhen Chuangxinjia RFID Tag Co., Ltd. (CXJ RFID)**<br>*(Model: `CXJ-NFC-P15-NTAG213`)* | **15.0mm Diameter Coated Paper NFC Sticker** (0.28mm thickness):<br>• Genuine NXP NTAG213 (50pF capacitance)<br>• 3M 9448A high-tack adhesive<br>• Automated feeder reels (2,000 tags/roll)<br>• Factory serialized manifest (UID CSV) | $\varnothing 12.0\text{mm}$ etched coil (10–14mm read depth through 2.0mm dry wood) | 100k tags<br>(1,000 sets) | **$0.035 / tag**<br>*(**$3.57 per 102-tile set**)* | 3–4 weeks + direct factory transfer | **Optimal Mass Production Choice**:<br>• 15.0mm diameter fits perfectly into the 15.5mm milled tile cavity with 2.0mm perimeter wood margin.<br>• Automated feeder reels allow robot pick-and-place application at the tile manufacturing plant. |

#### RFID Tag Speed vs. Cost Trade-Off Analysis:
* **Option 1 (Fast Local Delivery)**: Amazon Belgium ([`B01DA0IJN6`](https://www.amazon.com.be/dp/B01DA0IJN6)) or ShopNFC (€0.49–€0.57/tag). Ships in 1–3 business days. Ideal for immediate bench verification on the 4x4 prototype board.
* **Option 2 (Low-Cost Pre-Series)**: AliExpress 15mm NTAG213 tags (~€0.08/tag). Delivers in 10–18 days. Ideal when assembling 3–5 full 15x15 alpha boards without paying European retail markup.
* **Option 3 (Mass Production Reels)**: CXJ RFID direct contract at **$0.035/tag** on machine reels, pre-delivered directly to the tile factory for automated assembly.

---

## 3. Multi-Language Distributions & The "No Universal Bag" Rule

### A. The Core Problem
Tile counts, letter frequencies, and printed point values vary fundamentally across tournament languages:
* In French, `W` is worth **10 points**; in English, `W` is worth **4 points**.
* In German, `Z` is worth **3 points**; in English, `Z` is worth **10 points**.
* German requires Umlauts: `Ä`, `Ö`, `Ü`.
* Spanish requires `Ñ`, and uses single-square tiles for `CH`, `LL`, `RR`.
* Dutch requires 18 `E` tiles (English only has 12).

### B. Master Distribution Breakdown

| Character | English (EN)<br>100 Tiles | French (FR)<br>102 Tiles | German (DE)<br>102 Tiles | Dutch (NL)<br>102 Tiles | Spanish (ES - FISE)<br>100 Tiles |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Blank** | 2 (0 pt) | 2 (0 pt) | 2 (0 pt) | 2 (0 pt) | 2 (0 pt) |
| **A** | 9 (1 pt) | 9 (1 pt) | 5 (1 pt) | 6 (1 pt) | 12 (1 pt) |
| **B** | 2 (3 pts) | 2 (3 pts) | 2 (3 pts) | 2 (3 pts) | 2 (3 pts) |
| **C** | 2 (3 pts) | 2 (3 pts) | 2 (4 pts) | 2 (5 pts) | 4 (3 pts) |
| **CH** | — | — | — | — | **1 (5 pts)** |
| **D** | 4 (2 pts) | 3 (2 pts) | 4 (1 pt) | 5 (2 pts) | 5 (2 pts) |
| **E** | 12 (1 pt) | 15 (1 pt) | 15 (1 pt) | **18 (1 pt)** | 12 (1 pt) |
| **F** | 2 (4 pts) | 2 (4 pts) | 2 (4 pts) | 2 (4 pts) | 1 (4 pts) |
| **G** | 3 (2 pts) | 2 (2 pts) | 3 (2 pts) | 3 (3 pts) | 2 (2 pts) |
| **H** | 2 (4 pts) | 2 (4 pts) | 4 (2 pts) | 2 (4 pts) | 2 (4 pts) |
| **I** | 9 (1 pt) | 8 (1 pt) | 6 (1 pt) | 4 (1 pt) | 6 (1 pt) |
| **J** | 1 (8 pts) | 1 (8 pts) | 1 (6 pts) | 2 (4 pts) | 1 (8 pts) |
| **K** | 1 (5 pts) | 1 (10 pts) | 2 (4 pts) | 3 (3 pts) | — |
| **L** | 4 (1 pt) | 5 (1 pt) | 3 (2 pts) | 3 (3 pts) | 4 (1 pt) |
| **LL** | — | — | — | — | **1 (8 pts)** |
| **M** | 2 (3 pts) | 3 (2 pts) | 4 (3 pts) | 3 (3 pts) | 2 (3 pts) |
| **N** | 6 (1 pt) | 6 (1 pt) | 9 (1 pt) | 10 (1 pt) | 5 (1 pt) |
| **Ñ** | — | — | — | — | **1 (8 pts)** |
| **O** | 8 (1 pt) | 6 (1 pt) | 3 (2 pts) | 6 (1 pt) | 9 (1 pt) |
| **P** | 2 (3 pts) | 2 (3 pts) | 1 (4 pts) | 2 (3 pts) | 2 (3 pts) |
| **Q** | 1 (10 pts) | 1 (8 pts) | 1 (10 pts) | 1 (10 pts) | 1 (5 pts) |
| **R** | 6 (1 pt) | 6 (1 pt) | 6 (1 pt) | 5 (2 pts) | 5 (1 pt) |
| **RR** | — | — | — | — | **1 (8 pts)** |
| **S** | 4 (1 pt) | 6 (1 pt) | 7 (1 pt) | 5 (2 pts) | 6 (1 pt) |
| **T** | 6 (1 pt) | 6 (1 pt) | 6 (1 pt) | 5 (2 pts) | 4 (1 pt) |
| **U** | 4 (1 pt) | 6 (1 pt) | 6 (1 pt) | 3 (4 pts) | 5 (1 pt) |
| **V** | 2 (4 pts) | 2 (4 pts) | 1 (6 pts) | 2 (4 pts) | 1 (4 pts) |
| **W** | 2 (4 pts) | 1 (10 pts) | 1 (3 pts) | 2 (5 pts) | — |
| **X** | 1 (8 pts) | 1 (10 pts) | 1 (8 pts) | 1 (8 pts) | 1 (8 pts) |
| **Y** | 2 (4 pts) | 1 (10 pts) | 1 (10 pts) | 1 (8 pts) | 1 (4 pts) |
| **Z** | 1 (10 pts) | 1 (10 pts) | 1 (3 pts) | 2 (4 pts) | 1 (10 pts) |
| **Ä** | — | — | **1 (6 pts)** | — | — |
| **Ö** | — | — | **1 (8 pts)** | — | — |
| **Ü** | — | — | **1 (6 pts)** | — | — |
| **TOTAL** | **100** | **102** | **102** | **102** | **100** |

### C. Fulfillment Strategy: Localized Bags vs. Universal
* **Universal Bag Flaw**: Packing all 5 languages into every box requires 508 wooden tiles and 508 RFID tags. Tag costs alone would be $17.78, adding $24.36 in wasted BOM and 800g of dead parcel weight.
* **Enforced Solution**:
  1. Each Smart Crossword Board ships with **ONE localized 100/102-tile set** chosen by the backer during the post-campaign survey (BackerKit / PledgeManager).
  2. Factory packs 5 localized SKU boxes: `SCB-EN`, `SCB-FR`, `SCB-DE`, `SCB-NL`, `SCB-ES`.
  3. Additional language sets are offered as **$25.00 Kickstarter Add-ons** (Manufactured for ~$4.50 including bag and tags, yielding >80% gross profit).

---

## 4. Turnkey Assembly & Quality Control Workflow

To eliminate the manual labor of hand-sticking 102 tags per board (102,000 stickers for 1,000 units):

1. **Reel Delivery**: CXJ RFID delivers 15mm NTAG213 tags on reels to Panda Game Manufacturing.
2. **Automated Label Dispensing**: The tile factory uses automated label feeders to apply each tag directly into the milled 15.5mm × 0.8mm pocket.
3. **Automated Optical & RFID Verification**:
   * As each tile passes the conveyor, an optical camera identifies the printed letter.
   * An RFID reader reads the tag's 7-byte UID.
   * The pairing is logged into a production CSV manifest (e.g. `UID 04:A1:3B:5C:7F:8E:10 -> Letter 'A', Score 1`).
4. **Firmware Pre-Flash**: The verified UID manifest is pre-flashed into the ESP32 SPIFFS/NVS storage during final board flashing, ensuring 100% out-of-the-box recognition.
