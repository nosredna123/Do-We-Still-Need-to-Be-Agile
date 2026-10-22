"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const {
  validateRows, filterChoices, selectRows, sortRows, displayCell, loadDataset,
} = require("../assets/app.js");
const site = path.resolve(__dirname, "..");
const catalog = JSON.parse(readFileSync(path.join(site, "data/catalog.json")));
const release = JSON.parse(readFileSync(path.join(site, "data/release.json")));
const rowsFor = dataset => JSON.parse(readFileSync(path.join(site, dataset.paths.json)));
const descriptor = id => catalog.datasets.find(dataset => dataset.id === id);
const clone = value => JSON.parse(JSON.stringify(value));

test("all 49 public datasets satisfy exact schema, types, unique keys and release counts", () => {
  for (const dataset of catalog.datasets) {
    const rows = rowsFor(dataset);
    const record = release.datasets.find(item => item.id === dataset.id);
    assert.doesNotThrow(() => validateRows(rows, dataset, record.row_count), dataset.id);
  }
});

test("rejects missing/extra fields, wrong type, invalid null, infinity, duplicate keys and missing rows", () => {
  const dataset = descriptor("m1-perceptions");
  const original = rowsFor(dataset);
  for (const mutate of [
    rows => { delete rows[0].mean; },
    rows => { rows[0].private = "unexpected"; },
    rows => { rows[0].mean = "2"; },
    rows => { rows[0].mean = Infinity; },
    rows => { rows[0].mean = null; },
    rows => { rows[1] = rows[0]; },
    rows => { rows.pop(); },
    rows => { rows[0].cohort = ""; },
  ]) {
    const rows = clone(original);
    mutate(rows);
    assert.throws(() => validateRows(rows, dataset, original.length));
  }
  assert.throws(() => validateRows([], dataset, original.length));
  assert.throws(() => validateRows({}, dataset, original.length));
});

test("every approved filter uses typed source values and exact row predicates", () => {
  for (const dataset of catalog.datasets) {
    const rows = rowsFor(dataset);
    assert.equal(selectRows(rows, dataset, {}).length, rows.length);
    for (const filter of dataset.filters) {
      const choices = filterChoices(rows, dataset, filter);
      assert(choices.length > 0, dataset.id);
      assert.equal(new Set(choices.map(choice => choice.value)).size, choices.length);
      for (const choice of choices) {
        const selected = selectRows(rows, dataset, { [filter.id]: [choice.value] });
        assert.deepEqual(selected, rows.filter(row =>
          JSON.stringify(filter.fields.map(field => row[field])) === choice.value));
        assert(selected.length > 0);
      }
    }
  }
});

test("cohort-plus-team choices never merge repeated team labels", () => {
  const dataset = descriptor("m8-rework-magnitude");
  const rows = rowsFor(dataset);
  const filter = dataset.filters.find(item => item.id === "team_semester");
  const choices = filterChoices(rows, dataset, filter);
  assert.equal(choices.length, 14);
  for (const choice of choices) {
    assert.equal(selectRows(rows, dataset, { team_semester: [choice.value] }).length, 1);
    const [cohort, team] = JSON.parse(choice.value);
    assert(choice.label.includes(cohort) && choice.label.includes(team));
  }
});

test("filter reset is identity; incompatible intersections are empty, not zeros", () => {
  const dataset = descriptor("m8-rework-magnitude");
  const rows = rowsFor(dataset);
  const team = JSON.stringify(["2025.2", rows[0].team_id]);
  assert.deepEqual(selectRows(rows, dataset, { cohort: ['["2026.1"]'], team_semester: [team] }), []);
  assert.deepEqual(selectRows(rows, dataset, {}), rows);
  assert.throws(() => selectRows(rows, dataset, { unknown: '["value"]' }));
  assert.throws(() => selectRows(rows, dataset, { cohort: "malformed" }));
});

test("numeric sort compares numbers, text sort compares text, nulls remain last both ways", () => {
  const columns = [{ id: "n", type: "number" }, { id: "text", type: "string" }];
  const rows = [{ n: 10, text: "Z" }, { n: 2, text: "A" }, { n: null, text: "B" },
    { n: 0, text: "C" }, { n: -1, text: "D" }];
  assert.deepEqual(sortRows(rows, columns[0], "ascending").map(row => row.n), [-1, 0, 2, 10, null]);
  assert.deepEqual(sortRows(rows, columns[0], "descending").map(row => row.n), [10, 2, 0, -1, null]);
  assert.deepEqual(sortRows(rows, columns[1], "ascending").map(row => row.text), ["A", "B", "C", "D", "Z"]);
  assert.deepEqual(rows.map(row => row.n), [10, 2, null, 0, -1]);
  assert.throws(() => sortRows(rows, columns[0], "invalid"));
});

test("equal-value sort is stable and booleans stay typed", () => {
  const rows = [{ flag: true, id: 1 }, { flag: false, id: 2 }, { flag: true, id: 3 }];
  assert.deepEqual(sortRows(rows, { id: "flag", type: "boolean" }, "ascending").map(row => row.id), [2, 1, 3]);
});

test("every shipped column sorts in both directions without changing values or dropping nulls", () => {
  for (const dataset of catalog.datasets) {
    const rows = rowsFor(dataset);
    for (const column of dataset.columns) {
      for (const direction of ["ascending", "descending"]) {
        const result = sortRows(rows, column, direction);
        assert.equal(result.length, rows.length);
        assert(result.every(row => rows.includes(row)));
        let foundNull = false;
        for (const row of result) {
          if (row[column.id] === null) foundNull = true;
          else assert(!foundNull, `${dataset.id}/${column.id}: null must remain last`);
        }
      }
    }
    assert.deepEqual(rows, rowsFor(dataset));
  }
});

test("tables preserve precision, literal text, zeros and explicit unavailable state", () => {
  assert.equal(displayCell(null), "Unavailable");
  for (const value of [0, false, true, 0.15294804436660828, "<img onerror=alert(1)>"]) {
    assert.equal(displayCell(value), String(value));
  }
});

test("published summary filtering selects existing estimates without re-estimation", () => {
  const dataset = descriptor("m9-structural-outcomes");
  const rows = rowsFor(dataset);
  const filter = dataset.filters[0];
  const choice = filterChoices(rows, dataset, filter)[0];
  const selected = selectRows(rows, dataset, { [filter.id]: [choice.value] });
  assert(selected.every(row => rows.includes(row)));
  assert.deepEqual(rows, rowsFor(dataset));
});

test("multiple cohorts and repeated team labels select exact compatible cases without duplicates", () => {
  const dataset = descriptor("m8-rework-magnitude");
  const rows = rowsFor(dataset);
  const cohorts = ['["2025.2"]', '["2026.1"]'];
  const commonTeam = rows.find(row => rows.some(other =>
    other.cohort !== row.cohort && other.team_id === row.team_id)).team_id;
  const teams = cohorts.map(cohort => JSON.stringify([JSON.parse(cohort)[0], commonTeam]));
  const selected = selectRows(rows, dataset, { cohort: cohorts, team_semester: teams });
  assert.equal(selected.length, 2);
  assert(selected.every(row => row.team_id === commonTeam));
  assert.equal(new Set(selected.map(row => row.cohort)).size, 2);
  assert.deepEqual(selectRows(rows, dataset, { cohort: [cohorts[0]], team_semester: teams }),
    selected.filter(row => row.cohort === "2025.2"));
  assert.deepEqual(selectRows(rows, dataset, { cohort: cohorts }), rows);
  assert.deepEqual(selectRows(rows, dataset, { cohort: [], team_semester: [] }), rows);
  assert.deepEqual(rows, rowsFor(dataset));
});

test("every approved multi-value filter uses union within a filter and intersection across filters", () => {
  for (const dataset of catalog.datasets) {
    const rows = rowsFor(dataset);
    const selection = {};
    let expected = rows;
    for (const filter of dataset.filters) {
      const tokens = filterChoices(rows, dataset, filter).slice(0, 2).map(choice => choice.value);
      selection[filter.id] = tokens;
      expected = expected.filter(row => tokens.includes(JSON.stringify(filter.fields.map(field => row[field]))));
      assert.deepEqual(selectRows(rows, dataset, selection), expected, dataset.id);
    }
    assert.deepEqual(rows, rowsFor(dataset));
  }
});

test("multi-case selection rejects malformed, unapproved, duplicate or wrongly typed choices", () => {
  const dataset = descriptor("m8-rework-magnitude");
  const rows = rowsFor(dataset);
  for (const selection of [
    { cohort: '["2025.2"]' },
    { cohort: ["invalid JSON"] },
    { cohort: ['["unmeasured"]'] },
    { cohort: ['[2025.2]'] },
    { cohort: ['["2025.2"]', '["2025.2"]'] },
    { team_semester: ['["TEAM01"]'] },
    { cohort: null },
  ]) assert.throws(() => selectRows(rows, dataset, selection));
});

test("omitted-case selections keep their composite identity and never recalculate fixed estimates", () => {
  const dataset = catalog.datasets.find(item => item.filters.some(filter => filter.id === "omitted_case"));
  const rows = rowsFor(dataset);
  const filter = dataset.filters.find(item => item.id === "omitted_case");
  const tokens = filterChoices(rows, dataset, filter).slice(0, 2).map(choice => choice.value);
  const selected = selectRows(rows, dataset, { omitted_case: tokens });
  assert.deepEqual(selected, rows.filter(row =>
    tokens.includes(JSON.stringify(filter.fields.map(field => row[field])))));
  assert(selected.length > 0 && selected.every(row => rows.includes(row)));
  assert.deepEqual(rows, rowsFor(dataset));
});

test("surveys and global transcripts never offer or accept team filters", () => {
  for (const dataset of catalog.datasets.filter(item =>
    ["surveys", "transcript-aggregates"].includes(item.source) || item.id === "transcript-context-2025")) {
    assert(!dataset.filters.some(filter => filter.fields.some(field => field.includes("team"))), dataset.id);
    assert.throws(() => selectRows(rowsFor(dataset), dataset, {
      team_semester: ['["2025.2","TEAM01"]'],
    }), dataset.id);
  }
});

test("selected dataset fetch is local and validates its actual response", async () => {
  const dataset = descriptor("m8-rework-magnitude");
  const rows = rowsFor(dataset);
  const fetcher = async (url, { signal }) => {
    assert.equal(url, dataset.paths.json);
    assert(signal instanceof AbortSignal);
    return { ok: true, json: async () => rows };
  };
  assert.equal(await loadDataset(dataset, rows.length, fetcher), rows);
  await assert.rejects(loadDataset(dataset, rows.length + 1, fetcher));
  await assert.rejects(loadDataset(dataset, rows.length, async () => ({ ok: false, status: 404 })), /404/);
  await assert.rejects(loadDataset(dataset, rows.length, async () => ({
    ok: true, json: async () => { throw new SyntaxError("Invalid JSON"); },
  })), /Invalid JSON/);
});

test("dataset requests timeout and accept explicit cancellation", async () => {
  const stalled = (_url, { signal }) => new Promise((_resolve, reject) => {
    if (signal.aborted) reject(new Error("cancelled"));
    else signal.addEventListener("abort", () => reject(new Error("cancelled")), { once: true });
  });
  const dataset = descriptor("m1-perceptions");
  await assert.rejects(loadDataset(dataset, 1, stalled, undefined, 5), /timed out/);
  const controller = new AbortController();
  const request = loadDataset(dataset, 1, stalled, controller.signal);
  controller.abort();
  await assert.rejects(request, /cancelled/);
});
