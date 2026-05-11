import { writable, get } from "svelte/store";

export function createDevicesStore({ api, t, showToast }) {
  const state = writable({
    devicesData: null,
    devicesLoaded: false,
    devicesBusy: false,
    devicesStatus: "",
    devicesIsError: false,
    deviceConfirmOpen: false,
    deviceToDisconnect: null,
    deviceDisconnectBusy: false,
  });

  async function loadDevices(devicesEnabled, force = false) {
    const s = get(state);
    if (!devicesEnabled || s.devicesBusy || (s.devicesLoaded && !force)) return;
    state.update(s => ({ ...s, devicesBusy: true, devicesStatus: "", devicesIsError: false }));
    try {
      const response = await api("/devices");
      if (!response?.ok) throw response;
      state.update(s => ({ ...s, devicesData: response, devicesLoaded: true }));
    } catch (error) {
      state.update(s => ({ 
        ...s, 
        devicesStatus: error?.message || t("wa_devices_load_failed"), 
        devicesIsError: true, 
        devicesLoaded: true 
      }));
    } finally {
      state.update(s => ({ ...s, devicesBusy: false }));
    }
  }

  function openDeviceDisconnectDialog(device) {
    state.update(s => ({ ...s, deviceToDisconnect: device, deviceConfirmOpen: true }));
  }

  function closeDeviceDisconnectDialog() {
    const s = get(state);
    if (s.deviceDisconnectBusy) return;
    state.update(s => ({ ...s, deviceConfirmOpen: false, deviceToDisconnect: null }));
  }

  async function disconnectDevice(devicesEnabled) {
    const s = get(state);
    const token = String(s.deviceToDisconnect?.token || "").trim();
    if (!token || s.deviceDisconnectBusy) return;
    state.update(s => ({ ...s, deviceDisconnectBusy: true }));
    try {
      const response = await api("/devices/disconnect", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      if (!response?.ok) throw response;
      showToast(t("wa_device_disconnected"));
      state.update(s => ({ ...s, deviceConfirmOpen: false, deviceToDisconnect: null, devicesLoaded: false }));
      await loadDevices(devicesEnabled, true);
    } catch (error) {
      showToast(error?.message || t("wa_device_disconnect_failed"));
    } finally {
      state.update(s => ({ ...s, deviceDisconnectBusy: false }));
    }
  }

  function devicesLimitLabel() {
    const s = get(state);
    const value = s.devicesData?.max_devices;
    const numeric = Number(value ?? 0);
    if (!Number.isFinite(numeric) || numeric <= 0) return t("wa_devices_unlimited");
    return String(Math.trunc(numeric));
  }

  function devicesCountLabel() {
    const s = get(state);
    const current = Number(s.devicesData?.current_devices ?? s.devicesData?.devices?.length ?? 0);
    return t("wa_devices_count", { current, max: devicesLimitLabel() });
  }

  function devicesPercent() {
    const s = get(state);
    const current = Number(s.devicesData?.current_devices ?? s.devicesData?.devices?.length ?? 0);
    const max = Number(s.devicesData?.max_devices || 0);
    if (!max || max <= 0) return 100;
    return Math.max(0, Math.min(100, Math.round((current / max) * 100)));
  }

  return {
    subscribe: state.subscribe,
    set: state.set,
    update: state.update,
    loadDevices,
    openDeviceDisconnectDialog,
    closeDeviceDisconnectDialog,
    disconnectDevice,
    devicesLimitLabel,
    devicesCountLabel,
    devicesPercent,
  };
}
