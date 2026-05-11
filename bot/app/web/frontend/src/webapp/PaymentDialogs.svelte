<script>
  import { ArrowLeft, CheckCircle2, CircleX, LockKeyhole, RefreshCw, TriangleAlert } from "lucide-svelte";
  import { Tooltip } from "bits-ui";

  import Button from "../lib/components/ui/button.svelte";
  import Card from "../lib/components/ui/card.svelte";
  import Dialog from "../lib/components/ui/dialog.svelte";
  import Input from "../lib/components/ui/input.svelte";

  export let createPayment = () => {};
  export let deviceConfirmOpen = false;
  export let deviceDisconnectBusy = false;
  export let deviceToDisconnect = null;
  export let disconnectDevice = () => {};
  export let linkEmailBusy = false;
  export let linkEmailCode = "";
  export let linkEmailFieldError = "";
  export let linkEmailIsError = false;
  export let linkEmailOpen = false;
  export let linkEmailPending = "";
  export let linkEmailResendCooldown = 0;
  export let linkEmailStatus = "";
  export let linkEmailValue = "";
  export let methods = [];
  export let payBusy = false;
  export let paymentModalOpen = false;
  export let paymentStep = "tariff";
  export let plans = [];
  export let selectedMethod = "";
  export let selectedPlan = null;
  export let selectedTariff = null;
  export let selectedTariffKey = "";
  export let selectedTariffPlans = [];
  export let singleTariffMode = false;
  export let subscription = {};
  export let tariffCatalog = [];
  export let tariffMode = false;

  export let closeDeviceDisconnectDialog = () => {};
  export let closeLinkEmailDialog = () => {};
  export let closePaymentModal = () => {};
  export let continueWithSelectedTariff = () => {};
  export let methodMeta = () => ({});
  export let paymentDescription = () => "";
  export let paymentTitle = () => "";
  export let planKey = () => "";
  export let planSubtitle = () => "";
  export let planUnitHint = () => "";
  export let priceLabel = () => "";
  export let requestLinkEmailCode = () => {};
  export let selectTariff = () => {};
  export let t = (key) => key;
  export let verifyLinkEmailCode = () => {};
</script>

<Dialog
  open={paymentModalOpen}
  title={paymentTitle()}
  description={paymentDescription()}
  closeLabel={t("wa_close")}
  onclose={closePaymentModal}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    {#if tariffMode && !singleTariffMode && paymentStep === "tariff"}
      {#if tariffCatalog.length}
        <div class="option-list tariff-list">
          {#each tariffCatalog as tariff}
            <button
              class:active={selectedTariffKey === tariff.key}
              class="option-row tariff-row"
              type="button"
              on:click={() => selectTariff(tariff)}
            >
              <span class="option-row-main">
                <strong>{tariff.title}</strong>
                <small>{tariff.description || t("wa_tariff_no_description")}</small>
              </span>
              <span class="option-row-meta">
                <em>{tariffLimitLabel(tariff)}</em>
                {#if selectedTariffKey === tariff.key}
                  <CheckCircle2 size={18} />
                {:else}
                  <ArrowRight size={17} />
                {/if}
              </span>
            </button>
          {/each}
        </div>
        <Button class="wide bottom-action payment-submit-button" onclick={continueWithSelectedTariff} disabled={!selectedTariffKey}>
          {t("wa_next")}
          <ArrowRight size={17} />
        </Button>
      {:else}
        <Card class="empty-card">{t("wa_no_tariff_change_options")}</Card>
      {/if}
    {:else}
      {#if tariffMode}
        {#if !singleTariffMode && !(subscription?.active && subscription?.tariff_key && tariffCatalog.some((t) => t.key === subscription.tariff_key))}
          <button class="back-inline" type="button" on:click={backToTariffList}>
            <ArrowLeft size={16} />
            {t("wa_back_to_tariffs")}
          </button>
        {/if}
        {#if hasMultipleTariffs && selectedTariff}
          <p class="tariff-step-caption">{t("wa_selected_tariff", { tariff: selectedTariff.title })}</p>
        {/if}
      {/if}
      {#if selectedTariffPlans.length}
        <div class="period-grid period-grid-two-columns">
          {#each selectedTariffPlans as plan}
            <button
              class:active={planKey(selectedPlan) === planKey(plan)}
              class="period-card"
              type="button"
              on:click={() => (selectedPlan = plan)}
            >
              <strong>{planSubtitle(plan) || planDisplayTitle(plan)}</strong>
              <span>{priceLabel(plan)}</span>
              {#if planUnitHint(plan)}
                <small>{planUnitHint(plan)}</small>
              {/if}
              {#if planKey(selectedPlan) === planKey(plan)}
                <CheckCircle2 size={18} />
              {/if}
            </button>
          {/each}
        </div>
        <div class="payment-divider" aria-hidden="true"></div>
        <div class="method-grid">
          {#if methods.length}
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
          {:else}
            <Card class="empty-card">{t("wa_payment_methods_not_configured")}</Card>
          {/if}
        </div>
        <Button class="wide bottom-action payment-submit-button" onclick={createPayment} disabled={!selectedPlan || !methods.length || payBusy}>
          {t("wa_pay")} {selectedPlan ? priceLabel(selectedPlan) : ""}
          <LockKeyhole size={17} />
        </Button>
      {:else}
        <Card class="empty-card">{t("wa_no_tariff_change_options")}</Card>
      {/if}
    {/if}
    {#if !tariffMode}
      <div class="period-grid period-grid-two-columns">
        {#each plans as plan}
          <button
            class:active={planKey(selectedPlan) === planKey(plan)}
            class="period-card"
            type="button"
            on:click={() => (selectedPlan = plan)}
          >
            <strong>{planDisplayTitle(plan)}</strong>
            {#if planSubtitle(plan)}
              <em>{planSubtitle(plan)}</em>
            {/if}
            <span>{priceLabel(plan)}</span>
            {#if planUnitHint(plan)}
              <small>{planUnitHint(plan)}</small>
            {/if}
            {#if planKey(selectedPlan) === planKey(plan)}
              <CheckCircle2 size={18} />
            {/if}
          </button>
        {/each}
      </div>
      <div class="payment-divider" aria-hidden="true"></div>
      <div class="method-grid">
        {#if methods.length}
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
        {:else}
          <Card class="empty-card">{t("wa_payment_methods_not_configured")}</Card>
        {/if}
      </div>
      <Button class="wide bottom-action payment-submit-button" onclick={createPayment} disabled={!selectedPlan || !methods.length || payBusy}>
        {t("wa_pay")} {selectedPlan ? priceLabel(selectedPlan) : ""}
        <LockKeyhole size={17} />
      </Button>
    {/if}
  </div>
</Dialog>

<Dialog
  open={deviceConfirmOpen}
  title={t("wa_devices_disconnect_title")}
  description={t("wa_devices_disconnect_desc", {
    device: deviceToDisconnect?.display_name || t("wa_device_fallback_name", { index: deviceToDisconnect?.index || "" }),
  })}
  closeLabel={t("wa_close")}
  onclose={closeDeviceDisconnectDialog}
  class="payment-dialog-card"
>
  <div class="payment-dialog-body">
    <Button variant="outline" class="wide device-danger-button" onclick={disconnectDevice} disabled={deviceDisconnectBusy}>
      <CircleX size={17} />
      {t("wa_devices_disconnect_confirm")}
    </Button>
    <Button variant="secondary" class="wide" onclick={closeDeviceDisconnectDialog} disabled={deviceDisconnectBusy}>
      {t("wa_cancel")}
    </Button>
  </div>
</Dialog>

<Dialog
  open={linkEmailOpen}
  title={t("wa_link_email_modal_title")}
  description={linkEmailPending ? t("wa_email_sent_to", { email: linkEmailPending }) : t("wa_link_email_modal_desc")}
  closeLabel={t("wa_close")}
  onclose={closeLinkEmailDialog}
  class={`payment-dialog-card${linkEmailPending ? " link-email-dialog-card" : ""}`}
>
  <div class="payment-dialog-body">
    {#if !linkEmailPending}
      <div class="field-error-wrap">
        <Tooltip.Root open={Boolean(linkEmailFieldError)}>
          <Input
            bind:value={linkEmailValue}
            type="email"
            placeholder={t("wa_email_placeholder")}
            autocomplete="email"
            class={linkEmailFieldError ? "input-error" : ""}
            on:input={() => (linkEmailFieldError = "")}
          />
          {#if linkEmailFieldError}
            <Tooltip.Trigger class="field-error-trigger" aria-label={linkEmailFieldError}>
              <span class="field-error-icon" aria-hidden="true"><TriangleAlert size={18} /></span>
            </Tooltip.Trigger>
          {/if}
          {#if linkEmailFieldError}
            <Tooltip.Portal>
              <Tooltip.Content class="field-error-tooltip">{linkEmailFieldError}</Tooltip.Content>
            </Tooltip.Portal>
          {/if}
        </Tooltip.Root>
      </div>
      <Button class="wide bottom-action payment-submit-button" onclick={requestLinkEmailCode} disabled={linkEmailBusy}>
        {t("wa_send_code_email")}
      </Button>
    {:else}
      <div class="link-email-code-layout">
        <div class="otp-wrap link-email-code-center">
          <label class="otp-input-wrap">
            <input
              bind:value={linkEmailCode}
              inputmode="numeric"
              autocomplete="one-time-code"
              maxlength="6"
              aria-label={t("wa_email_code_aria")}
            />
            <span class="otp-slots" aria-hidden="true">
              {#each Array.from({ length: 6 }) as _, index}
                <span class:filled={linkEmailCode[index]}>{linkEmailCode[index] || ""}</span>
              {/each}
            </span>
          </label>
          <Button class="wide bottom-action payment-submit-button" onclick={verifyLinkEmailCode} disabled={linkEmailBusy}>
            {t("wa_confirm")}
          </Button>
        </div>
        <button
          class="link-button link-email-resend"
          type="button"
          on:click={requestLinkEmailCode}
          disabled={linkEmailBusy || linkEmailResendCooldown > 0}
        >
          <RefreshCw size={15} />
          {linkEmailResendCooldown > 0
            ? t("wa_auth_resend_wait", { seconds: linkEmailResendCooldown })
            : t("wa_resend_code")}
        </button>
      </div>
    {/if}
    {#if linkEmailStatus}
      <p class:error={linkEmailIsError} class="status-line">{linkEmailStatus}</p>
    {/if}
  </div>
</Dialog>
