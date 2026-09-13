#!/usr/bin/env node
/** Assemble an editable hybrid academic-figure PPTX and trace manifest. */

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import crypto from "node:crypto";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATE_MANIFEST = path.resolve(SCRIPT_DIR, "../assets/style_manifest.template.yaml");

async function loadArtifactTool() {
  const roots = [
    process.env.RUNTIME_NODE_MODULES,
    ...(process.env.NODE_PATH || "").split(path.delimiter),
    path.resolve(process.cwd(), "node_modules"),
    path.resolve(SCRIPT_DIR, "node_modules"),
  ].filter(Boolean);
  for (const root of roots) {
    const entry = path.join(root, "@oai", "artifact-tool", "dist", "artifact_tool.mjs");
    try {
      await fs.access(entry);
      return import(pathToFileURL(entry).href);
    } catch {
      // Try the next configured runtime root.
    }
  }
  throw new Error("@oai/artifact-tool was not found. Load the Codex workspace dependencies and set RUNTIME_NODE_MODULES; do not install a replacement silently.");
}

function usage() {
  return `build_figure_pptx.mjs

Usage:
  node build_figure_pptx.mjs --spec assembly.json --style-manifest style_manifest.yaml --output paper_figure_kit.pptx [options]
  node build_figure_pptx.mjs --demo --output demo_figure_kit.pptx [options]

Options:
  --spec PATH             Backend-neutral JSON assembly specification.
  --style-manifest PATH   JSON-compatible YAML style manifest.
  --style-json PATH       Normalized JSON emitted by validate_style_manifest.py.
  --output PATH           Output PPTX path (required).
  --manifest PATH         Output ppt_manifest.json path.
  --caption PATH          Figure caption Markdown/text; embedded in publication-slide notes.
  --preview-dir PATH      Retained preview directory; used only with --retain-previews.
  --retain-previews       Keep slide PNG/layout previews after QA (default: delete them).
  --demo                  Build a two-slide self-contained smoke-test kit.
  --help                  Show this help.

Full YAML requires prior normalization; no dependency is installed silently.`;
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") args.help = true;
    else if (token === "--demo") args.demo = true;
    else if (token === "--retain-previews") args.retain_previews = true;
    else if (token.startsWith("--")) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) throw new Error(`Missing value for ${token}`);
      args[token.slice(2).replaceAll("-", "_")] = value;
      index += 1;
    } else throw new Error(`Unexpected argument: ${token}`);
  }
  return args;
}

async function readJsonCompatible(filePath, label) {
  const text = await fs.readFile(filePath, "utf8");
  try {
    return JSON.parse(text.replace(/^\uFEFF/, ""));
  } catch (error) {
    throw new Error(`${label} is not JSON-compatible. Normalize full YAML with validate_style_manifest.py --emit-json. ${error.message}`);
  }
}

function get(object, keys, fallback) {
  let value = object;
  for (const key of keys) {
    if (!value || typeof value !== "object" || !(key in value)) return fallback;
    value = value[key];
  }
  return value;
}

function ensureHex(value, fallback) {
  return typeof value === "string" && /^#[0-9A-Fa-f]{6}$/.test(value) ? value : fallback;
}

function fontPx(style, token, fallbackPt) {
  return Number(get(style, ["typography", "hierarchy_pt", token], fallbackPt)) * (96 / 72);
}

function boundsOf(object, autoBounds) {
  const raw = object.bounds || object.position || autoBounds;
  const bounds = {
    left: Number(raw.left), top: Number(raw.top), width: Number(raw.width), height: Number(raw.height),
  };
  if (Object.values(bounds).some((value) => !Number.isFinite(value))) throw new Error(`Invalid bounds for ${object.id}`);
  return bounds;
}

function autoGridBounds(index, count, slideSize, titleOffset = 36, layout = {}) {
  const margin = Number(layout.outerMargin || 54);
  const gap = Number(layout.objectGap || 30);
  const columns = Math.max(1, Math.ceil(Math.sqrt(count)));
  const rows = Math.max(1, Math.ceil(count / columns));
  const width = (slideSize.width - 2 * margin - gap * (columns - 1)) / columns;
  const height = (slideSize.height - margin - titleOffset - margin - gap * (rows - 1)) / rows;
  return {
    left: margin + (index % columns) * (width + gap),
    top: margin + titleOffset + Math.floor(index / columns) * (height + gap),
    width,
    height,
  };
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ({ ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".tif": "image/tiff", ".tiff": "image/tiff", ".webp": "image/webp" })[ext];
}

function hash(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function styleTokens(style) {
  return {
    background: ensureHex(get(style, ["backgrounds", "slide"], "#FFFFFF"), "#FFFFFF"),
    panel: ensureHex(get(style, ["backgrounds", "panel"], "#F7F7F7"), "#F7F7F7"),
    text: ensureHex(get(style, ["neutral_colors", "text"], "#172B4D"), "#172B4D"),
    muted: ensureHex(get(style, ["neutral_colors", "muted_text"], "#666666"), "#666666"),
    border: ensureHex(get(style, ["neutral_colors", "border"], "#172B4D"), "#172B4D"),
    font: String(get(style, ["typography", "family", "sans"], "Arial")),
    borderWidth: Number(get(style, ["strokes", "module_pt"], 0.8)) * (96 / 72),
    connectorWidth: Number(get(style, ["strokes", "connector_pt"], 0.9)) * (96 / 72),
    cornerRadius: Number(get(style, ["corners", "module_radius_pt"], 4)) * (96 / 72),
    shadow: get(style, ["shadows", "enabled"], false) ? String(get(style, ["shadows", "token"], "shadow-sm")) : "shadow-none",
    semantic: get(style, ["semantic_colors"], {}),
    outerMargin: Number(get(style, ["powerpoint", "outer_margin_px"], 54)),
    objectGap: Number(get(style, ["powerpoint", "object_gap_px"], 30)),
    panelLabelOffset: Number(get(style, ["powerpoint", "panel_label_offset_px"], 24)),
  };
}

function demoSpec(style) {
  const blocks = ["Input", "Encoder", "Attention", "Fusion", "Decoder", "Output"].map((label, index) => ({
    id: `demo_${label.toLowerCase()}`,
    type: "native_block",
    label,
    semantic_role: label.toLowerCase(),
    bounds: { left: 80 + index * 235, top: 330, width: 170, height: 105 },
    editability: "A",
    source_trace: ["demo-only; replace with manuscript evidence"],
  }));
  const connectors = blocks.slice(0, -1).map((block, index) => ({
    id: `demo_link_${index + 1}`,
    type: "connector",
    from: block.id,
    to: blocks[index + 1].id,
    editability: "A",
    source_trace: ["demo-only"],
  }));
  const inlineSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="240" viewBox="0 0 640 240"><rect x="4" y="4" width="632" height="232" rx="24" fill="${style.semantic_colors?.encoder || "#AEC4E6"}" stroke="${style.neutral_colors?.border || "#172B4D"}" stroke-width="8"/><text x="320" y="132" font-family="Arial" font-size="44" text-anchor="middle">Vector SVG panel</text></svg>`;
  const vector = { id: "demo_vector", type: "asset", inline_svg: inlineSvg, panel_label: "(a)", editability: "B", bounds: { left: 110, top: 95, width: 620, height: 210 }, source_trace: ["demo inline SVG"] };
  return {
    slide_size: { width: Number(get(style, ["powerpoint", "slide_width_px"], 1600)), height: Number(get(style, ["powerpoint", "slide_height_px"], 900)) },
    mode: "hybrid",
    slides: [
      { kind: "figure_assembly", title: "Editable academic figure kit — smoke test", objects: [vector, ...blocks, ...connectors] },
      { kind: "component_board", title: "Editable Components", objects: [] },
    ],
  };
}

async function addObject({ slide, object, objectIndex, objectCount, slideSize, titleOffset, style, tokens, specDir, shapeMap, objectRecords, assetRecords, sourceTrace, isBoard }) {
  const auto = autoGridBounds(objectIndex, objectCount, slideSize, titleOffset, tokens);
  const bounds = boundsOf(object, auto);
  const level = String(object.editability || (object.type === "asset" ? "B" : "A")).toUpperCase();
  const baseRecord = { id: object.id, type: object.type, editability: level, bounds, source_trace: object.source_trace || [] };
  let facade;

  if (object.type === "native_block") {
    const role = String(object.semantic_role || "encoder");
    const fill = ensureHex(tokens.semantic[role], tokens.panel);
    facade = slide.shapes.add({
      geometry: "roundRect", name: object.id, position: bounds, fill,
      line: { style: "solid", fill: tokens.border, width: tokens.borderWidth },
      borderRadius: tokens.cornerRadius, shadow: tokens.shadow,
    });
    facade.text = String(object.label || object.id);
    facade.text.style = { fontSize: fontPx(style, "body", 6.5) * (isBoard ? 1.25 : 1), fontFamily: tokens.font, color: tokens.text, bold: Boolean(object.bold), alignment: "center", verticalAlignment: "middle" };
    shapeMap.set(object.id, facade);
  } else if (object.type === "text") {
    facade = slide.shapes.add({ geometry: "textbox", name: object.id, position: bounds, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
    facade.text = String(object.text || "");
    facade.text.style = { fontSize: Number(object.font_size || fontPx(style, "body", 6.5)), fontFamily: tokens.font, color: ensureHex(object.color, tokens.text), bold: Boolean(object.bold), alignment: object.alignment || "left", verticalAlignment: object.vertical_alignment || "middle" };
    shapeMap.set(object.id, facade);
  } else if (object.type === "native_arrow") {
    const arrowBounds = {
      left: bounds.left + bounds.width * 0.12,
      top: bounds.top + bounds.height * 0.34,
      width: bounds.width * 0.76,
      height: bounds.height * 0.32,
    };
    facade = slide.shapes.add({ geometry: object.geometry || "rightArrow", name: object.id, position: arrowBounds, fill: ensureHex(object.color, tokens.border), line: { style: "solid", fill: tokens.border, width: Math.max(0.5, tokens.borderWidth * 0.6) } });
    baseRecord.bounds = arrowBounds;
    shapeMap.set(object.id, facade);
  } else if (object.type === "connector") {
    baseRecord.pending_connector = true;
  } else if (object.type === "asset") {
    let bytes;
    let sourcePath = "";
    let contentType;
    if (object.inline_svg) {
      bytes = Buffer.from(String(object.inline_svg), "utf8");
      contentType = "image/svg+xml";
      sourcePath = "inline:svg";
    } else {
      if (!object.path) throw new Error(`Asset ${object.id} has no path`);
      sourcePath = path.resolve(specDir, object.path);
      bytes = await fs.readFile(sourcePath);
      contentType = contentTypeFor(sourcePath);
      if (!contentType) throw new Error(`Unsupported asset type for ${object.id}: ${sourcePath}`);
    }
    if (level === "B" && contentType !== "image/svg+xml") throw new Error(`Level B asset ${object.id} must be SVG, got ${contentType}`);
    if (level === "C" && contentType === "image/svg+xml") throw new Error(`Level C asset ${object.id} should be raster, not SVG`);
    facade = slide.images.add({ blob: new Uint8Array(bytes), contentType, alt: String(object.alt || object.id), fit: "contain", position: bounds });
    const record = { id: object.id, source: sourcePath, content_type: contentType, sha256: hash(bytes), editability: level, preserve_aspect_ratio: true, source_trace: object.source_trace || [] };
    assetRecords.push(record);
    baseRecord.asset_sha256 = record.sha256;
    baseRecord.content_type = contentType;
  } else {
    throw new Error(`Unsupported object type ${object.type} for ${object.id}`);
  }

  if (object.panel_label) {
    const label = slide.shapes.add({ geometry: "textbox", name: `${object.id}_panel_label`, position: { left: bounds.left - tokens.panelLabelOffset, top: Math.max(4, bounds.top - tokens.panelLabelOffset), width: 60, height: 30 }, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
    label.text = String(object.panel_label);
    label.text.style = { fontSize: fontPx(style, "panel_label", 8), fontFamily: tokens.font, color: tokens.text, bold: true, alignment: "left", verticalAlignment: "middle" };
    objectRecords.push({ id: `${object.id}_panel_label`, type: "native_panel_label", editability: "A", parent: object.id });
  }

  objectRecords.push(baseRecord);
  sourceTrace[object.id] = object.source_trace || [];
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { console.log(usage()); return; }
  if (!args.output) throw new Error("--output is required");
  if (!args.demo && !args.spec) throw new Error("--spec is required unless --demo is used");
  if (!args.demo && !args.style_manifest && !args.style_json) throw new Error("--style-manifest or --style-json is required");

  const stylePath = path.resolve(args.style_json || args.style_manifest || TEMPLATE_MANIFEST);
  const style = await readJsonCompatible(stylePath, "Style manifest");
  const specPath = args.spec ? path.resolve(args.spec) : "";
  const spec = args.demo ? demoSpec(style) : await readJsonCompatible(specPath, "Assembly spec");
  if (!Array.isArray(spec.slides) || spec.slides.length === 0) throw new Error("Assembly spec needs at least one slide");

  const outputPath = path.resolve(args.output);
  const outputDir = path.dirname(outputPath);
  const manifestPath = path.resolve(args.manifest || path.join(outputDir, "ppt_manifest.json"));
  const retainPreviews = Boolean(args.retain_previews);
  const previewDir = retainPreviews
    ? path.resolve(args.preview_dir || path.join(outputDir, "preview"))
    : path.join(outputDir, `.figure-build-preview-${process.pid}`);
  const captionPath = args.caption
    ? path.resolve(args.caption)
    : (spec.caption ? path.resolve(specPath ? path.dirname(specPath) : process.cwd(), spec.caption) : "");
  const captionText = captionPath ? (await fs.readFile(captionPath, "utf8")).trim() : "";
  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });

  const slideSize = spec.slide_size || { width: 1600, height: 900 };
  const { FileBlob, Presentation, PresentationFile } = await loadArtifactTool();
  const presentation = Presentation.create({ slideSize });
  const tokens = styleTokens(style);
  presentation.theme.colorScheme = {
    name: "Academic Figure Manifest",
    themeColors: {
      accent1: ensureHex(tokens.semantic.proposed_method, "#2F5D8C"), accent2: ensureHex(tokens.semantic.encoder, "#AEC4E6"),
      accent3: ensureHex(tokens.semantic.fusion, "#F7DFA0"), accent4: ensureHex(tokens.semantic.output, "#F3B9BA"),
      accent5: ensureHex(tokens.semantic.attention, "#D7C1E8"), accent6: ensureHex(tokens.semantic.decoder, "#C7E2B5"),
      bg1: tokens.background, bg2: tokens.panel, tx1: tokens.text, tx2: tokens.muted,
      dk1: "#000000", dk2: tokens.text, lt1: "#FFFFFF", lt2: tokens.panel, hlink: ensureHex(tokens.semantic.proposed_method, "#2F5D8C"), folHlink: ensureHex(tokens.semantic.attention, "#D7C1E8"),
    },
  };

  const manifest = {
    style_manifest: path.relative(path.dirname(manifestPath), stylePath).replaceAll("\\", "/"),
    assembly_spec: specPath ? path.relative(path.dirname(manifestPath), specPath).replaceAll("\\", "/") : "internal-demo",
    backend: { name: "@oai/artifact-tool", mode: spec.mode || "hybrid", rendered_preview: true },
    caption: captionPath ? path.relative(path.dirname(manifestPath), captionPath).replaceAll("\\", "/") : null,
    slide_size: { width: Number(slideSize.width), height: Number(slideSize.height), unit: "backend_px" },
    slides: [], assets: [], source_trace: {},
    editability: { native_ppt_objects: 0, vector_svg_objects: 0, raster_objects: 0, external_editable_source_files: [] },
    raster_fallbacks: [], unresolved_issues: [], structural_qa: { pptx_reopened: false, package_inspection: "pending" },
  };

  const firstAssemblyObjects = spec.slides.find((item) => item.kind === "figure_assembly")?.objects || [];
  for (let slideIndex = 0; slideIndex < spec.slides.length; slideIndex += 1) {
    const slideSpec = spec.slides[slideIndex];
    const slide = presentation.slides.add();
    slide.background.fill = tokens.background;
    const isBoard = slideSpec.kind === "component_board";
    const titleOffset = isBoard ? 78 : (slideSpec.title ? 44 : 8);
    const objectRecords = [];
    if (slideSpec.title) {
      const title = slide.shapes.add({ geometry: "textbox", name: `slide_${slideIndex + 1}_title`, position: { left: tokens.outerMargin, top: 14, width: slideSize.width - 2 * tokens.outerMargin, height: 36 }, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
      title.text = String(slideSpec.title);
      title.text.style = { fontSize: fontPx(style, "title", 8), fontFamily: tokens.font, color: tokens.text, bold: true, alignment: "left", verticalAlignment: "middle" };
      objectRecords.push({ id: `slide_${slideIndex + 1}_title`, type: "native_title", editability: "A" });
    }
    if (isBoard) {
      const legend = slide.shapes.add({ geometry: "textbox", name: `slide_${slideIndex + 1}_editability_legend`, position: { left: tokens.outerMargin, top: 48, width: slideSize.width - 2 * tokens.outerMargin, height: 28 }, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
      legend.text = "A  Native PowerPoint object     B  Vector SVG + external editable source     C  Raster asset";
      legend.text.style = { fontSize: fontPx(style, "annotation", 5.5) * 1.2, fontFamily: tokens.font, color: tokens.muted, alignment: "left", verticalAlignment: "middle" };
      objectRecords.push({ id: `slide_${slideIndex + 1}_editability_legend`, type: "native_editability_legend", editability: "A" });
    }
    const objects = isBoard && (!slideSpec.objects || slideSpec.objects.length === 0)
      ? [...firstAssemblyObjects.filter((object) => object.type !== "connector"), { id: "component_arrow_sample", type: "native_arrow", editability: "A", source_trace: ["style_manifest.arrows"] }]
      : (slideSpec.objects || []);
    const shapeMap = new Map();
    const connectors = [];
    for (let objectIndex = 0; objectIndex < objects.length; objectIndex += 1) {
      const sourceObject = objects[objectIndex];
      const object = isBoard
        ? { ...sourceObject, bounds: undefined, position: undefined, panel_label: undefined }
        : sourceObject;
      if (!object.id) throw new Error(`Slide ${slideIndex + 1} object ${objectIndex + 1} has no id`);
      if (object.type === "connector") connectors.push(object);
      await addObject({ slide, object, objectIndex, objectCount: objects.length, slideSize, titleOffset, style, tokens, specDir: specPath ? path.dirname(specPath) : process.cwd(), shapeMap, objectRecords, assetRecords: manifest.assets, sourceTrace: manifest.source_trace, isBoard });
    }
    for (const connectorObject of connectors) {
      const from = shapeMap.get(connectorObject.from);
      const to = shapeMap.get(connectorObject.to);
      if (!from || !to) {
        manifest.unresolved_issues.push(`Connector ${connectorObject.id} endpoints are not native shapes on slide ${slideIndex + 1}`);
        const record = objectRecords.find((item) => item.id === connectorObject.id);
        if (record) record.editability = "unresolved";
        continue;
      }
      slide.shapes.connect(from, to, {
        kind: connectorObject.kind || "straight", fromSide: connectorObject.from_side || "right", toSide: connectorObject.to_side || "left",
        line: { style: connectorObject.line_style || "solid", fill: ensureHex(connectorObject.color, tokens.border), width: tokens.connectorWidth },
        tail: { type: get(style, ["arrows", "type"], "triangle"), width: get(style, ["arrows", "width"], "med"), length: get(style, ["arrows", "length"], "med") },
      });
    }
    const captionBlock = captionText && !isBoard ? `[Figure caption]\n${captionText}\n\n` : "";
    slide.speakerNotes.textFrame.setText(`${captionBlock}[Authoring trace]\nStyle manifest: ${stylePath}\nObject source trace is stored in ${manifestPath}.`);
    manifest.slides.push({
      index: slideIndex + 1,
      kind: slideSpec.kind || "figure_assembly",
      title: slideSpec.title || "",
      objects: objectRecords,
      preview: retainPreviews ? `slide-${String(slideIndex + 1).padStart(2, "0")}.png` : null,
    });
  }

  for (const slideInfo of manifest.slides) {
    for (const object of slideInfo.objects) {
      if (object.editability === "A") manifest.editability.native_ppt_objects += 1;
      else if (object.editability === "B") manifest.editability.vector_svg_objects += 1;
      else if (object.editability === "C") manifest.editability.raster_objects += 1;
    }
  }
  const sourceFiles = new Set();
  for (const trace of Object.values(manifest.source_trace)) for (const item of trace) if (typeof item === "string" && !item.startsWith("demo")) sourceFiles.add(item);
  manifest.editability.external_editable_source_files = [...sourceFiles];

  for (let index = 0; index < presentation.slides.items.length; index += 1) {
    const slide = presentation.slides.items[index];
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(previewDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 2 }));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(previewDir, `${stem}.layout.json`), await layout.text(), "utf8");
  }
  await writeBlob(path.join(previewDir, "deck-montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(outputPath);
  try {
    const reopened = await PresentationFile.importPptx(await FileBlob.load(outputPath));
    manifest.structural_qa.pptx_reopened = reopened.slides.items.length === presentation.slides.items.length;
  } catch (error) {
    manifest.unresolved_issues.push(`PPTX reopen failed: ${error.message}`);
  }
  manifest.backend.rendered_preview = retainPreviews ? "retained" : "validated_then_removed";
  if (!retainPreviews) await fs.rm(previewDir, { recursive: true, force: true });
  await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2) + "\n", "utf8");
  console.log(`pptx=${outputPath} manifest=${manifestPath} previews=${retainPreviews ? previewDir : "removed"} slides=${manifest.slides.length}`);
}

main().catch((error) => { console.error(`error: ${error.message}`); process.exitCode = 1; });
