/* Run with node --test tools/test_app.cjs; no packages or private inputs. */
"use strict";

const assert = require("node:assert/strict");
const { readFileSync, readdirSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { validateMetadata, matchingDatasets, matchesDefinition, loadMetadata, validateRows } = require("../assets/app.js");
const site = path.resolve(__dirname, "..");
const catalog = JSON.parse(readFileSync(path.join(site, "data/catalog.json")));
const release = JSON.parse(readFileSync(path.join(site, "data/release.json")));
const clone = value => JSON.parse(JSON.stringify(value));

test("accepts the shipped catalog and matching release", () => {
  assert.doesNotThrow(() => validateMetadata(catalog, release));
});

test("RQ/metric/source selection covers all datasets without inventing relationships", () => {
  assert.equal(matchingDatasets(catalog, "", "", "").length, 49);
  for (const dataset of catalog.datasets) {
    for (const metric of dataset.metrics) {
      const choices = matchingDatasets(catalog, dataset.rq, metric, dataset.source);
      assert(choices.some(choice => choice.id === dataset.id));
      assert(choices.every(choice => choice.rq === dataset.rq &&
        choice.metrics.includes(metric) && choice.source === dataset.source));
    }
  }
  assert.deepEqual(matchingDatasets(catalog, "RQ1", "M8", ""), []);
  assert.deepEqual(matchingDatasets(catalog, "RQ2", "", "surveys"), []);
  assert(matchingDatasets(catalog, "RQ2", "M6").some(dataset => dataset.id === "planning-final7-commits"));
});

test("definition search includes metric, field, unit, and literal text without regex", () => {
  const dataset = catalog.datasets.find(item => item.id === "m8-rework-magnitude");
  for (const query of ["m8", " RQ3 ", "clean_rework_ratio_t3", dataset.columns[0].unit, ""]) {
    assert(matchesDefinition(dataset, query), query);
  }
  assert(!matchesDefinition(dataset, "unmatched-definition-012345"));
  assert(!matchesDefinition(dataset, ".*"));
});

test("rejects unsupported metadata versions and policies", () => {
  for (const [field, value] of [
    ["schema_version", "2.0"], ["path_base", "catalog"], ["language", "pt"],
    ["status", "published"], ["excerpt_policy", "enabled"],
  ]) {
    const altered = clone(catalog);
    altered[field] = value;
    assert.throws(() => validateMetadata(altered, release));
  }
  const altered = clone(release);
  altered.schema_version = "2.0";
  assert.throws(() => validateMetadata(catalog, altered));
});

test("rejects malformed, duplicate, or unsafe dataset descriptors", () => {
  for (const mutate of [
    c => { c.datasets[0].columns[0].unit = null; },
    c => { c.datasets[0].columns[0].nullable = "false"; },
    c => { c.datasets[0].key = ["unknown"]; },
    c => { c.datasets[0].source = "unknown"; },
    c => { c.datasets[0].metrics = ["M99"]; },
    c => { c.datasets.push(c.datasets[0]); },
    c => { c.datasets[0].paths.json = "https://example.invalid/data.json"; },
    c => { c.datasets[0].paths.csv = "../private.csv"; },
    c => { c.datasets[0].coverage = null; },
    c => { c.datasets[0].filters[0].fields = ["unknown"]; },
    c => { c.datasets[0].filters[0].mode = "query"; },
    c => { c.datasets[0].filters.push({ id: "team", label: "Team", fields: ["team_id"], mode: "multi_select" }); },
    c => { c.methods.definition_sets[0].rows = "malformed"; },
    c => { c.methods.definition_sets[0].rows[0].unexpected = []; },
  ]) {
    const altered = clone(catalog);
    mutate(altered);
    assert.throws(() => validateMetadata(altered, release));
  }
});

test("rejects inconsistent snapshot inventory, counts, and fingerprints", () => {
  for (const mutate of [
    r => { r.summary.dataset_count = 50; },
    r => { r.summary.observation_row_count += 1; },
    r => { r.datasets[0].id = "unknown"; },
    r => { r.datasets[0].column_count += 1; },
    r => { r.artifacts[0].sha256 = "not-a-hash"; },
    r => { r.artifacts.pop(); },
    r => { r.artifacts.push(r.artifacts[0]); },
    r => { r.snapshot_id = ""; },
  ]) {
    const altered = clone(release);
    mutate(altered);
    assert.throws(() => validateMetadata(catalog, altered));
  }
});

test("loads only two local metadata files, not observation files", async () => {
  const calls = [];
  const fetcher = async (url, options) => {
    calls.push(url);
    assert(options.signal instanceof AbortSignal);
    return { ok: true, json: async () => url.endsWith("catalog.json") ? catalog : release };
  };
  const loaded = await loadMetadata(fetcher);
  assert.equal(loaded.catalog, catalog);
  assert.equal(loaded.release, release);
  assert.deepEqual(calls.sort(), ["data/catalog.json", "data/release.json"]);
});

test("omission release contains no excerpt descriptor, artifact or empty placeholder", () => {
  const walk = directory => readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const name = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(name) : [path.relative(site, name).split(path.sep).join("/")];
  });
  const excerptName = /excerpt|verbatim|quotation/i;
  for (const name of walk(path.join(site, "data"))) assert(!excerptName.test(name), name);
  for (const dataset of catalog.datasets) {
    assert(!excerptName.test([dataset.id, dataset.title, dataset.source, ...Object.values(dataset.paths)].join(" ")));
    assert(!matchesDefinition(dataset, "qualitative-excerpts"));
    assert(!dataset.columns.some(column =>
      ["text", "quote", "excerpt", "evidence_quotes", "raw_response", "parsed_response"].includes(column.id)));
  }
  for (const artifact of release.artifacts) assert(!excerptName.test(artifact.path), artifact.path);
});

test("changed or missing excerpt policy fails metadata loading before any observations are requested", async () => {
  for (const policy of [undefined, "approved", "enabled", ""]) {
    const altered = clone(catalog);
    if (policy === undefined) delete altered.excerpt_policy;
    else altered.excerpt_policy = policy;
    const calls = [];
    await assert.rejects(loadMetadata(async url => {
      calls.push(url);
      assert(["data/catalog.json", "data/release.json"].includes(url));
      return { ok: true, json: async () => url.endsWith("catalog.json") ? altered : release };
    }), /publication policy/);
    assert.deepEqual(calls.sort(), ["data/catalog.json", "data/release.json"]);
  }
});

test("omission keeps approved lexical aggregates and planning counts, never their source quotations", () => {
  for (const id of ["m5-marker-density", "m5-marker-composition", "m5-corpus-coverage",
    "m5-lexicon", "transcript-context-2025", "m6b-planning-content"]) {
    const dataset = catalog.datasets.find(item => item.id === id);
    assert(dataset, id);
    const rows = JSON.parse(readFileSync(path.join(site, dataset.paths.json)));
    validateRows(rows, dataset, release.datasets.find(item => item.id === id).row_count);
    const altered = clone(rows);
    altered[0].evidence_quotes = ["Synthetic unapproved text"];
    assert.throws(() => validateRows(altered, dataset, rows.length), /columns disagree/);
    if (id === "m6b-planning-content") {
      assert(dataset.columns.some(column => column.id === "evidence_quotes_n"));
      assert(rows.some(row => row.evidence_quotes_n > 0));
      assert(rows.every(row => !Object.hasOwn(row, "evidence_quotes")));
    }
  }
});

test("HTTP failures and invalid JSON are explicit load errors", async () => {
  await assert.rejects(loadMetadata(async () => ({ ok: false, status: 404 })), /404/);
  await assert.rejects(loadMetadata(async () => ({
    ok: true, json: async () => { throw new SyntaxError("bad JSON"); },
  })), /bad JSON/);
});

test("timeout aborts stalled requests rather than leaving loading forever", async () => {
  const fetcher = (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  });
  await assert.rejects(loadMetadata(fetcher, 5), /timed out/);
});
