const fs = require("fs");
const path = require("path");
const Module = require("module");

// Load and compile DataLoom internal generator from plugin source
const pluginCode = fs.readFileSync(
  path.join(__dirname, "../.obsidian/plugins/obisidian-dataloom/main.js"),
  "utf8"
);

const modCode = pluginCode + `
module.exports.__internal = {
  createGenericLoomState,
  createColumn,
  createRow,
  createTextCell,
  createNumberCell,
  createEmbedCell,
  createFileCell,
  serializeState,
  deserializeState
};
`;

const originalRequire = Module.prototype.require;
Module.prototype.require = function (reqPath) {
  if (reqPath === "obsidian") {
    class MockView {}
    return {
      Modal: class {},
      setIcon: () => {},
      PluginSettingTab: class {},
      Setting: class {
        setName() { return this; }
        setDesc() { return this; }
        addToggle() { return this; }
        addText() { return this; }
        addDropdown() { return this; }
      },
      Notice: class {},
      TFile: class {},
      TextFileView: MockView,
      MarkdownView: MockView,
      MarkdownRenderer: class {},
      Platform: { isDesktop: true },
      normalizePath: (p) => p,
      Plugin: class {},
      TFolder: class {},
      addIcon: () => {},
    };
  }
  if (reqPath.startsWith("@codemirror/")) {
    return {
      ViewPlugin: { fromClass: () => {} },
      EditorView: class {},
    };
  }
  return originalRequire.apply(this, arguments);
};

const m = new Module("dataloom-runtime", module);
m.filename = path.join(__dirname, "../.obsidian/plugins/obisidian-dataloom/main.js");
m.paths = Module._nodeModulePaths(path.join(__dirname, "../.obsidian/plugins/obisidian-dataloom"));
m._compile(modCode, m.filename);

const {
  createGenericLoomState,
  createColumn,
  createRow,
  createTextCell,
  createNumberCell,
  serializeState,
  deserializeState
} = m.exports.__internal;

function buildPrototypeLoom() {
  const colItem = createColumn({ content: "Item / Component", type: "text" });
  colItem.width = "220px";

  const colDetails = createColumn({ content: "Top Pick & Pack Details", type: "text" });
  colDetails.width = "270px";

  const colAllocated = createColumn({ content: "Bench Cost (€)", type: "number" });
  colAllocated.width = "130px";
  colAllocated.numberFormat = "currency";
  colAllocated.currencyType = "EUR";
  colAllocated.calculationType = "sum";

  const colPackPrice = createColumn({ content: "Pack Price (€)", type: "number" });
  colPackPrice.width = "130px";
  colPackPrice.numberFormat = "currency";
  colPackPrice.currencyType = "EUR";
  colPackPrice.calculationType = "sum";

  const colLink = createColumn({ content: "Purchase Link", type: "text" });
  colLink.width = "340px";

  const colNotes = createColumn({ content: "Notes & CAD Specs", type: "text" });
  colNotes.width = "260px";

  const columns = [colItem, colDetails, colAllocated, colPackPrice, colLink, colNotes];

  const rawData = [
    {
      item: "Wood Letter Tiles",
      details: "200 Pcs Scrabble Wooden Tiles (16 needed)",
      cost: 6.99,
      pack: 6.99,
      link: "https://www.amazon.com.be/dp/B0GH7LXL2K",
      notes: "19x19x4.8mm pine/beechwood; fits 19mm CAD pockets"
    },
    {
      item: "13.56 MHz NFC Tags",
      details: "60 Pcs NTAG213 Stickers 25mm (16 needed)",
      cost: 6.99,
      pack: 6.99,
      link: "https://www.amazon.com.be/dp/B0HC2ZKQLQ",
      notes: "144 bytes, ISO14443A, fast read with PN532"
    },
    {
      item: "NFC Reader Module",
      details: "PN532 V3 RFID/NFC Breakout Kit (1 board)",
      cost: 8.98,
      pack: 8.98,
      link: "https://www.amazon.com.be/dp/B0C9DTJMLQ",
      notes: "SPI/I2C switches + level shifters; includes test cards"
    },
    {
      item: "Host Microcontroller",
      details: "diymore ESP32-S3 DevKit N16R8 3-Pack (1 used)",
      cost: 6.99,
      pack: 20.98,
      link: "https://www.amazon.com.be/dp/B0GXF14RRM",
      notes: "16MB Flash + 8MB PSRAM; holds Trie dictionary in RAM"
    },
    {
      item: "16-Ch Multiplexer",
      details: "DollaTek CD74HC4067 Breakout 5-Pack (1 used)",
      cost: 1.20,
      pack: 5.99,
      link: "https://www.amazon.com.be/dp/B07PPKRVGW",
      notes: ">60 MHz analog bandwidth, standard 0.1 inch DIP pins"
    },
    {
      item: "Rotating Turntable",
      details: "QWORK Square Ball Bearing 4-Pack (1 used)",
      cost: 1.75,
      pack: 6.98,
      link: "https://www.amazon.com.be/dp/B0B3X7R961",
      notes: "71x71mm steel bearing plate; fits 4x4 base enclosure"
    },
    {
      item: "Color Display Screen",
      details: "3.5\" TFT SPI 480x320 with Touch (1 screen)",
      cost: 17.91,
      pack: 17.91,
      link: "https://www.amazon.com.be/dp/B0BZXX1QFM",
      notes: "480x320 high-contrast LCD for senior visual accessibility"
    },
    {
      item: "Audio Referee DAC Amp",
      details: "MAX98357A I2S 3W Amp 3-Pack (1 used)",
      cost: 3.03,
      pack: 9.09,
      link: "https://www.amazon.com.be/dp/B0F21T7Q3P",
      notes: "Native I2S digital audio from ESP32; zero analog hiss"
    },
    {
      item: "Mini Speaker 40mm",
      details: "RELAND SUN 3W 4Ω 40mm Speakers 2-Pack (1 used)",
      cost: 2.35,
      pack: 4.70,
      link: "https://www.amazon.com.be/dp/B09YQ1S988",
      notes: "40mm diameter fits base cavity; clear vocal resonance"
    },
    {
      item: "Hardware Fasteners Kit",
      details: "440 Pcs M3 Button Head Screws & Nuts Box",
      cost: 7.88,
      pack: 7.88,
      link: "https://www.amazon.com.be/dp/B0B3MGZ7T2",
      notes: "Hex socket button heads; sits flush in CAD counterbores"
    },
    {
      item: "Anti-Skid Bumper Feet",
      details: "Silicone Bumper Feet 10mm 12-Pack (4 used)",
      cost: 3.00,
      pack: 8.99,
      link: "https://www.amazon.com.be/dp/B08GKP4311",
      notes: "High-friction non-marking silicone; fits corner recesses"
    },
    {
      item: "3D Printing Filament",
      details: "PLA / PETG Spool Allocation (~120g)",
      cost: 2.40,
      pack: 19.99,
      link: "hardware/cad/output/",
      notes: "Base enclosure + top grid plate (1.5mm floor, 1.2mm ribs)"
    }
  ];

  const rows = rawData.map((d, index) => {
    const c1 = createTextCell(colItem.id, { content: d.item });
    const c2 = createTextCell(colDetails.id, { content: d.details });
    const c3 = createNumberCell(colAllocated.id, { value: d.cost });
    c3.content = d.cost;
    const c4 = createNumberCell(colPackPrice.id, { value: d.pack });
    c4.content = d.pack;
    const c5 = createTextCell(colLink.id, { content: d.link });
    const c6 = createTextCell(colNotes.id, { content: d.notes });
    return createRow(index, { cells: [c1, c2, c3, c4, c5, c6] });
  });

  const state = createGenericLoomState({
    columns,
    rows,
    pluginVersion: "8.16.17",
    frozenColumnCount: 1
  });

  return serializeState(state);
}

function buildProductionLoom() {
  const colItem = createColumn({ content: "Item / Component", type: "text" });
  colItem.width = "220px";

  const colSupplier = createColumn({ content: "Supplier & Specification", type: "text" });
  colSupplier.width = "270px";

  const colBom = createColumn({ content: "Unit BOM ($)", type: "number" });
  colBom.width = "130px";
  colBom.numberFormat = "currency";
  colBom.currencyType = "USD";
  colBom.calculationType = "sum";

  const colMoq = createColumn({ content: "Batch MOQ / Basis", type: "text" });
  colMoq.width = "180px";

  const colLink = createColumn({ content: "Supplier / Reference Link", type: "text" });
  colLink.width = "320px";

  const colNotes = createColumn({ content: "Notes & Quality Targets", type: "text" });
  colNotes.width = "260px";

  const columns = [colItem, colSupplier, colBom, colMoq, colLink, colNotes];

  const rawData = [
    {
      item: "Beechwood Letter Tiles",
      supplier: "Panda Game Mfg",
      bom: 2.20,
      moq: "1,000 sets (102 tiles/set)",
      link: "https://pandagm.com",
      notes: "19x19x4.8mm Beechwood with factory CNC rear cavity ø15.5x0.8mm"
    },
    {
      item: "15mm NTAG213 Tags on Reels",
      supplier: "CXJ RFID Factory",
      bom: 3.57,
      moq: "2,000-tag reels ($0.035/tag)",
      link: "https://www.cxjrfidfactory.com",
      notes: "15mm clear wet inlays; pre-verified UID manifest file"
    },
    {
      item: "Factory Tag Placement & Mapping",
      supplier: "Board Game Assembly Partner",
      bom: 0.75,
      moq: "1,000 sets (102 tiles/set)",
      link: "https://pandagm.com",
      notes: "Automated pick-and-place tile adhesion + barcode/UID serialization"
    },
    {
      item: "15x15 Main Circuit Board",
      supplier: "JLCPCB / PCBWay",
      bom: 17.50,
      moq: "1,000 boards (320x320mm)",
      link: "https://jlcpcb.com",
      notes: "4-layer FR4; 225 planar spiral antenna coils + SMT analog MUX tree"
    },
    {
      item: "NFC Transceiver IC",
      supplier: "STMicroelectronics (ST25R3916)",
      bom: 3.00,
      moq: "Tape & reel (QFN-32)",
      link: "https://www.st.com/en/nfc/st25r3916.html",
      notes: "1.7W RF output, dynamic power control, capacitive wake-up"
    },
    {
      item: "Rotating Turntable 250mm Ring",
      supplier: "Hardware Wholesale Partner",
      bom: 4.00,
      moq: "1,000 units",
      link: "https://www.alibaba.com",
      notes: "Low-friction extruded aluminum ring with rubber isolating feet"
    },
    {
      item: "3.5\" IPS Color Screen (480x320)",
      supplier: "ST7796 / Panel Partner",
      bom: 7.20,
      moq: "1,000 panels",
      link: "https://www.aliexpress.com",
      notes: "Wide viewing angle IPS LCD; high-contrast UI for seniors"
    },
    {
      item: "Audio Voice Referee Subsystem",
      supplier: "PUI Audio / SMT BOM",
      bom: 2.45,
      moq: "1,000 sets (Amp + Speaker)",
      link: "https://www.puiaudio.com",
      notes: "Tuned 40mm acoustic cavity; warm voice synthesis, zero distortion"
    },
    {
      item: "Host Microcontroller Module",
      supplier: "Espressif Systems (ESP32-S3)",
      bom: 3.00,
      moq: "SMD Reels (ESP32-S3-WROOM-1)",
      link: "https://www.espressif.com",
      notes: "Dual-core 240MHz, 16MB Flash, 8MB PSRAM, CE/FCC certified"
    },
    {
      item: "Battery & Power Management",
      supplier: "Custom Battery Fabricator",
      bom: 6.20,
      moq: "1,000 packs",
      link: "https://www.alibaba.com",
      notes: "3500mAh LiPo cell + PCM protection + magnetic breakaway charging"
    },
    {
      item: "Wood Housing & Tile Grid Frame",
      supplier: "Wood Tooling & Fabricator",
      bom: 14.00,
      moq: "1,000 sets",
      link: "https://pandagm.com",
      notes: "CNC milled solid beech/walnut base tray + laser-cut tile locator grid"
    },
    {
      item: "Packaging, Foam Tray & Guide",
      supplier: "Packaging Fabricator",
      bom: 4.00,
      moq: "1,000 boxes",
      link: "https://pandagm.com",
      notes: "Premium rigid game box + custom die-cut EVA foam + senior guide"
    }
  ];

  const rows = rawData.map((d, index) => {
    const c1 = createTextCell(colItem.id, { content: d.item });
    const c2 = createTextCell(colSupplier.id, { content: d.supplier });
    const c3 = createNumberCell(colBom.id, { value: d.bom });
    c3.content = d.bom;
    const c4 = createTextCell(colMoq.id, { content: d.moq });
    const c5 = createTextCell(colLink.id, { content: d.link });
    const c6 = createTextCell(colNotes.id, { content: d.notes });
    return createRow(index, { cells: [c1, c2, c3, c4, c5, c6] });
  });

  const state = createGenericLoomState({
    columns,
    rows,
    pluginVersion: "8.16.17",
    frozenColumnCount: 1
  });

  return serializeState(state);
}

// Write files
const protoLoom = buildPrototypeLoom();
const protoPath = path.join(__dirname, "../docs/Prototype_4x4_Shopping_List.loom");
fs.writeFileSync(protoPath, protoLoom, "utf8");
console.log(`Generated: ${protoPath}`);

const prodLoom = buildProductionLoom();
const prodPath = path.join(__dirname, "../docs/Production_15x15_Sourcing_List.loom");
fs.writeFileSync(prodPath, prodLoom, "utf8");
console.log(`Generated: ${prodPath}`);

// Verify round-trip deserialization
const protoParsed = deserializeState(protoLoom, "8.16.17");
console.log(`Verified Proto Loom: ${protoParsed.model.columns.length} columns, ${protoParsed.model.rows.length} rows.`);

const prodParsed = deserializeState(prodLoom, "8.16.17");
console.log(`Verified Prod Loom: ${prodParsed.model.columns.length} columns, ${prodParsed.model.rows.length} rows.`);
