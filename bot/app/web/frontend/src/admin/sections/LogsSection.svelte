<script>
  import { ChevronLeft, ChevronRight } from "lucide-svelte";
  import { getContext, onMount } from "svelte";

  export let at;
  export let fmtDate;

  const logsStore = getContext("logsStore");

  $: ({
    logs,
    logsTotal,
    logsPage,
    logsUserFilter,
    logsLoading,
  } = $logsStore);

  $: logsHasMore = logs.length > 0 && logsTotal > (logsPage + 1) * 50; // 50 is LOGS_PAGE_SIZE

  onMount(() => {
    logsStore.loadLogs();
  });
</script>

<div class="admin-toolbar admin-toolbar-card">
  <div class="admin-toolbar-search admin-toolbar-search-actions">
    <input
      type="search"
      class="input"
      placeholder={at("logs_user_filter_placeholder", {}, "Фильтр по ID пользователя")}
      value={logsUserFilter}
      on:input={(e) => logsStore.setFilter(e.target.value)}
      on:keydown={(e) => e.key === "Enter" && (logsStore.setPage(0))}
    />
    <button type="button" class="admin-btn admin-btn-primary" on:click={() => { logsStore.setPage(0); }}>{at("apply", {}, "Применить")}</button>
    <button type="button" class="admin-btn admin-btn-ghost" on:click={() => { logsStore.setFilter(""); logsStore.setPage(0); }}>{at("reset", {}, "Сбросить")}</button>
  </div>
  <div class="admin-toolbar-summary">
    <span class="admin-toolbar-field-label">{at("total", {}, "Всего")}</span>
    <strong>{logsTotal}</strong>
  </div>
</div>

<div class="admin-table-wrap">
  {#if logsLoading}
    <table class="admin-table admin-table-skeleton" aria-hidden="true">
      <thead>
        <tr>
          <th>{at("date", {}, "Дата")}</th><th>{at("event", {}, "Событие")}</th><th>User</th><th>Target</th><th>{at("content", {}, "Контент")}</th>
        </tr>
      </thead>
      <tbody>
        {#each Array(10) as _, i (i)}
          <tr>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-short"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-short"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-tiny"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-tiny"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line"></span></td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else if !logs.length}
    <div class="admin-card-body"><span class="admin-muted">{at("logs_empty", {}, "Записей нет")}</span></div>
  {:else}
    <table class="admin-table">
      <thead>
        <tr>
          <th>{at("date", {}, "Дата")}</th>
          <th>{at("event", {}, "Событие")}</th>
          <th>{at("user_short", {}, "User")}</th>
          <th>{at("target_short", {}, "Target")}</th>
          <th>{at("content", {}, "Контент")}</th>
        </tr>
      </thead>
      <tbody>
        {#each logs as entry}
          <tr>
            <td data-label={at("date", {}, "Дата")}>{fmtDate(entry.timestamp)}</td>
            <td class="admin-cell-mono" data-label={at("event", {}, "Событие")}>{entry.event_type}</td>
            <td class="admin-cell-mono" data-label={at("user_short", {}, "User")}>{entry.user_id || "—"}</td>
            <td class="admin-cell-mono" data-label={at("target_short", {}, "Target")}>{entry.target_user_id || "—"}</td>
            <td class="admin-cell-wrap" data-label={at("content", {}, "Контент")}>{entry.content || ""}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<div class="admin-pagination">
  <span class="admin-pagination-meta">{at("page_short", {}, "Стр.")} {logsPage + 1}</span>
  <div class="admin-pagination-buttons">
    <button type="button" class="admin-btn admin-btn-sm" disabled={logsPage === 0} on:click={() => { logsStore.setPage(Math.max(0, logsPage - 1)); }}>
      <ChevronLeft size={14} /> {at("back", {}, "Назад")}
    </button>
    <button type="button" class="admin-btn admin-btn-sm" disabled={!logsHasMore} on:click={() => { logsStore.setPage(logsPage + 1); }}>
      {at("next", {}, "Далее")} <ChevronRight size={14} />
    </button>
  </div>
</div>
