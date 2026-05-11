<script>
  import { RefreshCw, Trash2 } from "lucide-svelte";

  export let disabledTariffs = 0;
  export let enabledTariffs = [];
  export let loadTariffs = () => {};
  export let openEditTariff = () => {};
  export let setDefaultTariff = () => {};
  export let tariffDeleteOpen = false;
  export let tariffDeleteTarget = null;
  export let tariffName = () => "";
  export let tariffPriceSummary = () => "";
  export let tariffsCatalog = { tariffs: [] };
  export let tariffsLoading = false;
  export let tariffsPath = "";
  export let tariffsSaving = false;
  export let toggleTariffEnabled = () => {};
</script>

{#if tariffsLoading}
  <div class="admin-empty">Загрузка…</div>
{:else}
  <div class="admin-stat-grid">
    <div class="admin-stat-card">
      <span class="admin-stat-label">Всего тарифов</span>
      <strong class="admin-stat-value">{tariffsCatalog.tariffs.length}</strong>
      <span class="admin-stat-trend">Включено: {enabledTariffs.length}</span>
    </div>
    <div class="admin-stat-card">
      <span class="admin-stat-label">По умолчанию</span>
      <strong class="admin-stat-value">{tariffsCatalog.default_tariff || "—"}</strong>
      <span class="admin-stat-trend">Используется для новых подписок</span>
    </div>
    <div class="admin-stat-card">
      <span class="admin-stat-label">Отключено</span>
      <strong class="admin-stat-value">{disabledTariffs}</strong>
      <span class="admin-stat-trend">Скрыто с витрины</span>
    </div>
  </div>

  <article class="admin-card">
    <header class="admin-card-head">
      <div>
        <h3>Каталог тарифов</h3>
        <small>{tariffsPath || "config/tariffs.json"}</small>
      </div>
      <button type="button" class="admin-btn admin-btn-sm" on:click={loadTariffs} disabled={tariffsLoading || tariffsSaving}>
        <RefreshCw size={13} /> Обновить
      </button>
    </header>
    <div class="admin-card-body">
      {#if !tariffsCatalog.tariffs.length}
        <div class="admin-empty">
          Каталог пуст. Добавьте первый тариф, после сохранения будет создан JSON-файл каталога.
        </div>
      {:else}
        <div class="admin-tariff-grid">
          {#each tariffsCatalog.tariffs as tariff}
            <article class="admin-tariff-card" class:is-disabled={tariff.enabled === false}>
              <div class="admin-tariff-top">
                <div>
                  <div class="admin-tariff-title">
                    <strong>{tariffName(tariff)}</strong>
                    {#if tariff.key === tariffsCatalog.default_tariff}
                      <span class="admin-badge admin-badge-success">Default</span>
                    {/if}
                  </div>
                  <code>{tariff.key}</code>
                </div>
                {#if tariff.enabled === false}
                  <span class="admin-badge admin-badge-muted">Выключен</span>
                {:else}
                  <span class="admin-badge admin-badge-success">Активен</span>
                {/if}
              </div>
              <p>{tariff.descriptions?.ru || tariff.descriptions?.en || "Без описания"}</p>
              <div class="admin-tariff-facts">
                <span>{tariff.billing_model === "traffic" ? "Трафик" : "Периоды"}</span>
                <span>{tariffPriceSummary(tariff)}</span>
                <span>Squads: {(tariff.squad_uuids || []).length}</span>
                <span>Premium: {(tariff.premium_squad_uuids || []).length ? `${tariff.premium_monthly_gb || 0} GB` : "—"}</span>
                <span>Устройства: {tariff.hwid_device_limit ?? "env"}</span>
              </div>
              <div class="admin-tariff-actions">
                <button type="button" class="admin-btn admin-btn-sm" on:click={() => openEditTariff(tariff)}>
                  Настроить
                </button>
                <button type="button" class="admin-btn admin-btn-sm" on:click={() => toggleTariffEnabled(tariff)} disabled={tariffsSaving}>
                  {tariff.enabled === false ? "Включить" : "Выключить"}
                </button>
                <button
                  type="button"
                  class="admin-btn admin-btn-sm"
                  on:click={() => setDefaultTariff(tariff.key)}
                  disabled={tariffsSaving || tariff.enabled === false || tariff.key === tariffsCatalog.default_tariff}
                >
                  По умолчанию
                </button>
                <button
                  type="button"
                  class="admin-btn admin-btn-sm admin-btn-danger"
                  on:click={() => { tariffDeleteTarget = tariff; tariffDeleteOpen = true; }}
                  disabled={tariffsSaving}
                  aria-label="Удалить тариф"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </div>
  </article>
{/if}
