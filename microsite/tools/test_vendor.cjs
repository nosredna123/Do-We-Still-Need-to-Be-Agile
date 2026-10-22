/* Run with node --test tools/test_vendor.cjs; no packages or private inputs. */
"use strict";

const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const { readFileSync, readdirSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { gzipSync } = require("node:zlib");
const site = path.resolve(__dirname, "..");
const directory = path.join(site, "assets/vendor");
const filename = "plotly-cartesian-4.1.2.min.js";

test("the single chart bundle is the exact pinned official Cartesian distribution", () => {
  const bytes = readFileSync(path.join(directory, filename));
  assert.equal(createHash("sha256").update(bytes).digest("hex"),
    "aaf12ff1d4671f7e93f6df4291651ab4ca6b76c0ea5f1576ec1030e3c2819a20");
  assert.equal(bytes.length, 1507990);
  assert(bytes.subarray(0, 150).toString().includes("v4.1.2"));
  assert(gzipSync(bytes, { level: 9 }).length < 510000,
    "Pinned bundle should remain approximately 0.50 MB compressed; exact gzip output can vary with zlib.");
  assert.deepEqual(readdirSync(directory).filter(name => name.endsWith(".js")), [filename]);
});

test("the upstream MIT license and bundled notices are retained locally", () => {
  const licenseBytes = readFileSync(path.join(directory, "LICENSE-plotly-4.1.2.txt"));
  assert.equal(createHash("sha256").update(licenseBytes).digest("hex"),
    "8c45d9eaf50c2f72dd9c7ab9ef440788ba58a3538484b5c51c1f17d5128752e7");
  const license = licenseBytes.toString("utf8");
  for (const phrase of ["MIT License", "Copyright (c) 2016-2024 Plotly Technologies Inc.",
    "Permission is hereby granted, free of charge", "THE SOFTWARE IS PROVIDED \"AS IS\""]) {
    assert(license.includes(phrase), phrase);
  }
  const bundle = readFileSync(path.join(directory, filename), "utf8");
  assert(bundle.startsWith("/**\n* plotly.js (cartesian - minified) v4.1.2"));
  assert(bundle.includes("Licensed under the MIT license"));
});

test("application script references are local existing files, never CDN imports", () => {
  const html = readFileSync(path.join(site, "index.html"), "utf8");
  for (const match of html.matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)) {
    assert(/^assets\/[a-zA-Z0-9/_.-]+\.js$/.test(match[1]), match[1]);
    assert(!match[1].split("/").includes(".."));
    assert(readFileSync(path.join(site, match[1])).length > 0);
  }
});
