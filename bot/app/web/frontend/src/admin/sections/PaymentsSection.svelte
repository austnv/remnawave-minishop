<script>
  import { ChevronLeft, ChevronRight } from "lucide-svelte";
  import { getContext, onMount } from "svelte";

  export let at = (key) => key;
  export let fmtDate = (value) => value;
  export let fmtMoney = (value) => value;
  export let paymentStatusVariant = () => "muted";

  const paymentsStore = getContext("paymentsStore");

  $: ({
    payments,
    paymentsTotal,
    paymentsPage,
    paymentsLoading,
  } = $paymentsStore);

  $: paymentsHasMore = payments.length > 0 && paymentsTotal > (paymentsPage + 1) * 25; // 25 is PAYMENTS_PAGE_SIZE

  onMount(() => {
    paymentsStore.loadPayments();
  });
</script>

<div class="admin-table-wrap">
  {#if paymentsLoading}
    <table class="admin-table admin-table-skeleton" aria-hidden="true">
      <thead>
        <tr>
          <th>{at("id", {}, "ID")}</th><th>{at("user", {}, "Пользователь")}</th><th>{at("amount", {}, "Сумма")}</th><th>{at("provider", {}, "Провайдер")}</th><th>{at("description", {}, "Описание")}</th><th>{at("status", {}, "Статус")}</th><th>{at("date", {}, "Дата")}</th>
        </tr>
      </thead>
      <tbody>
        {#each Array(8) as _, i (i)}
          <tr>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-tiny"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-short"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-short"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line"></span></td>
            <td><span class="admin-skeleton admin-skeleton-badge"></span></td>
            <td><span class="admin-skeleton admin-skeleton-line admin-skeleton-line-short"></span></td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else if !payments.length}
    <div class="admin-card-body"><span class="admin-muted">{at("payments_empty", {}, "Нет платежей")}</span></div>
  {:else}
    <table class="admin-table">
      <thead>
        <tr>
          <th>{at("id", {}, "ID")}</th>
          <th>{at("user", {}, "Пользователь")}</th>
          <th>{at("amount", {}, "Сумма")}</th>
          <th>{at("provider", {}, "Провайдер")}</th>
          <th>{at("description", {}, "Описание")}</th>
          <th>{at("status", {}, "Статус")}</th>
          <th>{at("date", {}, "Дата")}</th>
        </tr>
      </thead>
      <tbody>
        {#each payments as p}
          <tr>
            <td class="admin-cell-id" data-label="ID">#{p.payment_id}</td>
            <td data-label={at("user", {}, "Пользователь")}>{p.user_label || p.user_id}</td>
            <td data-label={at("amount", {}, "Сумма")}>{fmtMoney(p.amount, p.currency)}</td>
            <td data-label={at("provider", {}, "Провайдер")}>{p.provider}</td>
            <td class="admin-cell-wrap" data-label={at("description", {}, "Описание")}>{p.description || "—"}</td>
            <td data-label={at("status", {}, "Статус")}>
              <span class="admin-badge admin-badge-{paymentStatusVariant(p.status)}">{p.status}</span>
            </td>
            <td data-label={at("date", {}, "Дата")}>{fmtDate(p.created_at)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<div class="admin-pagination">
  <span class="admin-pagination-meta">{at("page_short", {}, "Стр.")} {paymentsPage + 1} · {at("total", {}, "Всего")} {paymentsTotal}</span>
  <div class="admin-pagination-buttons">
    <button type="button" class="admin-btn admin-btn-sm" disabled={paymentsPage === 0} on:click={() => { paymentsStore.setPage(Math.max(0, paymentsPage - 1)); }}>
      <ChevronLeft size={14} /> {at("back", {}, "Назад")}
    </button>
    <button type="button" class="admin-btn admin-btn-sm" disabled={!paymentsHasMore} on:click={() => { paymentsStore.setPage(paymentsPage + 1); }}>
      {at("next", {}, "Далее")} <ChevronRight size={14} />
    </button>
  </div>
</div>
