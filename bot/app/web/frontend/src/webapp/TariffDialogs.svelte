<script>
  import { ArrowRight, CheckCircle2, LockKeyhole } from "lucide-svelte";

  import Button from "../lib/components/ui/button.svelte";
  import Card from "../lib/components/ui/card.svelte";
  import Dialog from "../lib/components/ui/dialog.svelte";

  export let actionKey = () => "";
  export let applyTariffChange = () => {};
  export let changeActionTitle = () => "";
  export let changeConfirmOpen = false;
  export let changeModalOpen = false;
  export let changeOptions = null;
  export let closeDeviceTopupModal = () => {};
  export let closeTariffChangeConfirm = () => {};
  export let closeTariffChangeModal = () => {};
  export let closeTopupModal = () => {};
  export let createDeviceTopupPayment = () => {};
  export let createTopupPayment = () => {};
  export let deviceTopupModalDescription = () => "";
  export let deviceTopupModalOpen = false;
  export let deviceTopupOptions = null;
  export let methods = [];
  export let methodMeta = () => ({});
  export let openTariffChangeConfirm = () => {};
  export let payBusy = false;
  export let planKey = () => "";
  export let planUnitHint = () => "";
  export let priceLabel = () => "";
  export let selectedChangeAction = null;
  export let selectedChangeTarget = null;
  export let selectedDeviceTopupPlan = null;
  export let selectedMethod = "";
  export let selectedTopupPlan = null;
  export let singleTariffMode = false;
  export let tariffActionBusy = false;
  export let tariffChangeModalDescription = () => "";
  export let tariffChangeSummary = () => [];
  export let topupCarryoverNotes = () => [];
  export let topupModalDescription = () => "";
  export let topupModalOpen = false;
  export let topupModalTitle = () => "";
  export let topupOptions = null;
  export let t = (key) => key;
</script>

<Dialog
  open={changeModalOpen}
  title={t("wa_change_tariff")}
  description={tariffChangeModalDescription()}
  closeLabel={t("wa_close")}
  onclose={closeTariffChangeModal}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    {#if !changeOptions}
      <div class="dialog-skeleton" aria-label={t("wa_tariff_options_loading")}>
        <div class="tariff-action-list">
          {#each [1, 2] as _}
            <div class="tariff-action-card skeleton-row">
              <span>
                <span class="skeleton-line skeleton-line-title"></span>
                <span class="skeleton-line skeleton-line-short"></span>
              </span>
              <span class="skeleton-line skeleton-line-price"></span>
            </div>
          {/each}
        </div>
        <div class="payment-divider" aria-hidden="true"></div>
        <div class="option-list">
          {#each [1, 2] as _}
            <div class="option-row change-action-row skeleton-row">
              <span class="option-row-main">
                <span class="skeleton-line skeleton-line-title"></span>
                <span class="skeleton-line skeleton-line-short"></span>
              </span>
            </div>
          {/each}
        </div>
        <div class="skeleton-pay-button"></div>
      </div>
    {:else if changeOptions?.targets?.length}
      <p class="section-kicker">{t("wa_tariff_change_targets_title")}</p>
      <div class="tariff-action-list">
        {#each changeOptions.targets as target}
          <button
            class:active={selectedChangeTarget?.tariff_key === target.tariff_key}
            class="tariff-action-card"
            type="button"
            on:click={() => {
              selectedChangeTarget = target;
              selectedChangeAction = target.actions?.[0] || null;
            }}
          >
            <span>
              <strong>{target.title}</strong>
              <small>{target.description}</small>
            </span>
            <em>{target.billing_model === "traffic" ? t("wa_tariff_model_traffic") : t("wa_tariff_model_period")}</em>
          </button>
        {/each}
      </div>
      {#if selectedChangeTarget?.actions?.length}
        <div class="payment-divider" aria-hidden="true"></div>
        <p class="section-kicker">{t("wa_tariff_change_strategy_title")}</p>
        <div class="option-list">
          {#each selectedChangeTarget.actions as action}
            <button
              class:active={actionKey(selectedChangeAction) === actionKey(action)}
              class="option-row change-action-row"
              type="button"
              on:click={() => (selectedChangeAction = action)}
            >
              <span class="option-row-main">
                <strong>{changeActionTitle(action)}</strong>
                {#if action.mode === "recalc_days"}
                  <small>{t("wa_tariff_change_recalc_hint", { days: Number(action.remaining_days || 0) })}</small>
                {:else if action.mode === "convert_days_to_gb"}
                  <small>{t("wa_tariff_change_convert_hint", { days: Number(action.remaining_days || 0) })}</small>
                {:else if action.kind === "payment"}
                  <small>{t("wa_tariff_change_payment_hint")}</small>
                {/if}
              </span>
              {#if actionKey(selectedChangeAction) === actionKey(action)}
                <CheckCircle2 size={18} />
              {/if}
            </button>
          {/each}
        </div>
        {#if selectedChangeAction?.kind === "payment"}
          <div class="method-grid">
            {#each methods as method}
              {@const meta = methodMeta(method)}
              <button
                class:active={selectedMethod === method.id}
                class="method-card"
                type="button"
                on:click={() => (selectedMethod = method.id)}
              >
                <span class="method-card-main">
                  {#if meta.icon}
                    <svelte:component this={meta.icon} size={19} />
                  {/if}
                  <strong>{meta.title}</strong>
                </span>
              </button>
            {/each}
          </div>
        {/if}
        <Button class="wide bottom-action payment-submit-button" onclick={openTariffChangeConfirm} disabled={tariffActionBusy || payBusy}>
          {selectedChangeAction?.kind === "payment" ? t("wa_pay") : t("wa_apply")}
          <ArrowRight size={17} />
        </Button>
      {:else}
        <Card class="empty-card">{t("wa_no_tariff_change_options")}</Card>
      {/if}
    {:else}
      <Card class="empty-card">{t("wa_no_tariff_change_options")}</Card>
    {/if}
  </div>
</Dialog>

<Dialog
  open={changeConfirmOpen}
  title={t("wa_tariff_change_confirm_title")}
  description={t("wa_tariff_change_confirm_desc")}
  closeLabel={t("wa_close")}
  onclose={closeTariffChangeConfirm}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    <Card class="confirm-summary-card">
      {#each tariffChangeSummary() as row}
        <p>{row}</p>
      {/each}
    </Card>
    <Button class="wide bottom-action payment-submit-button" onclick={applyTariffChange} disabled={tariffActionBusy || payBusy}>
      {selectedChangeAction?.kind === "payment" ? t("wa_confirm_and_pay") : t("wa_confirm_and_apply")}
      <ArrowRight size={17} />
    </Button>
    <Button variant="secondary" class="wide" onclick={closeTariffChangeConfirm} disabled={tariffActionBusy || payBusy}>
      {t("wa_cancel")}
    </Button>
  </div>
</Dialog>

<Dialog
  open={topupModalOpen}
  title={topupModalTitle()}
  description={topupModalDescription()}
  closeLabel={t("wa_close")}
  onclose={closeTopupModal}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    {#if !topupOptions}
      <div class="dialog-skeleton" aria-label={t("wa_tariff_options_loading")}>
        <div class="option-list">
          {#each [1, 2, 3] as _}
            <div class="option-row plan-row skeleton-row">
              <span class="option-row-main">
                <span class="skeleton-line skeleton-line-title"></span>
                <span class="skeleton-line skeleton-line-short"></span>
              </span>
              <span class="option-row-meta">
                <span class="skeleton-line skeleton-line-price"></span>
                <span class="skeleton-line skeleton-line-tiny"></span>
              </span>
            </div>
          {/each}
        </div>
        <div class="method-grid">
          {#each [1, 2] as _}
            <div class="method-card skeleton-method">
              <span class="skeleton-dot"></span>
              <span class="skeleton-line skeleton-line-method"></span>
            </div>
          {/each}
        </div>
        <div class="skeleton-pay-button"></div>
      </div>
    {:else if topupOptions?.plans?.length}
      <div class="option-list">
        {#each topupOptions.plans as plan}
          <button
            class:active={planKey(selectedTopupPlan) === planKey(plan)}
            class="option-row plan-row"
            type="button"
            on:click={() => (selectedTopupPlan = plan)}
          >
            <span class="option-row-main">
              <strong>{plan.title}</strong>
              {#if !singleTariffMode || plan.sale_mode === "premium_topup"}
                <small>{plan.subtitle || topupOptions.tariff_name}</small>
              {/if}
            </span>
            <span class="option-row-meta">
              <em>{priceLabel(plan)}</em>
              {#if planUnitHint(plan)}
                <small>{planUnitHint(plan)}</small>
              {/if}
            </span>
          </button>
        {/each}
      </div>
      {@const carryoverNotes = topupCarryoverNotes()}
      {#if carryoverNotes.length}
        <div class="topup-carryover-note">
          {#each carryoverNotes as note}
            <p>{note}</p>
          {/each}
        </div>
      {/if}
      <div class="method-grid">
        {#each methods as method}
          {@const meta = methodMeta(method)}
          <button
            class:active={selectedMethod === method.id}
            class="method-card"
            type="button"
            on:click={() => (selectedMethod = method.id)}
          >
            <span class="method-card-main">
              {#if meta.icon}
                <svelte:component this={meta.icon} size={19} />
              {/if}
              <strong>{meta.title}</strong>
            </span>
          </button>
        {/each}
      </div>
      <Button class="wide bottom-action payment-submit-button" onclick={createTopupPayment} disabled={!selectedTopupPlan || !methods.length || payBusy}>
        {t("wa_buy_traffic")} {selectedTopupPlan ? priceLabel(selectedTopupPlan) : ""}
        <LockKeyhole size={17} />
      </Button>
    {:else}
      <Card class="empty-card">{t("wa_no_topup_options")}</Card>
    {/if}
  </div>
</Dialog>

<Dialog
  open={deviceTopupModalOpen}
  title={t("wa_buy_hwid_devices")}
  description={deviceTopupModalDescription()}
  closeLabel={t("wa_close")}
  onclose={closeDeviceTopupModal}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    {#if !deviceTopupOptions}
      <div class="dialog-skeleton" aria-label={t("wa_tariff_options_loading")}>
        <div class="option-list">
          {#each [1, 2, 3] as _}
            <div class="option-row plan-row skeleton-row">
              <span class="option-row-main">
                <span class="skeleton-line skeleton-line-title"></span>
                <span class="skeleton-line skeleton-line-short"></span>
              </span>
              <span class="option-row-meta">
                <span class="skeleton-line skeleton-line-price"></span>
              </span>
            </div>
          {/each}
        </div>
        <div class="method-grid">
          {#each [1, 2] as _}
            <div class="method-card skeleton-method">
              <span class="skeleton-dot"></span>
              <span class="skeleton-line skeleton-line-method"></span>
            </div>
          {/each}
        </div>
        <div class="skeleton-pay-button"></div>
      </div>
    {:else if deviceTopupOptions?.plans?.length}
      <div class="option-list">
        {#each deviceTopupOptions.plans as plan}
          <button
            class:active={planKey(selectedDeviceTopupPlan) === planKey(plan)}
            class="option-row plan-row"
            type="button"
            on:click={() => (selectedDeviceTopupPlan = plan)}
          >
            <span class="option-row-main">
              <strong>{t("wa_hwid_devices_package", { count: Number(plan.device_count || plan.months || 0) })}</strong>
              <small>{plan.subtitle || deviceTopupOptions.tariff_name}</small>
            </span>
            <span class="option-row-meta">
              <em>{priceLabel(plan)}</em>
              {#if planKey(selectedDeviceTopupPlan) === planKey(plan)}
                <CheckCircle2 size={18} />
              {/if}
            </span>
          </button>
        {/each}
      </div>
      <div class="method-grid">
        {#each methods as method}
          {@const meta = methodMeta(method)}
          <button
            class:active={selectedMethod === method.id}
            class="method-card"
            type="button"
            on:click={() => (selectedMethod = method.id)}
          >
            <span class="method-card-main">
              {#if meta.icon}
                <svelte:component this={meta.icon} size={19} />
              {/if}
              <strong>{meta.title}</strong>
            </span>
          </button>
        {/each}
      </div>
      <Button class="wide bottom-action payment-submit-button" onclick={createDeviceTopupPayment} disabled={!selectedDeviceTopupPlan || !methods.length || payBusy}>
        {t("wa_pay")} {selectedDeviceTopupPlan ? priceLabel(selectedDeviceTopupPlan) : ""}
        <LockKeyhole size={17} />
      </Button>
    {:else}
      <Card class="empty-card">{t("wa_no_hwid_device_options")}</Card>
    {/if}
  </div>
</Dialog>

