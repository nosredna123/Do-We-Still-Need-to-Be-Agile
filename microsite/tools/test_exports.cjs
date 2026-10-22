"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { csvText, prepareExport, selectRows, sortRows } = require("../assets/app.js");
const site = path.resolve(__dirname, "..");
const catalog = JSON.parse(readFileSync(path.join(site, "data/catalog.json")));
const release = JSON.parse(readFileSync(path.join(site, "data/release.json")));
const rowsFor = dataset => JSON.parse(readFileSync(path.join(site, dataset.paths.json)));
const dataset = catalog.datasets.find(d => d.id === "complexity-rework-figure");
const rows = rowsFor(dataset);

function parseCsv(content) {
  const records = [];
  let record = [], cell = "", quoted = false;
  for (let i = 0; i < content.length; i += 1) {
    const char = content[i];
    if (quoted) {
      if (char === '"' && content[i + 1] === '"') { cell += '"'; i += 1; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"') quoted = true;
    else if (char === "," || char === "\n") {
      record.push(cell); cell = "";
      if (char === "\n") { records.push(record); record = []; }
    } else cell += char;
  }
  assert.equal(quoted, false);
  assert.equal(cell, "");
  assert.equal(record.length, 0);
  return records;
}

test("all49 CSV exports retain exact approved columns and every scalar without mutation", () => {
  let cells = 0;
  for (const d of catalog.datasets) {
    const original = rowsFor(d), before = JSON.stringify(original);
    const parsed = parseCsv(csvText(original, d));
    assert.deepEqual(parsed.shift(), d.columns.map(c => c.id));
    assert.deepEqual(parsed, original.map(row => d.columns.map(c => row[c.id] === null ? "" : String(row[c.id]))));
    assert.equal(JSON.stringify(original), before);
    cells += parsed.flat().length;
  }
  assert.equal(cells, 17046);
});

test("CSV quotes commas, double quotes, Unicode, newlines and text without altering typed numbers or null", () => {
  const d = { columns: [
    { id: "text", type: "string", nullable: false },
    { id: "n", type: "number", nullable: true },
    { id: "flag", type: "boolean", nullable: false },
  ], key: ["text"] };
  const original = [{ text: 'a,"b"\nnext \u00e9', n: -0.12345678901234568, flag: false },
    { text: "null example", n: null, flag: true }, { text: "0", n: 0, flag: true }];
  const csv = csvText(original, d);
  assert.deepEqual(parseCsv(csv), [["text", "n", "flag"], ...original.map(r => [r.text, r.n === null ? "" : String(r.n), String(r.flag)])]);
  assert(csvText([{ text: "", n: null, flag: true }], { ...d, key: ["flag"] }).includes('"",,true\n'));
  assert(csv.includes("-0.12345678901234568"));
  assert.equal(csv.charCodeAt(0) === 0xfeff, false);
});

test("spreadsheet-unsafe textual cells and headers are rejected, not prefixed or silently changed", () => {
  const d = { columns: [{ id: "label", type: "string", nullable: false }], key: ["label"] };
  for (const value of ["=SUM(1)", " +formula", "-formula", "@formula", "\tformula", " \tformula", "\rvalue", "\nvalue"]) {
    assert.throws(() => csvText([{ label: value }], d), /Spreadsheet-unsafe/);
  }
  assert.throws(() => csvText([{ "=header": "safe" }], { ...d, columns: [{ ...d.columns[0], id: "=header" }] }),
    /Spreadsheet-unsafe/);
});

test("filtered export follows exact composite choices and current sorted order with reusable scope/definitions", () => {
  const selection = { team_semester: ['["2025.2","TEAM_01"]', '["2026.1","TEAM_01"]'] };
  const sort = { field: "clean_rework_churn_t3", direction: "descending" };
  const visible = sortRows(selectRows(rows, dataset, selection), dataset.columns.find(c => c.id === sort.field), sort.direction);
  const result = prepareExport(dataset, rows, selection, sort, release.snapshot_id);
  assert.deepEqual(parseCsv(result.csv).slice(1), visible.map(r => dataset.columns.map(c => r[c.id] === null ? "" : String(r[c.id]))));
  assert.deepEqual(result.metadata.filters, selection);
  assert.deepEqual(result.metadata.filter_definitions, dataset.filters);
  assert(result.metadata.filter_value_encoding.includes("typed values"));
  assert.deepEqual(result.metadata.sort, sort);
  assert.deepEqual(result.metadata.columns, dataset.columns);
  assert.equal(result.metadata.snapshot_id, release.snapshot_id);
  assert.equal(result.metadata.selected_row_count, 2);
  assert.equal(result.metadata.total_row_count, 14);
  assert.equal(result.metadata.denominator, dataset.denominator);
  assert.equal(result.metadata.filter_effect, dataset.filter_effect);
  assert.equal(result.filename, `${dataset.id}-filtered.csv`);
  assert(result.metadata.csv_null_encoding.includes("empty"));
});

test("empty filter results export headers only with zero selected rows, not a fabricated row", () => {
  const selection = { cohort: ['["2026.1"]'], team_semester: ['["2025.2","TEAM_01"]'] };
  const result = prepareExport(dataset, rows, selection, null, release.snapshot_id);
  assert.deepEqual(parseCsv(result.csv), [dataset.columns.map(c => c.id)]);
  assert.equal(result.metadata.selected_row_count, 0);
  assert.equal(result.metadata.total_row_count, 14);
});

test("invalid scalar/schema/filter/sort fails explicitly before producing CSV", () => {
  assert.throws(() => csvText([{ ...rows[0], extra: "hidden" }], dataset), /columns/);
  assert.throws(() => csvText([{ ...rows[0], clean_rework_churn_t3: NaN }], dataset), /Invalid value/);
  assert.throws(() => prepareExport(dataset, rows, { bad: ["x"] }, null, release.snapshot_id), /filter/);
  assert.throws(() => prepareExport(dataset, rows, {}, { field: "bad", direction: "ascending" }, release.snapshot_id), /sort/);
});

test("each permitted single-choice filter exports the same existing rows with unchanged definitions and fixed populations", () => {
  for (const d of catalog.datasets) {
    const source = rowsFor(d);
    for (const filter of d.filters) {
      const choices = [...new Set(source.map(row => JSON.stringify(filter.fields.map(field => row[field]))))];
      for (const choice of choices) {
        const selection = { [filter.id]: [choice] };
        const result = prepareExport(d, source, selection, null, release.snapshot_id);
        const wanted = selectRows(source, d, selection).map(row => d.columns.map(c => row[c.id] === null ? "" : String(row[c.id])));
        assert.deepEqual(parseCsv(result.csv).slice(1), wanted);
        assert.equal(result.metadata.estimation_population, d.estimation_population);
        assert.deepEqual(result.metadata.columns, d.columns);
      }
    }
  }
});

test("typed nulls, zero, false and text remain distinct; ambiguous nullable empty text fails explicitly", () => {
  const d = { columns: [
    { id: "id", type: "integer", nullable: false },
    { id: "text", type: "string", nullable: true },
    { id: "number", type: "number", nullable: true },
    { id: "flag", type: "boolean", nullable: true },
  ], key: ["id"] };
  const values = [{ id: 1, text: null, number: null, flag: null },
    { id: 2, text: "null", number: 0, flag: false }];
  assert.deepEqual(parseCsv(csvText(values, d)).slice(1), [["1", "", "", ""], ["2", "null", "0", "false"]]);
  assert.throws(() => csvText([{ ...values[0], text: "" }], d), /ambiguous/);
});
