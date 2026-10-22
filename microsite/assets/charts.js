(() => {
  "use strict";

  const figureIds = ["rq1-perceptions", "rq2-pooled-activity", "rq2-planning-final7",
    "rq2-churn-and-lexical-density", "rq3-artifact-presence", "rq3-planning-rework",
    "rq3-complexity-rework"];
  const mappings = [
    [["m1-perceptions", "error_bar", "checkpoint", "mean"]],
    [["m3-rolling-pooled", "line", "window_end_day", "total_commit_n"]],
    [["planning-final7-commits", "scatter", "planning_scope_log1p_t1", "final7_share_pct"]],
    [["m4-checkpoint-pooled", "bar", "checkpoint", "total_clean_churn"],
      ["m5-marker-density", "line", "checkpoint", "friction_marker_density_per_1k_tokens"]],
    [["m6a-presence-by-cohort", "stacked_bar", "cohort", "team_semester_count"]],
    [["planning-rework-profile", "scatter", "planning_scope_log1p_t1", "clean_rework_churn_t3"]],
    [["complexity-rework-figure", "scatter", "technical_complexity_mean_t3", "clean_rework_churn_t3"]],
  ];
  const cohorts = ["2025.2", "2026.1"];
  const colors = ["#174e86", "#9c410b", "#6c4096", "#00695c", "#845d00", "#933d68"];
  const escape = value => String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  const safe = value => typeof value === "string" ? escape(value) : value;
  const present = value => typeof value === "number" && Number.isFinite(value);
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  const checkpointOrder = rows => [...rows].sort((a, b) => a.checkpoint.localeCompare(b.checkpoint, "en"));
  const symbol = cohort => cohort === "2025.2" ? "circle" : "diamond";
  const config = { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false };

  function buildFigure(catalog, id, datasets, selection) {
    const index = figureIds.indexOf(id);
    const figure = catalog.figures?.find(item => item.id === id);
    check(index >= 0 && figure, "Unsupported paper figure.");
    check(JSON.stringify(figure.panels.map(panel => [panel.dataset, panel.kind, panel.x, panel.y])) ===
      JSON.stringify(mappings[index]), "Unsupported paper figure mapping.");
    const sources = figure.panels.map(panel => {
      const descriptor = catalog.datasets.find(item => item.id === panel.dataset);
      const rows = datasets[panel.dataset];
      check(descriptor && Array.isArray(rows) && rows.length > 0, `Missing figure dataset: ${panel.dataset}.`);
      for (const field of panel.fields) {
        const column = descriptor.columns.find(item => item.id === field);
        check(column, `Unknown figure field: ${field}.`);
        for (const row of rows) {
          const value = row[field];
          check(value === null || (["number", "integer"].includes(column.type)
            ? present(value) : typeof value === column.type), `Invalid figure value: ${field}.`);
        }
      }
      let selected = rows;
      if (selection?.id === descriptor.id) {
        check(Array.isArray(selection.rows) && typeof selection.summary === "string", "Invalid figure row selection.");
        const originals = new Set(rows.map(row => JSON.stringify(row)));
        check(selection.rows.every(row => originals.has(JSON.stringify(row))) &&
          new Set(selection.rows.map(row => JSON.stringify(row))).size === selection.rows.length,
        "Figure selection must contain unchanged original rows.");
        selected = selection.rows;
      }
      return { id: descriptor.id, descriptor, rows: selected, total: rows.length };
    });
    const data = [];
    const excluded = [];
    const layout = {
      font: { family: "system-ui, sans-serif", size: 14, color: "#1f2933" },
      paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
      margin: { l: 90, r: 50, t: 65, b: 100 }, height: 540,
      legend: { orientation: "h", y: -0.25 }, hovermode: "closest",
      xaxis: { zeroline: false, gridcolor: "#e5e7eb" },
      yaxis: { type: "linear", zeroline: true, gridcolor: "#e5e7eb", rangemode: "tozero" },
    };
    const axis = (field, source = sources[0]) => {
      const column = source.descriptor.columns.find(item => item.id === field);
      return { text: `${escape(column.label)} (${escape(column.unit)})` };
    };
    const guide = (x, y) => {
      check(present(x) && present(y), "Invalid frozen median guides.");
      layout.shapes = [
        { type: "line", x0: x, x1: x, yref: "paper", y0: 0, y1: 1,
          line: { dash: "dot", color: "#465565" } },
        { type: "line", xref: "paper", x0: 0, x1: 1, y0: y, y1: y,
          line: { dash: "dash", color: "#465565" } },
      ];
      layout.annotations = [{ x, y: 1, yref: "paper", text: `Original median: ${x}`,
        showarrow: false, yanchor: "bottom" },
      { x: 1, xref: "paper", y, text: `Original median: ${y}`, showarrow: false, xanchor: "right", yanchor: "bottom" }];
    };
    const scatter = (rows, name, x, y, marker) => ({
      type: "scatter", mode: "markers", name: escape(name),
      x: rows.map(row => row[x]), y: rows.map(row => row[y]),
      customdata: rows.map(row => [safe(row.cohort), safe(row.team_id),
        row.baseline_eligible_for_rework_t3 ?? null,
        row.clean_rework_ratio_t3 === null ? "Unavailable" : row.clean_rework_ratio_t3 ?? null,
        safe(row.ratio_status || row.measurement_status || "See dataset definitions")]),
      marker: { size: 13, line: { color: "#ffffff", width: 1.4 }, ...marker },
      hovertemplate: "%{customdata[0]} / %{customdata[1]}<br>x=%{x}<br>y=%{y}" +
        "<br>Baseline eligible=%{customdata[2]}" +
        (rows.some(row => Object.hasOwn(row, "clean_rework_ratio_t3")) ? "<br>Ratio=%{customdata[3]}" : "") +
        "<br>Status=%{customdata[4]}<extra>%{fullData.name}</extra>",
    });
    const usable = (rows, x, y, log = false) => rows.filter(row => {
      let reason;
      if (!present(row[x]) || !present(row[y])) reason = "unavailable coordinate";
      else if (log && row[y] <= 0) reason = row[y] === 0 ? "zero on logarithmic axis" : "negative on logarithmic axis";
      if (reason) excluded.push({ cohort: row.cohort, team_id: row.team_id, reason });
      return !reason;
    });
    const rows = sources[0].rows;
    let explanation = "";
    switch (id) {
      case "rq1-perceptions": {
        const labels = sources[0].descriptor.columns.find(column => column.id === "perception_family").value_labels;
        const families = Object.keys(labels).sort((a, b) => labels[a].localeCompare(labels[b], "en"));
        for (const [ci, cohort] of cohorts.entries()) {
          for (const [fi, family] of families.entries()) {
            const selected = checkpointOrder(rows.filter(row => row.cohort === cohort && row.perception_family === family));
            if (!selected.length) continue;
            const trace = {
              type: "scatter", mode: "lines+markers", name: escape(labels[family]),
              meta: { family }, legendgroup: family, showlegend: !data.some(trace => trace.legendgroup === family),
              xaxis: ci ? "x2" : "x", yaxis: ci ? "y2" : "y",
              x: selected.map(row => safe(row.checkpoint)), y: selected.map(row => row.mean),
              error_y: { type: "data", array: selected.map(row => row.std), visible: true },
              customdata: selected.map(row => [safe(row.cohort), row.response_n, row.std === null ? "Unavailable" : row.std]),
              line: { color: colors[fi] }, marker: { size: 7 }, connectgaps: false,
              hovertemplate: "%{customdata[0]} / %{x}<br>Mean=%{y}<br>SD=%{customdata[2]}" +
                "<br>Responses=%{customdata[1]}<extra>%{fullData.name}</extra>",
            };
            data.push(trace);
            if (selected.some(row => row.std === null)) {
              delete trace.error_y;
              const known = selected.filter(row => present(row.std) && present(row.mean));
              if (known.length) data.push({
                type: "scatter", mode: "markers", name: escape(labels[family]),
                meta: { uncertaintyFor: family }, legendgroup: family, showlegend: false,
                xaxis: trace.xaxis, yaxis: trace.yaxis,
                x: known.map(row => safe(row.checkpoint)), y: known.map(row => row.mean),
                marker: { opacity: 0 }, hoverinfo: "skip",
                error_y: { type: "data", array: known.map(row => row.std), visible: true, color: colors[fi] },
              });
            }
          }
        }
        layout.grid = { rows: 1, columns: 2, pattern: "independent" };
        layout.xaxis = { categoryorder: "array", categoryarray: ["T1", "T2", "T3"], title: { text: "2025.2 checkpoint" } };
        layout.xaxis2 = { ...layout.xaxis, title: { text: "2026.1 checkpoint" } };
        layout.yaxis = { range: [0, 5], title: { text: "Mean score (family scale)" } };
        layout.yaxis2 = { range: [0, 5], matches: "y" };
        const visibleCohorts = cohorts.filter(cohort => rows.some(row => row.cohort === cohort));
        if (visibleCohorts.length === 1) {
          delete layout.grid;
          delete layout.xaxis2;
          delete layout.yaxis2;
          layout.xaxis.title.text = `${visibleCohorts[0]} checkpoint`;
          for (const trace of data) { trace.xaxis = "x"; trace.yaxis = "y"; }
        }
        explanation = "Bars show standard deviations, not confidence intervals. Unavailable SDs have no bar, not a zero-length bar. Coded families use 0-4; autonomy/tool balance retains its 1-5 scale. Axes display 0-5 as in the paper; uncertainty below zero is clipped, not changed. Original response Ns are retained per point.";
        break;
      }
      case "rq2-pooled-activity": {
        const ordered = [...rows].sort((a, b) => a.window_end_day - b.window_end_day);
        data.push({ type: "scatter", mode: "lines+markers", name: "Pooled commits",
          x: ordered.map(row => row.window_end_day), y: ordered.map(row => row.total_commit_n),
          line: { color: colors[0], width: 3 }, connectgaps: false,
          customdata: ordered.map(row => [row.team_semester_n]),
          hovertemplate: "Relative day=%{x}<br>Commits=%{y}<br>Team-semesters=%{customdata[0]}<extra></extra>" });
        layout.xaxis.title = { text: "Window end relative to T3 anchor (days)" };
        layout.yaxis.title = { text: "Commits across all team-semesters" };
        layout.shapes = [{ type: "line", x0: 0, x1: 0, yref: "paper", y0: 0, y1: 1,
          line: { dash: "dash", color: "#465565" } }];
        const peak = ordered.find(row => row.window_end_day === 1);
        if (present(peak?.total_commit_n)) layout.annotations = [{
          x: 1, y: peak.total_commit_n, text: `Peak: ${peak.total_commit_n}`,
          showarrow: true, arrowhead: 2, ax: 55, ay: -32,
        }];
        explanation = "Overlapping seven-day windows are not independent teams. The original fixed pooled population and each row's N remain unchanged; day zero marks T3.";
        break;
      }
      case "rq2-planning-final7": {
        const selected = usable(rows, "planning_scope_log1p_t1", "final7_share_pct");
        const scores = datasets[sources[0].id].map(row => row.evaluator_score_t3).filter(present);
        for (const cohort of cohorts) {
          const subset = selected.filter(row => row.cohort === cohort);
          if (!subset.length) continue;
          const showscale = data.length === 0;
          const trace = scatter(subset, cohort, "planning_scope_log1p_t1", "final7_share_pct", {
            symbol: symbol(cohort), size: subset.map(row => row.marker_size), sizemode: "diameter",
            color: subset.map(row => row.evaluator_score_t3), colorscale: "Viridis",
            cmin: Math.min(...scores), cmax: Math.max(...scores), showscale,
            ...(showscale ? { colorbar: { title: { text: "T3 evaluator score" } } } : {}),
          });
          trace.customdata = subset.map(row => [safe(row.cohort), safe(row.team_id),
            row.evaluator_score_t3, row.abs_delta_score_t3_minus_t1, safe(row.planning_scope_tier)]);
          trace.hovertemplate = "%{customdata[0]} / %{customdata[1]}<br>T1 scope=%{x}<br>Final-seven share=%{y}" +
            "<br>T3 score=%{customdata[2]}<br>Absolute score change=%{customdata[3]}" +
            "<br>Planning tier=%{customdata[4]}<extra></extra>";
          data.push(trace);
        }
        layout.xaxis.title = axis("planning_scope_log1p_t1");
        layout.yaxis = { title: { text: "Final-seven commits (% of project commits)" }, range: [-4, 104], ticksuffix: "%" };
        guide(catalog.methods.planning_high_tier.log_scope_minimum_inclusive, catalog.methods.concentration_medians_pct.commits);
        explanation = "Original cohort symbols, T3 evaluator-score color, and stored marker diameters encode absolute score change. Original full-population median guides remain fixed; no subset thresholds or new estimates are calculated.";
        break;
      }
      case "rq2-churn-and-lexical-density": {
        const clean = checkpointOrder(rows);
        const lexical = checkpointOrder(sources[1].rows);
        data.push({ type: "bar", name: "M4 clean churn", x: clean.map(row => safe(row.checkpoint)),
          y: clean.map(row => row.total_clean_churn), marker: { color: colors[1] },
          customdata: clean.map(row => [row.team_semester_n]),
          hovertemplate: "%{x}<br>Clean churn=%{y} lines<br>Team-semesters=%{customdata[0]}<extra></extra>" });
        data.push({ type: "scatter", mode: "lines+markers", name: "M5 lexical density", xaxis: "x2", yaxis: "y2",
          x: lexical.map(row => safe(row.checkpoint)), y: lexical.map(row => row.friction_marker_density_per_1k_tokens),
          line: { color: "#00695c", width: 3 }, connectgaps: false,
          customdata: lexical.map(row => [row.token_n, row.transcript_chunk_n]),
          hovertemplate: "%{x}<br>Markers per 1,000 tokens=%{y}<br>Tokens=%{customdata[0]}" +
            "<br>Transcript chunks=%{customdata[1]}<extra></extra>" });
        layout.grid = { rows: 1, columns: 2, pattern: "independent" };
        layout.xaxis = { title: { text: "M4 checkpoint" }, categoryorder: "array", categoryarray: ["T1", "T2", "T3"] };
        layout.xaxis2 = { ...layout.xaxis, title: { text: "M5 checkpoint" } };
        layout.yaxis.title = { text: "Clean churn (lines)" };
        layout.yaxis2 = { title: { text: "Markers per 1,000 tokens" }, rangemode: "tozero" };
        explanation = "Independent panels: M4 is fixed pooled source/test changed lines, not all churn or defects; M5 is one global 2025.2 corpus, not individual teams or an unmeasured cohort. Original team Ns, token counts and corpus coverage remain distinct.";
        break;
      }
      case "rq3-artifact-presence": {
        const states = ["Artifact observed", "No repository artifact observed"];
        for (const [i, state] of states.entries()) {
          const selected = [...rows.filter(row => row.evidence_state === state)].sort((a, b) => a.cohort.localeCompare(b.cohort));
          if (!selected.length) continue;
          data.push({ type: "bar", name: state, x: selected.map(row => safe(row.cohort)),
            y: selected.map(row => row.team_semester_count), text: selected.map(row => row.team_semester_count),
            textposition: "inside", marker: { color: i ? "#718096" : colors[0] },
            customdata: selected.map(row => [row.team_semester_n]),
            hovertemplate: "%{x}<br>Count=%{y}<br>Cohort N=%{customdata[0]}<extra>%{fullData.name}</extra>" });
        }
        layout.barmode = "stack";
        layout.xaxis = { type: "category", title: { text: "Cohort" } };
        layout.yaxis.title = { text: "Team-semesters (count)" };
        explanation = "Observed artifact-state counts, not percentages or planning-quality scores. Original cohort sizes are 9 and 5; no repository artifact observed does not imply no planning.";
        break;
      }
      case "rq3-planning-rework": {
        const selected = usable(rows, "planning_scope_log1p_t1", "clean_rework_churn_t3", true);
        for (const [i, cohort] of cohorts.entries()) {
          for (const eligible of [true, false]) {
            const subset = selected.filter(row => row.cohort === cohort && row.baseline_eligible_for_rework_t3 === eligible);
            if (subset.length) data.push(scatter(subset, `${cohort} / ${eligible ? "Baseline eligible" : "Baseline not observed"}`,
              "planning_scope_log1p_t1", "clean_rework_churn_t3",
              { color: colors[i], symbol: eligible ? "circle" : "diamond", size: 11 }));
          }
        }
        layout.xaxis.title = axis("planning_scope_log1p_t1");
        layout.yaxis = { type: "log", title: { text: "T3 clean rework magnitude (lines, log axis)" } };
        const zeroCount = excluded.filter(item => item.reason === "zero on logarithmic axis").length;
        explanation = `${zeroCount} zero magnitudes are excluded from the log plot and retained unchanged in the source table. No zero-to-one substitution. Magnitude is not a baseline-eligible ratio; eligibility is encoded separately by circle/diamond, not used to discard nonzero magnitudes.`;
        break;
      }
      case "rq3-complexity-rework": {
        const selected = usable(rows, "technical_complexity_mean_t3", "clean_rework_churn_t3");
        for (const [i, tier] of ["high_repository_visible_planning", "lower_repository_visible_planning"].entries()) {
          for (const cohort of cohorts) {
            const subset = selected.filter(row => row.cohort === cohort && row.planning_scope_tier === tier);
            if (subset.length) data.push(scatter(subset, `${i ? "Lower" : "High"} planning / ${cohort}`,
              "technical_complexity_mean_t3", "clean_rework_churn_t3",
              { color: colors[i], symbol: symbol(cohort), size: 15 }));
          }
        }
        layout.xaxis.title = { text: "Evaluator technical complexity at T3 (score points)" };
        layout.yaxis.title = { text: "T3 clean rework magnitude (changed lines)" };
        // Frozen medians from the original 14-case figure; never recompute after selection.
        guide(catalog.methods.complexity_strata.median, 842.5);
        explanation = "Evaluator complexity is not repository structural complexity or causal adjustment. Linear magnitude axis retains zeros and all 14 cases, including cases ineligible for ratios. Planning tier colors and cohort symbols remain fixed. Original full-population medians remain fixed.";
        break;
      }
    }
    if (data.length <= 1) delete layout.legend;
    const scope = sources.map(source => `${source.descriptor.title}: ${source.rows.length} of ${source.total} rows. ` +
      (selection?.id === source.id ? `${selection.summary}. ` : "Full approved source snapshot. ") +
      (source.descriptor.filter_effect === "select_rows_only"
        ? "Fixed published summary: selection chooses existing summary rows, not a recalculated population or N. "
        : "Existing observations only; original thresholds and association populations remain fixed. ")).join("");
    const caption = `${figure.rq}: ${figure.title}. ${scope}${explanation} ${figure.notes} ` +
      (excluded.length ? `${excluded.length} rows not plotted; see exclusion details and complete source table.` : "");
    return { id, title: figure.title, data, layout, config: { ...config }, caption, sources, excluded };
  }

  function createViewer(loadDataset, chooseDataset) {
    const byId = id => document.getElementById(id);
    const controls = byId("figure-controls");
    const select = byId("figure-select");
    const status = byId("figure-status");
    const error = byId("figure-error");
    const retry = byId("figure-retry");
    const reset = byId("figure-reset");
    const output = byId("figure-output");
    let catalog;
    let release;
    let request;
    let version = 0;
    let plot;
    let currentSpec;
    let selection;
    let selectionKey;
    const node = (tag, text) => {
      const element = document.createElement(tag);
      if (text !== undefined) element.textContent = text;
      return element;
    };
    function clear() {
      version += 1;
      request?.abort();
      request = null;
      if (plot && window.Plotly) window.Plotly.purge(plot);
      plot = null;
      currentSpec = null;
      output.replaceChildren();
      error.textContent = "";
      status.setAttribute("aria-busy", "false");
      status.textContent = "Choose a paper figure or a mapped source dataset to inspect its approved rows.";
      retry.hidden = true;
      reset.disabled = true;
    }
    function tables(spec) {
      const result = node("div");
      for (const source of spec.sources) {
        const detail = node("details");
        detail.append(node("summary", `Exact source table: ${source.descriptor.title} (${source.rows.length} of ${source.total} rows)`),
          node("p", `Grain: ${source.descriptor.grain}. Denominator: ${source.descriptor.denominator}. ` +
            source.descriptor.estimation_population));
        const use = node("button", `Filter this source: ${source.descriptor.title}`);
        use.type = "button";
        use.addEventListener("click", () => chooseDataset(source.id));
        detail.append(use);
        const wrapper = node("div");
        wrapper.className = "table-scroll";
        wrapper.tabIndex = 0;
        wrapper.setAttribute("role", "region");
        wrapper.setAttribute("aria-label", `Figure source table: ${source.descriptor.title}`);
        const table = node("table");
        table.append(node("caption", `${source.descriptor.title}. ${source.rows.length} of ${source.total} original rows; ` +
          `Unavailable means null, never zero. ${selection?.id === source.id ? selection.summary : "Full source snapshot."}`));
        const head = node("thead");
        const header = node("tr");
        for (const column of source.descriptor.columns) {
          const cell = node("th", `${column.label} (${column.unit})`);
          cell.scope = "col";
          header.append(cell);
        }
        head.append(header);
        table.append(head);
        const body = node("tbody");
        for (const row of source.rows) {
          const tr = node("tr");
          for (const column of source.descriptor.columns) {
            const value = row[column.id];
            const cell = node("td", value === null ? "Unavailable" : String(value));
            if (value === null) cell.className = "unavailable";
            else if (["integer", "number"].includes(column.type)) cell.className = "numeric";
            tr.append(cell);
          }
          body.append(tr);
        }
        table.append(body);
        wrapper.append(table);
        detail.append(wrapper);
        result.append(detail);
      }
      return result;
    }
    async function show() {
      clear();
      if (!select.value) return;
      const token = version;
      request = new AbortController();
      const pendingPlot = node("div");
      try {
        check(window.Plotly?.version === "4.1.2", "Local chart renderer 4.1.2 is unavailable. Check the vendor file.");
        const figure = catalog.figures.find(item => item.id === select.value);
        check(figureIds.includes(figure?.id), "Unsupported paper figure.");
        status.textContent = `Loading selected source rows for ${figure.title}...`;
        status.setAttribute("aria-busy", "true");
        const ids = [...new Set(figure.panels.map(panel => panel.dataset))];
        const entries = await Promise.all(ids.map(async id => {
          const descriptor = catalog.datasets.find(dataset => dataset.id === id);
          const record = release.datasets.find(dataset => dataset.id === id);
          check(descriptor && record, `Missing catalog/release entry: ${id}.`);
          return [id, await loadDataset(descriptor, record.row_count, fetch, request.signal)];
        }));
        if (token !== version) return;
        const spec = buildFigure(catalog, figure.id, Object.fromEntries(entries), selection);
        pendingPlot.className = "figure-plot";
        const hasPoints = spec.data.some(trace => trace.y.some(value => present(value)));
        if (hasPoints) {
          const errors = window.Plotly.validate(spec.data, spec.layout) || [];
          check(!errors.length, `Chart specification rejected: ${errors.map(item => item.msg).join("; ")}`);
          await window.Plotly.newPlot(pendingPlot, spec.data,
            { ...spec.layout, width: Math.max(760, output.clientWidth) }, spec.config);
        } else {
          pendingPlot.append(node("p", spec.sources.every(source => !source.rows.length)
            ? "No rows match these filters. Change a filter or reset row filters."
            : "No plottable values in the selected rows. See the exact source table and exclusion details; unavailable values are not zero."));
        }
        if (token !== version) { window.Plotly.purge(pendingPlot); return; }
        plot = hasPoints ? pendingPlot : null;
        currentSpec = spec;
        const figureNode = node("figure");
        const caption = node("figcaption", spec.caption);
        caption.id = "figure-caption";
        const wrapper = node("div");
        wrapper.className = "figure-scroll";
        wrapper.tabIndex = 0;
        wrapper.setAttribute("role", "region");
        wrapper.setAttribute("aria-label", spec.title);
        wrapper.setAttribute("aria-describedby", caption.id);
        wrapper.append(pendingPlot);
        figureNode.append(caption, wrapper);
        output.append(figureNode);
        if (spec.excluded.length) {
          const list = node("ul");
          for (const item of spec.excluded) list.append(node("li", `${item.cohort} / ${item.team_id}: ${item.reason}.`));
          output.append(node("p", "Rows retained in the source table but excluded from the plot:"), list);
        }
        output.append(tables(spec));
        status.textContent = `Figure loaded: ${spec.title}. ${scopeText()}`;
        reset.disabled = false;
      } catch (failure) {
        window.Plotly?.purge(pendingPlot);
        if (token !== version) return;
        request?.abort();
        plot = null;
        currentSpec = null;
        output.replaceChildren();
        error.textContent = `Figure error: ${failure instanceof Error ? failure.message : String(failure)} Choose another figure or retry.`;
        status.textContent = "Figure could not be loaded. No figure or source table is being shown.";
        retry.hidden = false;
        console.error("Research explorer figure load failed:", failure);
      } finally {
        if (token === version) status.setAttribute("aria-busy", "false");
      }
    }
    function scopeText() {
      return selection ? `Linked to the observation table for ${selection.id}. ${selection.summary}. ` +
        "Only that exact source is filtered; other panels retain their full snapshots. Original Ns and guides remain fixed."
        : "Full approved source snapshots; no observation selection is linked.";
    }
    select.addEventListener("change", () => {
      const figure = catalog.figures.find(item => item.id === select.value);
      if (figure) chooseDataset(figure.panels[0].dataset);
      else clear();
    });
    retry.addEventListener("click", show);
    reset.addEventListener("click", show);
    window.addEventListener("resize", () => {
      if (plot && currentSpec) {
        const token = version;
        window.Plotly.relayout(plot, { width: Math.max(760, output.clientWidth) }).catch(failure => {
          if (token !== version) return;
          error.textContent = `Figure resize error: ${failure.message}. Retry the figure.`;
          console.error("Research explorer figure resize failed:", failure);
          retry.hidden = false;
        });
      }
    });
    return {
      clear() {
        clear(); selection = null; selectionKey = null;
        controls.disabled = true; select.replaceChildren(new Option("Choose a paper figure", ""));
      },
      setSelection(next) {
        if (!next) {
          selection = null; selectionKey = null;
          clear();
          status.textContent = "Waiting for the selected observation dataset. No stale figure is shown.";
          return;
        }
        const key = JSON.stringify(next);
        if (key === selectionKey) return;
        selectionKey = key;
        selection = next;
        const figure = catalog.figures.find(item => item.panels.some(panel => panel.dataset === next.id));
        select.value = figure?.id || "";
        if (figure) show();
        else {
          clear();
          status.textContent = "No selected paper figure maps to this dataset. Choose a paper figure to open its source dataset and filters.";
        }
      },
      configure(nextCatalog, nextRelease) {
        clear();
        catalog = nextCatalog;
        release = nextRelease;
        check(Array.isArray(catalog.figures) && JSON.stringify(catalog.figures.map(figure => figure.id)) ===
          JSON.stringify(figureIds), "Unsupported paper figure inventory.");
        select.replaceChildren(new Option("Choose a paper figure", ""),
          ...catalog.figures.map(figure => new Option(`${figure.rq}: ${figure.title}`, figure.id)));
        controls.disabled = false;
      },
    };
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { figureIds, buildFigure };
  else window.ResearchCharts = { figureIds, buildFigure, createViewer };
})();
