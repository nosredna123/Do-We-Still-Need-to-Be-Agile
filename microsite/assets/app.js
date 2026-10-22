(() => {
  "use strict";

  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }

  const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
  const text = value => typeof value === "string" && value.trim().length > 0;
  const strings = value => Array.isArray(value) && value.length > 0 && value.every(text);
  const unique = values => new Set(values).size === values.length;
  const count = value => Number.isSafeInteger(value) && value >= 0;

  function metadataTree(value) {
    return value === null || typeof value === "string" || typeof value === "boolean" ||
      (typeof value === "number" && Number.isFinite(value)) ||
      (Array.isArray(value) && value.every(metadataTree)) ||
      (object(value) && Object.values(value).every(metadataTree));
  }

  function validateMetadata(catalog, release) {
    requireValue(object(catalog) && catalog.schema_version === "1.0" &&
      catalog.language === "en" && catalog.path_base === "site_root" &&
      catalog.status === "snapshot_prepared_release_pending" &&
      catalog.excerpt_policy === "omitted_by_human_decision", "Unsupported catalog format or publication policy.");
    requireValue(Array.isArray(catalog.research_questions) && catalog.research_questions.length === 3 &&
      catalog.research_questions.every((rq, i) => object(rq) && rq.id === `RQ${i + 1}` &&
        text(rq.title) && strings(rq.metrics)), "Invalid research-question metadata.");
    const metrics = catalog.research_questions.flatMap(rq => rq.metrics);
    requireValue(unique(metrics) && metrics.length === 9 &&
      metrics.every(metric => /^M[1-9]$/.test(metric)), "Invalid metric navigation.");
    requireValue(Array.isArray(catalog.sources) && catalog.sources.length > 0 &&
      catalog.sources.every(source => object(source) && text(source.id) && text(source.label)) &&
      unique(catalog.sources.map(source => source.id)), "Invalid evidence-source metadata.");
    requireValue(Array.isArray(catalog.datasets) && catalog.datasets.length > 0 &&
      unique(catalog.datasets.map(dataset => dataset?.id)), "Invalid or duplicate dataset inventory.");
    for (const dataset of catalog.datasets) {
      requireValue(object(dataset) && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(dataset.id) &&
        ["title", "grain", "definition", "denominator", "estimation_population"].every(key => text(dataset[key])) &&
        strings(dataset.metrics) && unique(dataset.metrics) &&
        catalog.research_questions.some(rq => rq.id === dataset.rq) &&
        dataset.metrics.every(metric => metrics.includes(metric)) &&
        catalog.sources.some(source => source.id === dataset.source), "Invalid dataset navigation or definition.");
      requireValue(object(dataset.paths) &&
        dataset.paths.json === `data/datasets/${dataset.id}.json` &&
        dataset.paths.csv === `data/downloads/${dataset.id}.csv`, "Dataset paths must stay local.");
      requireValue(Array.isArray(dataset.columns) && dataset.columns.length > 0 &&
        dataset.columns.every(column => object(column) &&
          ["id", "label", "unit", "definition"].every(key => text(column[key])) &&
          ["string", "integer", "number", "boolean"].includes(column.type) &&
          typeof column.nullable === "boolean") &&
        unique(dataset.columns.map(column => column.id)) &&
        strings(dataset.key) && unique(dataset.key) &&
        dataset.key.every(key => dataset.columns.some(column => column.id === key)), "Invalid dataset column definitions.");
      requireValue(object(dataset.coverage) && object(dataset.missingness) &&
        strings(dataset.limitations) && metadataTree(dataset.coverage) &&
        metadataTree(dataset.missingness), "Invalid dataset coverage or missingness.");
      requireValue(Array.isArray(dataset.filters) && unique(dataset.filters.map(filter => filter?.id)) &&
        dataset.filters.every(filter => object(filter) && text(filter.id) && text(filter.label) &&
          filter.mode === "multi_select" && strings(filter.fields) && unique(filter.fields) &&
          filter.fields.every(field => dataset.columns.some(column => column.id === field)) &&
          (!filter.fields.includes("team_id") || JSON.stringify(filter.fields) === '["cohort","team_id"]') &&
          (!filter.fields.includes("omitted_team_id") ||
            JSON.stringify(filter.fields) === '["omitted_cohort","omitted_team_id"]')) &&
        ["select_rows_only", "select_observations"].includes(dataset.filter_effect),
      "Invalid grain-specific filters.");
    }
    requireValue(object(catalog.methods) && metadataTree(catalog.methods) &&
      Array.isArray(catalog.methods.definition_sets) && catalog.methods.definition_sets.length > 0 &&
      catalog.methods.definition_sets.every(set => object(set) && text(set.id) && strings(set.key) &&
        Array.isArray(set.rows) && set.rows.length > 0 &&
        set.rows.every(row => object(row) && set.key.every(key => text(row[key])) &&
          Object.values(row).every(value => value === null || ["string", "boolean", "number"].includes(typeof value)))),
    "Invalid methods definitions.");
    requireValue(object(release) && release.schema_version === "1.0" && text(release.snapshot_id) &&
      release.status === catalog.status && release.path_base === "site_root" &&
      release.hash_algorithm === "sha256" && text(release.artifact_scope) &&
      text(release.coverage_note) && object(release.summary) &&
      Array.isArray(release.datasets) && Array.isArray(release.artifacts), "Invalid snapshot metadata.");
    requireValue(release.summary.dataset_count === catalog.datasets.length &&
      release.datasets.length === catalog.datasets.length && unique(release.datasets.map(dataset => dataset?.id)) &&
      release.datasets.every(dataset => object(dataset) && count(dataset.row_count) &&
        dataset.row_count > 0 && count(dataset.column_count) &&
        catalog.datasets.some(descriptor => descriptor.id === dataset.id &&
          descriptor.columns.length === dataset.column_count)), "Snapshot dataset counts disagree with catalog.");
    const paths = ["data/catalog.json", ...catalog.datasets.flatMap(dataset => Object.values(dataset.paths))];
    requireValue(release.artifacts.length === paths.length &&
      release.summary.artifact_count === paths.length &&
      unique(release.artifacts.map(artifact => artifact?.path)), "Snapshot artifact inventory is invalid.");
    for (const artifact of release.artifacts) {
      requireValue(object(artifact) && paths.includes(artifact.path) &&
        /^[0-9a-f]{64}$/.test(artifact.sha256) && count(artifact.bytes) && artifact.bytes > 0,
      "Snapshot artifact fingerprint is invalid.");
      if (artifact.path !== "data/catalog.json") {
        const descriptor = catalog.datasets.find(dataset => Object.values(dataset.paths).includes(artifact.path));
        const dataset = release.datasets.find(item => item.id === descriptor.id);
        requireValue(artifact.row_count === dataset.row_count, "Snapshot artifact row count disagrees.");
      }
    }
    requireValue(release.summary.observation_row_count === release.datasets.reduce((n, dataset) => n + dataset.row_count, 0) &&
      release.summary.scalar_cell_count === release.datasets.reduce((n, dataset) =>
        n + dataset.row_count * dataset.column_count, 0), "Snapshot row or scalar totals disagree.");
  }

  function matchingDatasets(catalog, rq = "", metric = "", source = "") {
    return catalog.datasets.filter(dataset => (!rq || dataset.rq === rq) &&
      (!metric || dataset.metrics.includes(metric)) && (!source || dataset.source === source));
  }

  function matchesDefinition(dataset, query) {
    const content = [dataset.title, dataset.rq, ...dataset.metrics, dataset.definition, dataset.grain,
      ...dataset.columns.flatMap(column => [column.id, column.label, column.definition, column.unit])].join(" ");
    return content.toLowerCase().includes(query.trim().toLowerCase());
  }

  function validateRows(rows, dataset, expectedCount) {
    requireValue(Array.isArray(rows) && rows.length === expectedCount && rows.length > 0,
      "Dataset row count disagrees with the frozen snapshot.");
    const names = dataset.columns.map(column => column.id);
    const keys = new Set();
    for (const row of rows) {
      requireValue(object(row) && JSON.stringify(Object.keys(row)) === JSON.stringify(names),
        "Dataset columns disagree with the catalog.");
      for (const column of dataset.columns) {
        const value = row[column.id];
        const valid = value === null ? column.nullable :
          column.type === "integer" ? Number.isSafeInteger(value) :
          column.type === "number" ? typeof value === "number" && Number.isFinite(value) :
          typeof value === column.type;
        requireValue(valid, `Invalid value for ${column.id}; expected ${column.type}${column.nullable ? " or null" : ""}.`);
      }
      const identity = dataset.key.map(key => row[key]);
      const serialized = JSON.stringify(identity);
      requireValue(identity.every(value => value !== null && value !== "") && !keys.has(serialized),
        "Dataset has a missing or duplicate analytical key.");
      keys.add(serialized);
    }
  }

  function displayCell(value) {
    return value === null ? "Unavailable" : String(value);
  }

  function compareValues(left, right, type) {
    if (left === right) return 0;
    if (left === null) return 1;
    if (right === null) return -1;
    if (type === "number" || type === "integer" || type === "boolean") return left < right ? -1 : 1;
    return String(left).localeCompare(String(right), "en");
  }

  function filterChoices(rows, dataset, filter) {
    const choices = new Map();
    for (const row of rows) {
      const values = filter.fields.map(field => row[field]);
      const value = JSON.stringify(values);
      if (!choices.has(value)) {
        const labels = values.map((cell, index) => {
          const column = dataset.columns.find(item => item.id === filter.fields[index]);
          const translated = column.value_labels?.[cell];
          return translated ? `${translated} (${displayCell(cell)})` : displayCell(cell);
        });
        choices.set(value, { value, label: labels.join(" / "), values });
      }
    }
    return [...choices.values()].sort((a, b) => {
      for (let index = 0; index < filter.fields.length; index += 1) {
        const column = dataset.columns.find(item => item.id === filter.fields[index]);
        const order = column.value_order;
        let compared;
        if (order && order.includes(a.values[index]) && order.includes(b.values[index])) {
          compared = order.indexOf(a.values[index]) - order.indexOf(b.values[index]);
        } else {
          compared = compareValues(a.values[index], b.values[index], column.type);
        }
        if (compared) return compared;
      }
      return 0;
    });
  }

  function selectRows(rows, dataset, selection) {
    const predicates = Object.entries(selection).map(([id, values]) => {
      const filter = dataset.filters.find(item => item.id === id);
      requireValue(filter && Array.isArray(values) && values.every(value => typeof value === "string") &&
        unique(values), "Invalid filter selection.");
      const approved = new Set(filterChoices(rows, dataset, filter).map(choice => choice.value));
      requireValue(values.every(value => approved.has(value)), "Unknown or wrongly typed filter choice.");
      const chosen = new Set(values);
      return row => !chosen.size || chosen.has(JSON.stringify(filter.fields.map(field => row[field])));
    });
    return rows.filter(row => predicates.every(predicate => predicate(row)));
  }

  function sortRows(rows, column, direction) {
    requireValue(["ascending", "descending"].includes(direction), "Invalid sort direction.");
    return rows.map((row, index) => ({ row, index })).sort((a, b) => {
      const left = a.row[column.id];
      const right = b.row[column.id];
      let compared = compareValues(left, right, column.type);
      if (direction === "descending" && left !== null && right !== null) compared = -compared;
      return compared || a.index - b.index;
    }).map(item => item.row);
  }

  function selectedRows(rows, dataset, selection, sort) {
    const visible = selectRows(rows, dataset, selection);
    if (!sort) return visible;
    const column = dataset.columns.find(item => item.id === sort.field);
    requireValue(column, "Invalid export/table sort field.");
    return sortRows(visible, column, sort.direction);
  }

  function csvText(rows, dataset) {
    requireValue(Array.isArray(rows), "Invalid export rows.");
    if (rows.length) validateRows(rows, dataset, rows.length);
    const quote = value => {
      requireValue(!/^ *[\t\r\n]/u.test(value) && !/^[\s\u0085\u001c-\u001f]*[=+\-@]/u.test(value),
        "Spreadsheet-unsafe text requires reviewed export handling; no CSV was created.");
      return `"${value.replaceAll('"', '""')}"`;
    };
    const header = dataset.columns.map(column => quote(column.id)).join(",");
    const lines = rows.map(row => dataset.columns.map(column => {
      const value = row[column.id];
      if (typeof value === "string") {
        requireValue(value !== "" || !column.nullable,
          "Empty nullable text is ambiguous with CSV null; use the typed JSON instead.");
        return quote(value);
      }
      return value === null ? "" : String(value);
    }).join(","));
    return [header, ...lines].join("\n") + "\n";
  }

  function prepareExport(dataset, rows, selection, sort, snapshotId) {
    requireValue(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(dataset.id) && text(snapshotId), "Invalid export identity.");
    const visible = selectedRows(rows, dataset, selection, sort);
    const csv = csvText(visible, dataset);
    return {
      filename: `${dataset.id}-filtered.csv`,
      csv,
      metadata: {
        schema_version: "1.0", snapshot_id: snapshotId, dataset_id: dataset.id,
        csv_filename: `${dataset.id}-filtered.csv`, title: dataset.title,
        selected_row_count: visible.length, total_row_count: rows.length,
        filters: JSON.parse(JSON.stringify(selection)), sort: sort ? { ...sort } : null,
        filter_definitions: dataset.filters.map(filter => ({ ...filter, fields: [...filter.fields] })),
        filter_value_encoding: "Each choice is a JSON-encoded array of typed values in the filter's fields order. Choices within a filter use OR; filters use AND; absent or empty choices mean all.",
        column_order: dataset.columns.map(column => column.id),
        columns: dataset.columns.map(column => ({ ...column })),
        grain: dataset.grain, key: [...dataset.key], denominator: dataset.denominator,
        filter_effect: dataset.filter_effect, estimation_population: dataset.estimation_population,
        missingness: dataset.missingness, coverage: dataset.coverage, limitations: dataset.limitations,
        csv_encoding: "UTF-8 without BOM; comma-separated; LF records; quoted strings and doubled double quotes.",
        csv_null_encoding: "An empty unquoted cell means null (Unavailable), never numeric zero or false. Use column types and status fields.",
        spreadsheet_safety: "Formula-leading text is rejected, not altered. Import using the supplied column types; spreadsheet auto-conversion can lose precision.",
        numeric_encoding: "Finite numbers use round-trip JavaScript decimal notation, without display rounding. Original numeric values are retained.",
        scope: "Exactly the displayed observation rows in current sort order, not chart legend visibility or other panels. No estimates are recalculated.",
      },
    };
  }

  async function fetchJSON(path, signal, fetcher = fetch) {
    const response = await fetcher(path, { signal, cache: "no-cache" });
    requireValue(response.ok, `${path} returned HTTP ${response.status}.`);
    return response.json();
  }

  async function loadDataset(dataset, expectedCount, fetcher = fetch, signal, timeout = 15000) {
    const controller = new AbortController();
    const cancel = () => controller.abort();
    if (signal?.aborted) cancel();
    else signal?.addEventListener("abort", cancel, { once: true });
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, timeout);
    try {
      const rows = await fetchJSON(dataset.paths.json, controller.signal, fetcher);
      validateRows(rows, dataset, expectedCount);
      return rows;
    } catch (error) {
      if (timedOut) throw new Error("Dataset request timed out. Check the local server and retry.");
      throw error;
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener("abort", cancel);
    }
  }

  async function loadMetadata(fetcher = fetch, timeout = 15000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const [catalog, release] = await Promise.all(["data/catalog.json", "data/release.json"]
        .map(path => fetchJSON(path, controller.signal, fetcher)));
      validateMetadata(catalog, release);
      return { catalog, release };
    } catch (error) {
      if (controller.signal.aborted) throw new Error("Metadata request timed out. Check the local server and retry.");
      throw error;
    } finally {
      clearTimeout(timer);
      controller.abort();
    }
  }

  function start() {
    const byId = id => document.getElementById(id);
    const navigation = byId("dataset-navigation");
    const rq = byId("rq-select");
    const metric = byId("metric-select");
    const source = byId("source-select");
    const datasetSelect = byId("dataset-select");
    const status = byId("explorer-status");
    const errorMessage = byId("metadata-error");
    const retry = byId("metadata-retry");
    const detail = byId("dataset-details");
    const snapshot = byId("snapshot-details");
    const definitions = byId("definition-results");
    const search = byId("definition-search");
    const figures = window.ResearchCharts?.createViewer(loadDataset, chooseFigureDataset);
    let catalog;
    let release;
    const rowControls = byId("row-controls");
    const filterContainer = byId("row-filters");
    const rowStatus = byId("row-status");
    const rowError = byId("row-error");
    const rowRetry = byId("row-retry");
    const tableContainer = byId("dataset-table");
    const fullDownloads = byId("full-downloads");
    const filteredDownloads = byId("filtered-downloads");
    const exportStatus = byId("export-status");
    const exportError = byId("export-error");
    let exportUrls = [];
    let activeDataset;
    let rows = [];
    let selection = {};
    let sort = null;
    let rowRequest = null;
    let requestVersion = 0;

    function element(tag, value) {
      const node = document.createElement(tag);
      if (value !== undefined) node.textContent = String(value);
      return node;
    }

    function label(key) {
      return key.replaceAll("_", " ");
    }

    function tree(value) {
      if (!object(value) && !Array.isArray(value)) return element("span", value === null ? "Unavailable" : value);
      const list = element(Array.isArray(value) ? "ul" : "dl");
      for (const [key, item] of Object.entries(value)) {
        if (Array.isArray(value)) {
          const entry = element("li");
          entry.append(tree(item));
          list.append(entry);
        } else {
          const entry = element("dd");
          entry.append(tree(item));
          list.append(element("dt", label(key)), entry);
        }
      }
      return list;
    }

    function options(select, values, allLabel) {
      const previous = select.value;
      select.replaceChildren();
      if (allLabel) select.append(new Option(allLabel, ""));
      for (const [value, title] of values) select.append(new Option(title, value));
      if ([...select.options].some(option => option.value === previous)) select.value = previous;
      select.disabled = select.options.length === 0;
    }

    function showDataset() {
      detail.replaceChildren();
      const dataset = catalog.datasets.find(item => item.id === datasetSelect.value);
      if (!dataset) {
        clearRows();
        status.textContent = "No datasets match this navigation selection. Change the research question, metric, or source.";
        return;
      }
      const title = element("h3", dataset.title);
      const sourceLabel = catalog.sources.find(item => item.id === dataset.source).label;
      detail.append(title, element("p", `${dataset.rq} / ${dataset.metrics.join(", ")} / ${sourceLabel}`),
        element("p", dataset.definition),
        tree({ grain: dataset.grain, key: dataset.key, denominator: dataset.denominator,
          coverage: dataset.coverage, missingness: dataset.missingness,
          estimation_population: dataset.estimation_population, limitations: dataset.limitations }));
      const fields = element("details");
      fields.append(element("summary", `Column definitions and units (${dataset.columns.length})`));
      for (const column of dataset.columns) {
        fields.append(element("h4", `${column.label} (${column.id})`),
          element("p", `${column.definition} Unit: ${column.unit}. Type: ${column.type}. ` +
            `Null allowed: ${column.nullable ? "yes" : "no"}.`));
        if (column.value_labels) fields.append(tree(column.value_labels));
        if (column.value_order) fields.append(tree({ value_order: column.value_order }));
      }
      detail.append(fields, element("p", "Mapped paper figures below follow this dataset's permitted row filters. " +
        "Original populations, Ns and thresholds remain fixed. Downloads below distinguish full and displayed rows."));
      const available = datasetSelect.options.length;
      status.textContent = `${available} ${available === 1 ? "dataset" : "datasets"} available in this navigation selection. ` +
        `Showing definitions for ${dataset.title}.`;
      showRows(dataset);
    }

    function clearRows() {
      clearExports();
      fullDownloads.replaceChildren();
      figures?.setSelection(null);
      requestVersion += 1;
      rowRequest?.abort();
      rowRequest = null;
      rows = [];
      selection = {};
      sort = null;
      activeDataset = null;
      rowControls.disabled = true;
      rowRetry.hidden = true;
      filterContainer.replaceChildren();
      tableContainer.replaceChildren();
      rowError.textContent = "";
      rowStatus.textContent = "Select a dataset to load its observations.";
      rowStatus.setAttribute("aria-busy", "false");
      byId("active-filters").textContent = "No active row filters.";
      byId("row-scope").textContent = "";
    }

    function clearExports() {
      for (const url of exportUrls) URL.revokeObjectURL(url);
      exportUrls = [];
      filteredDownloads.replaceChildren();
      byId("export-retry").hidden = true;
      exportError.textContent = "";
      exportStatus.textContent = "Filtered downloads are available after observations load successfully.";
    }

    function renderExports() {
      clearExports();
      try {
        const result = prepareExport(activeDataset, rows, selection, sort, release.snapshot_id);
        for (const [content, type, filename, title] of [
          [result.csv, "text/csv;charset=utf-8", result.filename, "Download displayed rows (CSV)"],
          [JSON.stringify(result.metadata, null, 2) + "\n", "application/json;charset=utf-8",
            `${activeDataset.id}-filtered-metadata.json`, "Download matching export scope and column definitions (JSON)"],
        ]) {
          const url = URL.createObjectURL(new Blob([content], { type }));
          exportUrls.push(url);
          const link = element("a", title);
          link.href = url;
          link.download = filename;
          const entry = element("p");
          entry.append(link);
          filteredDownloads.append(entry);
        }
        exportStatus.textContent = `${result.metadata.selected_row_count} of ${rows.length} rows ready for ${activeDataset.title}. ` +
          `Snapshot: ${release.snapshot_id}. ${byId("active-filters").textContent} ` +
          (sort ? `Sort: ${sort.field}, ${sort.direction}.` : "Original source order.") +
          (result.metadata.selected_row_count ? "" : " CSV contains column headers only; no rows match.");
      } catch (error) {
        clearExports();
        exportStatus.textContent = "Filtered export could not be prepared. Observation tables remain available.";
        exportError.textContent = `Export error: ${error instanceof Error ? error.message : String(error)} ` +
          "Check the data and export policy, or retry preparing the export.";
        byId("export-retry").hidden = false;
        console.error("Research explorer export preparation failed:", error);
      }
    }

    function renderRows() {
      const visible = selectedRows(rows, activeDataset, selection, sort);
      rowStatus.textContent = `${visible.length} of ${rows.length} rows shown. ` +
        (visible.length ? "Values retain their original precision." : "No rows match these filters. Change a filter or reset.");
      const summaries = Object.entries(selection).map(([id, values]) => {
        const filter = activeDataset.filters.find(item => item.id === id);
        const choices = filterChoices(rows, activeDataset, filter);
        return `${filter.label}: ${values.map(value =>
          choices.find(item => item.value === value).label).join(" or ")}`;
      });
      byId("active-filters").textContent = summaries.length
        ? `Active row filters: ${summaries.join("; ")}` : "No active row filters.";
      renderExports();
      figures?.setSelection({ id: activeDataset.id, rows: visible,
        summary: summaries.length ? `Active row filters: ${summaries.join("; ")}` : "No active row filters" });
      tableContainer.replaceChildren();
      if (!visible.length) return;
      const table = element("table");
      const caption = element("caption", `${activeDataset.title}: ${visible.length} of ${rows.length} rows. ` +
        `Grain: ${activeDataset.grain}. Unavailable means null, not zero.`);
      table.append(caption);
      const head = element("thead");
      const headerRow = element("tr");
      for (const column of activeDataset.columns) {
        const header = element("th");
        header.scope = "col";
        const direction = sort?.field === column.id ? sort.direction : "none";
        header.setAttribute("aria-sort", direction);
        const button = element("button", `${column.label} (${column.unit})` +
          (direction === "none" ? "" : ` [${direction}]`));
        button.type = "button";
        button.dataset.sortField = column.id;
        button.setAttribute("aria-label", `Sort by ${column.label}, ` +
          `${direction === "ascending" ? "descending" : "ascending"}; ${column.unit}`);
        button.addEventListener("click", () => {
          sort = { field: column.id, direction: direction === "ascending" ? "descending" : "ascending" };
          renderRows();
          [...tableContainer.querySelectorAll("button")].find(item => item.dataset.sortField === column.id).focus();
        });
        header.append(button);
        headerRow.append(header);
      }
      head.append(headerRow);
      table.append(head);
      const body = element("tbody");
      for (const row of visible) {
        const entry = element("tr");
        for (const column of activeDataset.columns) {
          const value = row[column.id];
          const cell = element("td", displayCell(value));
          if (value !== null && ["number", "integer"].includes(column.type)) cell.className = "numeric";
          if (value === null) {
            cell.className = "unavailable";
            const reason = row.ratio_status || row.measurement_status;
            cell.title = reason ? `Unavailable (${reason}); see dataset missingness.` : column.definition;
          }
          entry.append(cell);
        }
        body.append(entry);
      }
      table.append(body);
      tableContainer.append(table);
    }

    async function showRows(dataset) {
      clearRows();
      if (!dataset) return;
      activeDataset = dataset;
      for (const [kind, title] of [["csv", "Full dataset (CSV)"], ["json", "Full dataset (typed JSON)"]]) {
        const link = element("a", title);
        link.href = dataset.paths[kind];
        link.download = `${dataset.id}.${kind}`;
        const entry = element("p");
        entry.append(link);
        fullDownloads.append(entry);
      }
      const version = requestVersion;
      rowRequest = new AbortController();
      rowStatus.textContent = `Loading observations for ${dataset.title}...`;
      rowStatus.setAttribute("aria-busy", "true");
      byId("row-scope").textContent = dataset.filter_effect === "select_rows_only"
        ? "Filters select existing published rows only. Original populations, denominators, sample sizes and estimates remain fixed; nothing is recalculated."
        : "Filters select existing observations at the stated grain. No new estimates or thresholds are calculated.";
      if (!dataset.filters.some(filter => filter.id === "team_semester")) {
        byId("row-scope").append(" No team-semester observation filter is available for this dataset; only its approved filters are offered.");
      }
      try {
        const expected = release.datasets.find(item => item.id === dataset.id).row_count;
        const loaded = await loadDataset(dataset, expected, fetch, rowRequest.signal);
        if (version !== requestVersion) return;
        rows = loaded;
        for (const filter of dataset.filters) {
          const choices = filterChoices(rows, dataset, filter);
          if (filter.fields.includes("cohort") || filter.fields.includes("omitted_cohort")) {
            const group = element("fieldset");
            group.className = "case-filter";
            group.dataset.filterId = filter.id;
            group.append(element("legend", filter.label));
            const hint = element("p", "Select any number. None selected means all.");
            hint.id = `filter-${filter.id}-hint`;
            group.append(hint);
            const list = element("div");
            list.className = "case-choices";
            group.setAttribute("aria-describedby", hint.id);
            for (const choice of choices) {
              const title = element("label");
              const control = element("input");
              control.type = "checkbox";
              control.value = choice.value;
              control.addEventListener("change", () => {
                const values = [...list.querySelectorAll("input:checked")].map(input => input.value);
                if (values.length) selection[filter.id] = values;
                else delete selection[filter.id];
                renderRows();
              });
              title.append(control, element("span", choice.label));
              list.append(title);
            }
            group.append(list);
            filterContainer.append(group);
            continue;
          }
          const wrapper = element("div");
          const control = element("select");
          const id = `filter-${filter.id}`;
          control.id = id;
          const title = element("label", filter.label);
          title.htmlFor = id;
          control.append(new Option(`All: ${filter.label}`, ""));
          for (const choice of choices) {
            control.append(new Option(choice.label, choice.value));
          }
          control.addEventListener("change", () => {
            if (control.value) selection[filter.id] = [control.value];
            else delete selection[filter.id];
            renderRows();
          });
          wrapper.append(title, control);
          filterContainer.append(wrapper);
        }
        if (!dataset.filters.length) filterContainer.append(element("p", "This dataset has no approved row filters."));
        rowControls.disabled = false;
        renderRows();
      } catch (error) {
        if (version !== requestVersion) return;
        rows = [];
        tableContainer.replaceChildren();
        filterContainer.replaceChildren();
        rowControls.disabled = true;
        rowStatus.textContent = "Observations could not be loaded. No rows are being shown.";
        rowError.textContent = `Dataset error: ${error instanceof Error ? error.message : String(error)} ` +
          "Check the copied data files and retry, or choose another dataset.";
        rowRetry.hidden = false;
        console.error("Research explorer dataset load failed:", error);
      } finally {
        if (version === requestVersion) rowStatus.setAttribute("aria-busy", "false");
      }
    }

    function chooseFigureDataset(id) {
      rq.value = "";
      metric.value = "";
      source.value = "";
      options(metric, catalog.research_questions.flatMap(item => item.metrics).map(value => [value, value]), "All metrics");
      options(source, catalog.sources.map(item => [item.id, item.label]), "All evidence sources");
      options(datasetSelect, catalog.datasets.map(dataset => [dataset.id, dataset.title]));
      datasetSelect.value = id;
      showDataset();
    }

    function updateNavigation(level) {
      if (level === "rq") {
        metric.value = "";
        source.value = "";
      }
      if (level === "metric") source.value = "";
      const inQuestion = matchingDatasets(catalog, rq.value);
      const metrics = catalog.research_questions.flatMap(item => item.metrics)
        .filter(id => inQuestion.some(dataset => dataset.metrics.includes(id)));
      options(metric, metrics.map(id => [id, id]), "All metrics");
      const inMetric = matchingDatasets(catalog, rq.value, metric.value);
      options(source, catalog.sources.filter(item => inMetric.some(dataset => dataset.source === item.id))
        .map(item => [item.id, item.label]), "All evidence sources");
      options(datasetSelect, matchingDatasets(catalog, rq.value, metric.value, source.value)
        .map(dataset => [dataset.id, dataset.title]));
      showDataset();
    }

    function renderDefinitions() {
      const query = search.value.trim().toLowerCase();
      definitions.replaceChildren();
      let matches = 0;
      for (const dataset of catalog.datasets) {
        if (!matchesDefinition(dataset, query)) continue;
        const entry = element("details");
        entry.append(element("summary", `${dataset.title} (${dataset.metrics.join(", ")})`),
          element("p", dataset.definition), element("p", `Grain: ${dataset.grain}. Denominator: ${dataset.denominator}`));
        const columns = element("dl");
        for (const column of dataset.columns) {
          columns.append(element("dt", `${column.label} (${column.id})`),
            element("dd", `${column.definition} Unit: ${column.unit}. Type: ${column.type}. ` +
              `Null allowed: ${column.nullable ? "yes" : "no"}.`));
        }
        entry.append(columns);
        definitions.append(entry);
        matches += 1;
      }
      for (const set of catalog.methods.definition_sets) {
        if (query && !JSON.stringify(set).toLowerCase().includes(query)) continue;
        const entry = element("details");
        entry.append(element("summary", label(set.id.replaceAll("-", "_"))), tree(set.rows));
        definitions.append(entry);
        matches += 1;
      }
      byId("definition-status").textContent = matches
        ? `${matches} definition ${matches === 1 ? "group matches" : "groups match"}. Open a group to read its definitions.`
        : "No definitions match. Try a metric, field name, unit, or a different term.";
    }

    async function load() {
      clearRows();
      figures?.clear();
      navigation.disabled = true;
      search.disabled = true;
      retry.hidden = true;
      errorMessage.textContent = "";
      status.textContent = "Loading the local dataset catalog and snapshot metadata...";
      status.setAttribute("aria-busy", "true");
      detail.replaceChildren();
      snapshot.replaceChildren();
      definitions.replaceChildren();
      byId("definition-status").textContent = "Definitions will be available when metadata finishes loading.";
      byId("method-policies").replaceChildren();
      try {
        ({ catalog, release } = await loadMetadata());
        if (figures) figures.configure(catalog, release);
        else {
          byId("figure-error").textContent = "Figure code is unavailable. Check the copied assets/charts.js file and reload. Observation tables remain available.";
          console.error("Research explorer figure code is unavailable.");
        }
        options(rq, catalog.research_questions.map(item => [item.id, `${item.id}: ${item.title}`]), "All research questions");
        const initialQuestion = location.hash.slice(1).toUpperCase();
        if (catalog.research_questions.some(item => item.id === initialQuestion)) rq.value = initialQuestion;
        navigation.disabled = false;
        search.disabled = false;
        updateNavigation("rq");
        snapshot.append(tree({
          snapshot: release.snapshot_id, schema_version: release.schema_version,
          publication_status: "Prepared snapshot; publication approval remains pending.",
          dataset_count: release.summary.dataset_count, exported_rows: release.summary.observation_row_count,
          coverage_note: release.coverage_note, hash_scope: release.artifact_scope,
        }));
        const policies = { ...catalog.methods };
        delete policies.definition_sets;
        byId("method-policies").append(tree(policies));
        renderDefinitions();
      } catch (error) {
        clearRows();
        figures?.clear();
        navigation.disabled = true;
        search.disabled = true;
        detail.replaceChildren();
        snapshot.replaceChildren();
        definitions.replaceChildren();
        byId("method-policies").replaceChildren();
        byId("definition-status").textContent = "Definitions are unavailable because metadata could not be loaded.";
        status.textContent = "Metadata could not be loaded. No dataset is being shown.";
        errorMessage.textContent = `Catalog or snapshot error: ${error instanceof Error ? error.message : String(error)} ` +
          "Check that the copied site is served over HTTP(S) with its data directory, then retry.";
        retry.hidden = false;
        console.error("Research explorer metadata load failed:", error);
      } finally {
        status.setAttribute("aria-busy", "false");
      }
    }

    rq.addEventListener("change", () => updateNavigation("rq"));
    metric.addEventListener("change", () => updateNavigation("metric"));
    source.addEventListener("change", () => updateNavigation("source"));
    datasetSelect.addEventListener("change", showDataset);
    search.addEventListener("input", renderDefinitions);
    retry.addEventListener("click", load);
    rowRetry.addEventListener("click", () => showRows(activeDataset));
    byId("export-retry").addEventListener("click", () => {
      if (activeDataset && rows.length) renderExports();
    });
    window.addEventListener("pagehide", clearExports);
    window.addEventListener("pageshow", event => {
      if (event.persisted && activeDataset && rows.length) renderExports();
    });
    byId("row-reset").addEventListener("click", () => {
      selection = {};
      sort = null;
      for (const control of filterContainer.querySelectorAll("select")) control.value = "";
      for (const control of filterContainer.querySelectorAll('input[type="checkbox"]')) control.checked = false;
      renderRows();
    });
    window.addEventListener("hashchange", () => {
      if (navigation.disabled) return;
      const question = location.hash.slice(1).toUpperCase();
      if (catalog.research_questions.some(item => item.id === question)) {
        rq.value = question;
        updateNavigation("rq");
      }
    });
    for (const link of document.querySelectorAll(".rq-cards a")) {
      link.addEventListener("click", event => {
        if (navigation.disabled || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        rq.value = link.hash.slice(1).toUpperCase();
        updateNavigation("rq");
        location.hash = "explore";
        rq.focus({ preventScroll: true });
      });
    }
    load();
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { validateMetadata, matchingDatasets, matchesDefinition, loadMetadata,
      validateRows, filterChoices, selectRows, sortRows, displayCell, loadDataset, csvText, prepareExport };
  } else {
    start();
  }
})();
