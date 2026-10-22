/* Run with node --test tools/test_app.cjs; no packages or private inputs. */
"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { validateMetadata, matchingDatasets, matchesDefinition, loadMetadata } = require("../assets/app.js");
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
