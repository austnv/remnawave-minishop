<script>
  import { BarChart3, Coins, Database, Send, Shield, UsersRound } from "lucide-svelte";

  export let fmtDate = (value) => value;
  export let fmtMoney = (value) => value;
  export let paymentStatusVariant = () => "muted";
  export let stats = null;
  export let statsError = "";
  export let statsLoading = false;
</script>

{#if statsError}
  <div class="admin-empty">Не удалось загрузить статистику: {statsError}</div>
{:else if statsLoading || !stats}
  <div class="admin-empty">Загрузка…</div>
{:else}
  <div class="admin-stat-grid">
    <article class="admin-stat-card">
      <span class="admin-stat-label"><UsersRound size={14} /> Пользователи</span>
      <span class="admin-stat-value">{stats.users?.total_users ?? 0}</span>
      <span class="admin-stat-trend">В бане: {stats.users?.banned_users ?? 0}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Shield size={14} /> Платные подписки</span>
      <span class="admin-stat-value">{stats.users?.paid_subscriptions ?? 0}</span>
      <span class="admin-stat-trend">Триалы: {stats.users?.trial_users ?? 0}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Coins size={14} /> Доход за день</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.today_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">{stats.financial?.today_payments_count ?? 0} платежей</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><BarChart3 size={14} /> За неделю</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.week_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">Месяц: {fmtMoney(stats.financial?.month_revenue, stats.currency_symbol)}</span>
    </article>
    <article class="admin-stat-card">
      <span class="admin-stat-label"><Database size={14} /> Всё время</span>
      <span class="admin-stat-value">{fmtMoney(stats.financial?.all_time_revenue, stats.currency_symbol)}</span>
      <span class="admin-stat-trend">Sync: {stats.panel_sync?.status ?? "—"}</span>
    </article>
    {#if stats.queue}
      <article class="admin-stat-card">
        <span class="admin-stat-label"><Send size={14} /> Очередь</span>
        <span class="admin-stat-value">{stats.queue.user_queue_size ?? 0}</span>
        <span class="admin-stat-trend">Группы: {stats.queue.group_queue_size ?? 0}</span>
      </article>
    {/if}
  </div>

  <div class="admin-table-wrap">
    <header class="admin-card-head">
      <h3>Последние платежи</h3>
      <small>{(stats.recent_payments || []).length} записей</small>
    </header>
    {#if (stats.recent_payments || []).length}
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пользователь</th>
            <th>Сумма</th>
            <th>Провайдер</th>
            <th>Статус</th>
            <th>Дата</th>
          </tr>
        </thead>
        <tbody>
          {#each stats.recent_payments as p}
            <tr>
              <td class="admin-cell-id" data-label="ID">#{p.payment_id}</td>
              <td data-label="Пользователь">{p.user_label || p.user_id}</td>
              <td data-label="Сумма">{fmtMoney(p.amount, p.currency)}</td>
              <td data-label="Провайдер">{p.provider}</td>
              <td data-label="Статус">
                <span class="admin-badge admin-badge-{paymentStatusVariant(p.status)}">{p.status}</span>
              </td>
              <td data-label="Дата">{fmtDate(p.created_at)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <div class="admin-card-body"><span class="admin-muted">Нет данных</span></div>
    {/if}
  </div>
{/if}
