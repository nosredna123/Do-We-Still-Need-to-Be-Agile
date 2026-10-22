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

  async function loadMetadata(fetcher = fetch, timeout = 15000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const [catalog, release] = await Promise.all(["data/catalog.json", "data/release.json"].map(async path => {
        const response = await fetcher(path, { signal: controller.signal, cache: "no-cache" });
        requireValue(response.ok, `${path} returned HTTP ${response.status}.`);
        return response.json();
      }));
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
    let catalog;
    let release;

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
      detail.append(fields, element("p", "Observation tables, filters, figures, and export controls are not implemented yet."));
      const available = datasetSelect.options.length;
      status.textContent = `${available} ${available === 1 ? "dataset" : "datasets"} available in this navigation selection. ` +
        `Showing definitions for ${dataset.title}.`;
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
    module.exports = { validateMetadata, matchingDatasets, matchesDefinition, loadMetadata };
  } else {
    start();
  }
})();
