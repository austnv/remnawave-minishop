<script>
  import { BarChart3, Coins, Database, Send, Shield, UsersRound } from "lucide-svelte";
  import { getContext, onMount } from "svelte";

  export let at;
  export let fmtDate = (value) => value;
  export let fmtMoney = (value) => value;
  export let paymentStatusVariant = () => "muted";

  const statsStore = getContext("statsStore");

  $: ({
    stats,
    statsError,
    statsLoading,
  } = $statsStore);

  onMount(() => {
    statsStore.loadStats();
  });
</script>

{#if statsError}
  <div class="admin-empty">{at("stats_error", { error: statsError }, "Не удалось загрузить статистику: " + statsError)}</div>
{:else if statsLoading || !stats}
  <div class="admin-empty">{at("loading", {}, "Загрузка…")}</div>
{:else}
  <div class="admin-stat-grid">
    <article class="admin-stat-card">
      <span class="admin-stat-label"><UsersRound size={14} /> {at("stats_label_users", {}, "Пользователи")}</span>
      <span class="admin-stat-value">{stats.users?.total_users ?? 0}</span>
      <span class="admin-stat-trend">{at("stats_trend_banned", { count: stats.users?.banned_users ?? 0 }, "В бане: " + (stats.users?.banned_users ?? 0))}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Shield size={14} /> {at("stats_label_paid_subs", {}, "Платные подписки")}</span>
      <span class="admin-stat-value">{stats.users?.paid_subscriptions ?? 0}</span>
      <span class="admin-stat-trend">{at("stats_trend_trials", { count: stats.users?.trial_users ?? 0 }, "Триалы: " + (stats.users?.trial_users ?? 0))}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Coins size={14} /> {at("stats_label_today_rev", {}, "Доход за день")}</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.today_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">{at("stats_trend_payments", { count: stats.financial?.today_payments_count ?? 0 }, (stats.financial?.today_payments_count ?? 0) + " платежей")}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><BarChart3 size={14} /> {at("stats_label_week", {}, "За неделю")}</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.week_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">{at("stats_trend_month", { value: fmtMoney(stats.financial?.month_revenue, stats.currency_symbol) }, "Месяц: " + fmtMoney(stats.financial?.month_revenue, stats.currency_symbol))}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Database size={14} /> {at("stats_label_all_time", {}, "Всё время")}</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.all_time_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">{at("stats_sync_label", {}, "Sync")}: {stats.panel_sync?.status ?? "—"}</span>
    </article>
    {#if stats.queue}
      <article class="admin-stat-card">
        <span class="admin-stat-label"><Send size={14} /> {at("stats_label_queue", {}, "Очередь")}</span>
        <span class="admin-stat-value">{stats.queue.user_queue_size ?? 0}</span>
        <span class="admin-stat-trend">{at("stats_trend_groups", { count: stats.queue.group_queue_size ?? 0 }, "Группы: " + (stats.queue.group_queue_size ?? 0))}</span>
      </article>
    {/if}
  </div>

  <div class="admin-table-wrap">
    <header class="admin-card-head">
      <h3>{at("stats_recent_payments", {}, "Последние платежи")}</h3>
      <small>{at("stats_records_count", { count: (stats.recent_payments || []).length }, (stats.recent_payments || []).length + " записей")}</small>
    </header>
    {#if (stats.recent_payments || []).length}
      <table class="admin-table">
        <thead>
          <tr>
            <th>{at("id", {}, "ID")}</th>
            <th>{at("user", {}, "Пользователь")}</th>
            <th>{at("amount", {}, "Сумма")}</th>
            <th>{at("provider", {}, "Провайдер")}</th>
            <th>{at("status", {}, "Статус")}</th>
            <th>{at("date", {}, "Дата")}</th>
          </tr>
        </thead>
        <tbody>
          {#each stats.recent_payments as p}
            <tr>
              <td class="admin-cell-id" data-label="ID">#{p.payment_id}</td>
              <td data-label={at("user", {}, "Пользователь")}>{p.user_label || p.user_id}</td>
              <td data-label={at("amount", {}, "Сумма")}>{fmtMoney(p.amount, p.currency)}</td>
              <td data-label={at("provider", {}, "Провайдер")}>{p.provider}</td>
              <td data-label={at("status", {}, "Статус")}>
                <span class="admin-badge admin-badge-{paymentStatusVariant(p.status)}">{p.status}</span>
              </td>
              <td data-label={at("date", {}, "Дата")}>{fmtDate(p.created_at)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <div class="admin-card-body"><span class="admin-muted">{at("no_data", {}, "Нет данных")}</span></div>
    {/if}
  </div>
{/if}
