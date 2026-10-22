"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { buildFigure, figureIds } = require("../assets/charts.js");
const site = path.resolve(__dirname, "..");
const catalog = JSON.parse(readFileSync(path.join(site, "data/catalog.json")));
const datasets = Object.fromEntries(catalog.datasets.map(dataset =>
  [dataset.id, JSON.parse(readFileSync(path.join(site, dataset.paths.json)))]));
const clone = value => JSON.parse(JSON.stringify(value));
const build = id => buildFigure(catalog, id, datasets);
const points = spec => spec.data.flatMap(trace => trace.x.map((x, i) => [x, trace.y[i]]));

test("exactly the seven included figures build from approved mappings, without mutation or extra charts", () => {
  assert.deepEqual(figureIds, catalog.figures.map(figure => figure.id));
  const before = JSON.stringify({ catalog, datasets });
  for (const id of figureIds) {
    const spec = build(id);
    assert(spec.data.length && spec.caption && spec.sources.length);
    assert.equal(spec.config.displaylogo, false);
    assert.equal(spec.config.displayModeBar, false);
    assert(spec.layout.font.family.includes("system-ui"));
    assert(spec.sources.every(source => datasets[source.id] === source.rows));
  }
  assert.equal(JSON.stringify({ catalog, datasets }), before);
});

test("M1 preserves all means/SD/Ns, facets, family labels/order and the original displayed scale", () => {
  const spec = build("rq1-perceptions");
  assert.equal(spec.data.length, 12);
  assert.equal(points(spec).length, 36);
  for (const trace of spec.data) {
    const rows = datasets["m1-perceptions"].filter(row =>
      row.cohort === trace.customdata[0][0] && row.perception_family === trace.meta.family)
      .sort((a, b) => a.checkpoint.localeCompare(b.checkpoint));
    assert.deepEqual(trace.x, rows.map(row => row.checkpoint));
    assert.deepEqual(trace.y, rows.map(row => row.mean));
    assert.deepEqual(trace.error_y.array, rows.map(row => row.std));
    assert.deepEqual(trace.customdata.map(item => item[1]), rows.map(row => row.response_n));
    assert.equal(trace.error_y.type, "data");
    assert(trace.name.length > 0);
  }
  assert.deepEqual(spec.layout.yaxis.range, [0, 5]);
  assert.deepEqual(spec.layout.yaxis2.range, [0, 5]);
  assert(spec.caption.includes("standard deviations, not confidence intervals"));
});

test("pooled rolling activity is ordered by numeric day and retains fixed original Ns and T3 anchor", () => {
  const spec = build("rq2-pooled-activity");
  const rows = [...datasets["m3-rolling-pooled"]].sort((a, b) => a.window_end_day - b.window_end_day);
  assert.deepEqual(spec.data[0].x, rows.map(row => row.window_end_day));
  assert.deepEqual(spec.data[0].y, rows.map(row => row.total_commit_n));
  assert(spec.data[0].customdata.every(item => item[0] === 14));
  assert.equal(spec.layout.shapes[0].x0, 0);
  assert.equal(spec.layout.legend, undefined);
  assert.deepEqual([spec.layout.annotations[0].x, spec.layout.annotations[0].y,
    spec.layout.annotations[0].text], [1, 302, "Peak: 302"]);
  assert(spec.caption.includes("Overlapping"));
  assert(spec.caption.includes("fixed"));
});

test("planning-concentration scatter preserves exact marker diameters, score colors, cohort symbols and frozen guides", () => {
  const spec = build("rq2-planning-final7");
  for (const trace of spec.data) {
    const rows = datasets["planning-final7-commits"].filter(row => row.cohort === trace.name);
    assert.deepEqual(trace.x, rows.map(row => row.planning_scope_log1p_t1));
    assert.deepEqual(trace.y, rows.map(row => row.final7_share_pct));
    assert.deepEqual(trace.marker.size, rows.map(row => row.marker_size));
    assert.deepEqual(trace.marker.color, rows.map(row => row.evaluator_score_t3));
    assert.equal(trace.marker.sizemode, "diameter");
    assert.equal(trace.marker.cmin, 1.5);
    assert.equal(trace.marker.cmax, 2.5);
    assert.equal(trace.marker.colorscale, "Viridis");
    assert.equal(trace.marker.symbol, trace.name === "2025.2" ? "circle" : "diamond");
    assert.deepEqual(trace.customdata.map(item => item.slice(0, 2)), rows.map(row => [row.cohort, row.team_id]));
  }
  assert.equal(points(spec).length, 14);
  assert.equal(spec.data.filter(trace => trace.marker.showscale).length, 1);
  assert.equal(spec.data[1].marker.colorbar, undefined);
  assert.deepEqual(spec.layout.yaxis.range, [-4, 104]);
  assert.equal(spec.layout.shapes[0].x0, 1.791759469228055);
  assert.equal(spec.layout.shapes[1].y0, 43.743509865005194);
});

test("M4/M5 remain independent panels with distinct units, populations and original denominators", () => {
  const spec = build("rq2-churn-and-lexical-density");
  assert.equal(spec.data[0].type, "bar");
  assert.equal(spec.data[1].type, "scatter");
  assert.equal(spec.data[1].yaxis, "y2");
  assert.deepEqual(spec.data[0].y, datasets["m4-checkpoint-pooled"].map(row => row.total_clean_churn));
  assert.deepEqual(spec.data[1].y, datasets["m5-marker-density"].map(row => row.friction_marker_density_per_1k_tokens));
  assert.deepEqual(spec.data[1].customdata.map(row => row[0]), datasets["m5-marker-density"].map(row => row.token_n));
  assert(spec.layout.yaxis.title.text.includes("lines"));
  assert(spec.layout.yaxis2.title.text.includes("1,000 tokens"));
  assert.equal(spec.sources.length, 2);
});

test("artifact presence is stacked counts, never percentages or re-estimated cohort sizes", () => {
  const spec = build("rq3-artifact-presence");
  assert.equal(spec.layout.barmode, "stack");
  for (const trace of spec.data) {
    const rows = datasets["m6a-presence-by-cohort"].filter(row => row.evidence_state === trace.name);
    assert.deepEqual(trace.y, rows.map(row => row.team_semester_count));
    assert.deepEqual(trace.customdata.map(row => row[0]), rows.map(row => row.team_semester_n));
  }
  assert.equal(spec.layout.yaxis.rangemode, "tozero");
  assert.equal(spec.layout.yaxis.type, "linear");
});

test("log rework excludes original zeros, never substitutes one, keeps all source rows and eligibility symbols", () => {
  const spec = build("rq3-planning-rework");
  assert.equal(spec.layout.yaxis.type, "log");
  assert.equal(points(spec).length, 11);
  assert.equal(spec.excluded.length, 3);
  assert(spec.excluded.every(row => row.reason.includes("zero")));
  assert.equal(spec.sources[0].rows.length, 14);
  assert.equal(spec.caption.includes("3 zero"), true);
  for (const trace of spec.data) {
    assert(trace.y.every(value => value > 0));
    assert(["circle", "diamond"].includes(trace.marker.symbol));
    assert(trace.customdata.every(row => typeof row[2] === "boolean"));
    assert(!trace.hovertemplate.includes("Ratio="));
  }
});

test("complexity scatter retains zeros and ineligible magnitudes, fixed medians and planning/cohort encodings", () => {
  const spec = build("rq3-complexity-rework");
  assert.equal(points(spec).length, 14);
  assert.equal(points(spec).filter(point => point[1] === 0).length, 3);
  assert.equal(spec.layout.yaxis.type, "linear");
  assert.equal(spec.layout.shapes[0].x0, 1.875);
  assert.equal(spec.layout.shapes[1].y0, 842.5);
  const actual = spec.data.flatMap(trace => trace.customdata.map(row => row.slice(0, 2))).sort();
  assert.deepEqual(actual, datasets["complexity-rework-figure"].map(row => [row.cohort, row.team_id]).sort());
  assert.equal(spec.data.flatMap(trace => trace.customdata).filter(row => row[3] === "Unavailable").length,
    datasets["complexity-rework-figure"].filter(row => row.clean_rework_ratio_t3 === null).length);
});

test("missing scatter values are excluded explicitly, not numeric zero; all rows remain in source tables", () => {
  const altered = { ...datasets, "complexity-rework-figure": clone(datasets["complexity-rework-figure"]) };
  altered["complexity-rework-figure"][0].technical_complexity_mean_t3 = null;
  const spec = buildFigure(catalog, "rq3-complexity-rework", altered);
  assert.equal(points(spec).length, 13);
  assert.equal(spec.excluded[0].reason, "unavailable coordinate");
  assert.equal(spec.sources[0].rows.length, 14);
  assert.equal(spec.layout.shapes[0].x0, 1.875);
  assert.equal(spec.layout.shapes[1].y0, 842.5);
});

test("missing line values remain gaps and uncertainty never silently becomes zero", () => {
  const altered = { ...datasets, "m1-perceptions": clone(datasets["m1-perceptions"]) };
  altered["m1-perceptions"][0].mean = null;
  altered["m1-perceptions"][0].std = null;
  const spec = buildFigure(catalog, "rq1-perceptions", altered);
  const trace = spec.data.find(trace => trace.meta.family === "ai_benefit" && trace.customdata[0][0] === "2025.2");
  assert.equal(trace.y[0], null);
  assert.equal(trace.error_y, undefined);
  assert.equal(trace.customdata[0][2], "Unavailable");
  const uncertainty = spec.data.find(item => item.meta?.uncertaintyFor === "ai_benefit");
  assert.deepEqual(uncertainty.x, ["T2", "T3"]);
  assert(uncertainty.error_y.array.every(value => typeof value === "number"));
  assert.equal(trace.connectgaps, false);
});

test("unsupported mappings, missing data, malformed figure fields and invalid scalars fail explicitly", () => {
  assert.throws(() => build("unapproved-figure"));
  assert.throws(() => buildFigure(catalog, "rq1-perceptions", {}));
  const altered = clone(catalog);
  altered.figures[0].panels[0].y = "median";
  assert.throws(() => buildFigure(altered, "rq1-perceptions", datasets), /mapping/);
  for (const value of [Infinity, "2", undefined]) {
    const invalid = { ...datasets, "m1-perceptions": clone(datasets["m1-perceptions"]) };
    invalid["m1-perceptions"][0].mean = value;
    assert.throws(() => buildFigure(catalog, "rq1-perceptions", invalid));
  }
});

test("HTML-like cohort/team metadata is escaped in chart hover/custom labels", () => {
  const altered = { ...datasets, "planning-rework-profile": clone(datasets["planning-rework-profile"]) };
  altered["planning-rework-profile"][0].team_id = "<img src=x>";
  const spec = buildFigure(catalog, "rq3-planning-rework", altered);
  const text = spec.data.flatMap(trace => trace.customdata).find(row => String(row[1]).includes("img"))[1];
  assert.equal(text, "&lt;img src=x&gt;");
});

test("selected source rows drive plots and alternatives without changing frozen score domain or medians", () => {
  const id = "planning-final7-commits";
  const selected = datasets[id].filter(row => row.cohort === "2026.1");
  const spec = buildFigure(catalog, "rq2-planning-final7", datasets, { id, rows: selected, summary: "Cohort: 2026.1" });
  assert.equal(points(spec).length, 5);
  assert.deepEqual(spec.sources[0].rows, selected);
  assert.equal(spec.sources[0].total, 14);
  assert(spec.caption.includes("Cohort: 2026.1"));
  assert(spec.data.every(t => t.marker.cmin === 1.5 && t.marker.cmax === 2.5));
  assert.equal(spec.layout.shapes[1].y0, 43.743509865005194);
});

test("fixed summary selections choose existing rows, not populations, and never cross-filter the other panel", () => {
  const id = "m4-checkpoint-pooled";
  const selected = datasets[id].filter(row => row.checkpoint === "T2");
  const spec = buildFigure(catalog, "rq2-churn-and-lexical-density", datasets, { id, rows: selected, summary: "Checkpoint: T2" });
  assert.equal(spec.data[0].y.length, 1);
  assert.equal(spec.data[0].customdata[0][0], 14);
  assert.equal(spec.data[1].y.length, 3);
  assert(spec.caption.includes("Fixed published summary"));
  assert.equal(spec.sources[1].rows.length, 3);
});

test("empty selection is genuinely empty; logarithmic zeros remain selected source rows but not marks", () => {
  const id = "planning-rework-profile";
  const empty = buildFigure(catalog, "rq3-planning-rework", datasets, { id, rows: [], summary: "Conflicting filters" });
  assert.equal(points(empty).length, 0);
  assert.equal(empty.sources[0].rows.length, 0);
  const zeros = datasets[id].filter(row => row.clean_rework_churn_t3 === 0);
  const spec = buildFigure(catalog, "rq3-planning-rework", datasets, { id, rows: zeros, summary: "Zero cases" });
  assert.equal(points(spec).length, 0);
  assert.equal(spec.excluded.length, 3);
  assert.equal(spec.sources[0].rows.length, 3);
});

test("single-cohort perception selection labels the surviving facet and keeps all family legends and SDs", () => {
  const id = "m1-perceptions";
  for (const cohort of ["2025.2", "2026.1"]) {
    const rows = datasets[id].filter(row => row.cohort === cohort);
    const spec = buildFigure(catalog, "rq1-perceptions", datasets, { id, rows, summary: cohort });
    assert.equal(points(spec).length, 18);
    assert.equal(spec.layout.xaxis.title.text, `${cohort} checkpoint`);
    assert.equal(spec.layout.xaxis2, undefined);
    assert(spec.data.every(t => t.showlegend && t.yaxis === "y" && t.xaxis === "x"));
    assert.deepEqual(spec.layout.yaxis.range, [0, 5]);
    assert.deepEqual(spec.data.flatMap(t => t.error_y.array).sort(), rows.map(r => r.std).sort());
  }
});

test("figure selection rejects altered values, duplicate rows and malformed selection rather than fabricating points", () => {
  const id = "planning-final7-commits";
  for (const rows of [[{ ...datasets[id][0], marker_size: 999 }], [datasets[id][0], datasets[id][0]], null]) {
    assert.throws(() => buildFigure(catalog, "rq2-planning-final7", datasets, { id, rows, summary: "Invalid" }),
      /selection|unchanged/);
  }
});

test("every mapped source supports exact row subsets and order without mutating full snapshots", () => {
  const before = JSON.stringify(datasets);
  for (const figure of catalog.figures) {
    for (const panel of figure.panels) {
      const rows = datasets[panel.dataset].filter((_, i) => i % 2 === 0).reverse();
      const spec = buildFigure(catalog, figure.id, datasets, { id: panel.dataset, rows, summary: "Existing rows" });
      const source = spec.sources.find(s => s.id === panel.dataset);
      assert.deepEqual(source.rows, rows);
      assert.equal(source.total, datasets[panel.dataset].length);
      for (const other of spec.sources.filter(s => s.id !== panel.dataset)) {
        assert.deepEqual(other.rows, datasets[other.id]);
      }
      assert(spec.caption.includes(`${rows.length} of ${source.total} rows`));
    }
  }
  assert.equal(JSON.stringify(datasets), before);
});
