<script>
  import { CheckCircle2, ChevronsUpDown, CircleX, Database, Download, Gift, RefreshCw } from "lucide-svelte";

  import BrandMark from "../../BrandMark.svelte";
  import Button from "../../lib/components/ui/button.svelte";
  import Card from "../../lib/components/ui/card.svelte";

  export let CFG = {};
  export let appSettings = {};
  export let brandEmoji = "";
  export let brandTitle = "";
  export let canChangeTariff = false;
  export let canOpenPremiumTopupModal = false;
  export let canOpenRegularTopupModal = false;
  export let canShowTopupButton = false;
  export let currentTariffName = "";
  export let hasActiveTariffSubscription = false;
  export let hasMultipleTariffs = false;
  export let subscription = {};
  export let trafficMode = false;
  export let trialBusy = false;

  export let activeSubscriptionTermLabel = () => "";
  export let activateTrial = () => {};
  export let openConnectLink = () => {};
  export let openPaymentModal = () => {};
  export let openTariffChangeModal = () => {};
  export let openTopupModal = () => {};
  export let premiumServerLabels = () => [];
  export let premiumTitle = () => "";
  export let premiumTrafficLabel = () => "";
  export let premiumTrafficPercent = () => 0;
  export let primaryPayActionLabel = () => "";
  export let t = (key) => key;
  export let trafficLabel = () => "";
  export let trafficPercent = () => 0;
  export let trafficResetLabel = () => "";
  export let trialTrafficLabel = () => "";
</script>

<main class="home-layout">
  <div class="login-brand home-brand">
    <BrandMark class="brand-mark-xl" logoUrl={CFG.logoUrl} emoji={brandEmoji} />
    <h1>{brandTitle}</h1>
  </div>

  <div class="home-bottom">
    <Card class={`status-card${subscription.active ? "" : " status-card-inactive"}`}>
      {#if subscription.active}
        <div class="sub-status">
          <CheckCircle2 size={23} />
          <div>
            <h2>{trafficMode ? t("wa_home_access_active") : t("wa_home_subscription_active")} | {activeSubscriptionTermLabel(subscription)}</h2>
            {#if hasActiveTariffSubscription && hasMultipleTariffs && currentTariffName}
              <p class="current-tariff-line">{t("wa_current_tariff", { tariff: currentTariffName })}</p>
            {/if}
            <p>{subscription.end_date_text ? t("wa_until_date", { date: subscription.end_date_text }) : subscription.remaining_text}</p>
          </div>
        </div>
      {:else}
        <div class="sub-status sub-status-inactive">
          <CircleX size={23} />
          <h2>{t("wa_home_subscription_inactive")}</h2>
        </div>
      {/if}
    </Card>

    {#if subscription.active}
      <Card class={canOpenRegularTopupModal ? "traffic-card-clickable" : ""}>
        {#if canOpenRegularTopupModal}
          <button class="card-click-target" type="button" on:click={() => openTopupModal("regular")} aria-label={t("wa_topup_traffic")}></button>
        {/if}
        <div class="traffic-top">
          <span>{t("wa_home_traffic_used")}</span>
          <strong>{trafficLabel(subscription)}</strong>
        </div>
        <div class="progress">
          <span style={`width: ${trafficPercent(subscription)}%`}></span>
        </div>
        <div class="traffic-meta">
          <span>{trafficResetLabel(subscription)}</span>
          <span class="traffic-percent">{trafficPercent(subscription)}%</span>
        </div>
      </Card>
      {#if Number(subscription?.premium_limit_bytes || 0) > 0}
        <Card class={`${canOpenPremiumTopupModal ? "traffic-card-clickable " : ""}premium-traffic-card${subscription?.premium_is_limited ? " premium-traffic-card-limited" : ""}`}>
          {#if canOpenPremiumTopupModal}
            <button class="card-click-target" type="button" on:click={() => openTopupModal("premium")} aria-label={premiumTitle(subscription)}></button>
          {/if}
          <div class="traffic-top">
            <span>{premiumTitle(subscription)}</span>
            <strong>{premiumTrafficLabel(subscription)}</strong>
          </div>
          <div class="progress premium-progress">
            <span style={`width: ${premiumTrafficPercent(subscription)}%`}></span>
          </div>
          <div class="traffic-meta premium-traffic-meta">
            {#if premiumServerLabels(subscription).length}
              <details class="premium-server-dropdown">
                <summary>
                  <span>{subscription?.premium_is_limited ? t("wa_premium_access_limited", {}, "Доступ к premium временно ограничен") : t("wa_premium_reset_monthly", {}, "Отдельный лимит на месяц")}</span>
                  <ChevronsUpDown size={13} />
                </summary>
                <div class="premium-server-list premium-server-list-dropdown">
                  <small>{t("wa_premium_servers_limited", {}, "Отдельный лимит действует на")}</small>
                  <div>
                    {#each premiumServerLabels(subscription).slice(0, 8) as label}
                      <span>{label}</span>
                    {/each}
                  </div>
                </div>
              </details>
            {:else}
              <span>{subscription?.premium_is_limited ? t("wa_premium_access_limited", {}, "Доступ к premium временно ограничен") : t("wa_premium_reset_monthly", {}, "Отдельный лимит на месяц")}</span>
            {/if}
            <span class="traffic-percent">{premiumTrafficPercent(subscription)}%</span>
          </div>
        </Card>
      {/if}
    {:else if appSettings?.trial_enabled && appSettings?.trial_available}
      <Card class="trial-card">
        <div class="trial-card-head">
          <Gift size={22} />
          <span>
            <strong>{t("wa_trial_title")}</strong>
            <small>{t("wa_trial_details", { days: Number(appSettings?.trial_duration_days || 0), traffic: trialTrafficLabel() })}</small>
          </span>
        </div>
      </Card>
    {/if}

    <div class="action-stack">
      {#if subscription.active}
        <Button class="wide" onclick={openConnectLink}>
          <Download size={18} />
          {t("wa_install_and_configure")}
        </Button>
      {/if}
      <Button class="wide" variant={subscription.active ? "secondary" : "default"} onclick={openPaymentModal}>
        {#if subscription.active}
          <RefreshCw size={18} />
        {:else if trafficMode}
          <Database size={18} />
        {/if}
        {primaryPayActionLabel()}
      </Button>
      {#if !subscription.active && appSettings?.trial_enabled && appSettings?.trial_available}
        <Button class="wide" variant="secondary" onclick={activateTrial} disabled={trialBusy}>
          <Gift size={18} />
          {t("wa_activate_trial")}
        </Button>
      {/if}
      {#if canChangeTariff}
        <Button class="wide" variant="secondary" onclick={openTariffChangeModal}>
          <RefreshCw size={18} />
          {t("wa_change_tariff")}
        </Button>
      {/if}
      {#if canShowTopupButton}
        <Button class="wide" variant="secondary" onclick={() => openTopupModal(canOpenRegularTopupModal ? "regular" : "premium")}>
          <Database size={18} />
          {t("wa_topup_traffic")}
        </Button>
      {/if}
    </div>
  </div>
</main>
