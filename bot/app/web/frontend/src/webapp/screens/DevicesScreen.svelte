<script>
  import { CircleX, Plus, RefreshCw, Smartphone } from "lucide-svelte";

  import Button from "../../lib/components/ui/button.svelte";
  import Card from "../../lib/components/ui/card.svelte";

  export let devicesBusy = false;
  export let devicesData = {};
  export let devicesIsError = false;
  export let devicesLoaded = false;
  export let devicesStatus = "";
  export let subscription = {};

  export let loadDevices = () => {};
  export let openDeviceDisconnectDialog = () => {};
  export let openDeviceTopupModal = () => {};
  export let t = (key) => key;
  function devicesLimitLabel(value = devicesData?.max_devices) {
    const numeric = Number(value ?? 0);
    if (!Number.isFinite(numeric) || numeric <= 0) return t("wa_devices_unlimited");
    return String(Math.trunc(numeric));
  }

  function devicesCountLabel() {
    const current = Number(devicesData?.current_devices ?? devicesData?.devices?.length ?? 0);
    return t("wa_devices_count", { current, max: devicesLimitLabel() });
  }

  function devicesPercent() {
    const current = Number(devicesData?.current_devices ?? devicesData?.devices?.length ?? 0);
    const max = Number(devicesData?.max_devices || 0);
    if (!max || max <= 0) return 100;
    return Math.max(0, Math.min(100, Math.round((current / max) * 100)));
  }

</script>

<main class="content with-nav">
  <Card class="devices-summary-card">
    <div class="devices-summary-head">
      <Smartphone size={28} />
      <span>
        <strong>{t("wa_devices_title")}</strong>
        <small>{devicesCountLabel()}</small>
      </span>
      <Button variant="icon" size="icon" onclick={() => loadDevices(true)} disabled={devicesBusy} aria-label={t("wa_devices_refresh")}>
        <RefreshCw size={18} />
      </Button>
    </div>
    <div class="progress devices-progress">
      <span style={`width: ${devicesPercent()}%`}></span>
    </div>
    {#if subscription?.active && subscription?.max_devices !== 0}
      <Button variant="secondary" class="wide" onclick={openDeviceTopupModal}>
        <Plus size={17} />
        {t("wa_buy_hwid_devices")}
      </Button>
    {/if}
  </Card>

  {#if devicesBusy && !devicesLoaded}
    <Card class="empty-card">{t("wa_devices_loading")}</Card>
  {:else if devicesStatus}
    <Card class="empty-card">
      <p class:error={devicesIsError} class="status-line">{devicesStatus}</p>
    </Card>
  {:else if !devicesData?.devices?.length}
    <Card class="empty-card devices-empty-card">
      <Smartphone size={28} />
      <span>{t("wa_devices_empty")}</span>
      <small>{t("wa_devices_empty_hint", { max: devicesLimitLabel() })}</small>
    </Card>
  {:else}
    <div class="devices-list">
      {#each devicesData.devices as device (device.token || device.index)}
        <Card class="device-card">
          <div class="device-card-head">
            <div class="device-icon"><Smartphone size={20} /></div>
            <span>
              <strong>{device.display_name || t("wa_device_fallback_name", { index: device.index })}</strong>
              <small>{device.platform_label || t("wa_devices_platform_unknown")}</small>
            </span>
          </div>
          <div class="device-meta">
            {#if device.created_at_text}
              <div>
                <span>{t("wa_devices_connected_at")}</span>
                <strong>{device.created_at_text}</strong>
              </div>
            {/if}
            {#if device.hwid_short}
              <div>
                <span>HWID</span>
                <code>{device.hwid_short}</code>
              </div>
            {/if}
            {#if device.user_agent}
              <div class="device-user-agent">
                <span>User Agent</span>
                <small>{device.user_agent}</small>
              </div>
            {/if}
          </div>
          {#if device.can_disconnect}
            <Button variant="outline" class="wide device-disconnect-button" onclick={() => openDeviceDisconnectDialog(device)}>
              <CircleX size={17} />
              {t("wa_devices_disconnect")}
            </Button>
          {/if}
        </Card>
      {/each}
    </div>
  {/if}
</main>
