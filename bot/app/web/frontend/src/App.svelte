<script>
  import { Bitcoin, CreditCard } from "lucide-svelte";
  import { onMount, setContext } from "svelte";
  import { createAuthStore } from "./lib/webapp/stores/authStore.js";
  import { createBillingStore } from "./lib/webapp/stores/billingStore.js";
  import { createDevicesStore } from "./lib/webapp/stores/devicesStore.js";
  import { createAccountStore } from "./lib/webapp/stores/accountStore.js";
  import { Tooltip } from "bits-ui";

  import BrandMark from "./BrandMark.svelte";
  import PreviewBoard from "./PreviewBoard.svelte";
  import AdminPanel from "./admin/AdminPanel.svelte";
  import WebAppShell from "./webapp/WebAppShell.svelte";
  import AuthScreen from "./webapp/auth/AuthScreen.svelte";
  import PaymentDialogs from "./webapp/PaymentDialogs.svelte";
  import TariffDialogs from "./webapp/TariffDialogs.svelte";
  import DevicesScreen from "./webapp/screens/DevicesScreen.svelte";
  import HomeScreen from "./webapp/screens/HomeScreen.svelte";
  import InviteScreen from "./webapp/screens/InviteScreen.svelte";
  import SettingsScreen from "./webapp/screens/SettingsScreen.svelte";

  import {
    LANGUAGE_FLAGS,
    LANGUAGE_LABELS,
    MANUAL_LOGOUT_FLAG_KEY,
    TELEGRAM_MINI_APP_AUTH_TIMEOUT_MS,
    TELEGRAM_SDK_ACTION_TIMEOUT_MS,
    TELEGRAM_SDK_BOOT_TIMEOUT_MS,
    TELEGRAM_WEBAPP_SCRIPT_URL,
    WEBAPP_LANGUAGE_ORDER,
  } from "./lib/webapp/constants.js";
  


  import { applyFavicon, readJsonScript, structuredCloneSafe } from "./lib/webapp/browser.js";
  import { createApiClient } from "./lib/webapp/publicApi.js";
  import { createI18n } from "./lib/webapp/i18n.js";
  import {
    formatCompactNumber,
    formatTrafficGb,
    normalizedEmail,
    telegramName,
  } from "./lib/webapp/formatters.js";
  import {
    activeTariffName,
    buildTariffCatalog,
    priceLabel,
  } from "./lib/webapp/tariffs.js";
  import {
    premiumTitle,
    premiumTrafficPercent,
    trafficPercent,
  } from "./lib/webapp/traffic.js";
  import { buildGravatarUrl } from "./lib/webapp/gravatar.js";
  import { createBillingActions } from "./lib/webapp/billingActions.js";
  import {
    readReferralParam as readReferralParamHelper,
    readTelegramAuthStatus,
    readMagicLoginToken,
    readTelegramLoginWidgetAuthData,
    clearAuthQuery,
    buildTelegramOAuthStartUrl as buildTelegramOAuthStartUrlHelper,
    emailError as emailErrorHelper,
  } from "./lib/webapp/authHelpers.js";
  import {
    clearManualLogoutFlag as clearManualLogoutFlagInStorage,
    clearStoredToken,
    CSRF_COOKIE_NAME,
    isManuallyLoggedOut as readManualLogoutFlag,
    markManualLogout as markManualLogoutInStorage,
    persistToken,
    readCookie,
    readStoredToken,
  } from "./lib/webapp/session.js";
  import { createTelegramSdk } from "./lib/webapp/telegramSdk.js";
  import { mockApi as runMockApi } from "./lib/webapp/mockApi.js";
  import { DEV_MOCK, applyPreviewMock } from "./lib/webapp/previewMock.js";
  import {
    adminSectionFromPath,
    adminUserIdFromPath,
    normalizeSection,
    sectionFromPath,
    syncSectionPath,
  } from "./lib/webapp/routes.js";

  const query = new URLSearchParams(window.location.search);
  applyPreviewMock(query.get("mock"));
  const isPreviewBoard = query.get("preview") === "all";
  const injectedConfig = readJsonScript("webapp-config");
  const injectedI18n = readJsonScript("i18n");
  const isLocalShell =
    window.location.protocol === "file:" ||
    ["", "localhost", "127.0.0.1"].includes(window.location.hostname);
  const MOCK = !injectedConfig && isLocalShell ? DEV_MOCK : null;
  const CFG = {
    ...DEV_MOCK.config,
    ...(MOCK ? MOCK.config : {}),
    ...(injectedConfig || {}),
  };
  const I18N = injectedI18n || {};
  let telegramSdkStatus = "idle";
  let telegramMiniAppInitData = "";

  let mode = isPreviewBoard ? "preview" : "loading";
  let activeTab = "home";
  let screen = "home";
  let data = isPreviewBoard ? structuredCloneSafe(DEV_MOCK.data) : null;
  let selectedPlan = null;
  let selectedMethod = "";
  let trialBusy = false;
  let promoCode = "";
  let promoBusy = false;
  let promoStatus = "";
  let promoIsError = false;
  let promoFieldError = "";
  let toastText = "";
  let toastTimer = null;
  let languageMenuOpen = false;
  let languageClickGuard = false;
  let languageClickGuardArmed = false;
  let languageClickGuardTimer = null;
  let languageClickGuardArmTimer = null;
  let emailAvatarUrl = "";
  let avatarHashToken = "";
  let token = MOCK ? "local-preview" : readStoredToken();
  let csrfToken = MOCK ? "" : readCookie(CSRF_COOKIE_NAME) || "";
  let scrollLockApplied = false;
  let tg = null;
  const telegramSdk = createTelegramSdk({
    scriptUrl: TELEGRAM_WEBAPP_SCRIPT_URL,
    bootTimeoutMs: TELEGRAM_SDK_BOOT_TIMEOUT_MS,
    actionTimeoutMs: TELEGRAM_SDK_ACTION_TIMEOUT_MS,
    miniAppAuthTimeoutMs: TELEGRAM_MINI_APP_AUTH_TIMEOUT_MS,
    onStatusChange: (status) => (telegramSdkStatus = status),
    onInitDataChange: (initData) => (telegramMiniAppInitData = initData || ""),
  });
  tg = telegramSdk.refresh();
  telegramSdkStatus = tg ? "ready" : "idle";
  telegramMiniAppInitData = telegramSdk.initData;
  const i18n = createI18n({
    messages: I18N,
    defaultLang: "ru",
    getLang: () => user?.language_code || CFG.language || "ru",
  });
  const normalizeLangCode = i18n.normalizeLangCode;
  const t = i18n.t;
  const termUnitLabel = i18n.termUnitLabel;
  const languageName = i18n.languageName;
  const apiClient = createApiClient({
    apiBase: CFG.apiBase,
    csrfCookieName: CSRF_COOKIE_NAME,
    getToken: () => token,
    getCsrfToken: () => csrfToken,
    onUnauthorized: () => {
      clearToken();
      showLogin();
    },
    mockApi: MOCK
      ? (path, options, context) => runMockApi(path, options, context)
      : null,
    getMockContext: () => ({ currentLang, normalizeLangCode, clone: structuredCloneSafe }),
  });
  const billing = createBillingActions({ api: (path, options) => apiClient.api(path, options), t: (...args) => t(...args) });

  const authStore = createAuthStore({ publicApi, setToken, loadData, telegramSdk, getTg: () => tg, t, currentLang: () => currentLang, clearManualLogoutFlag });
  const billingStore = createBillingStore({ billing, loadData, t, showToast, openExternalLink, tg });
  const devicesStore = createDevicesStore({ api, t, showToast });
  const accountStore = createAccountStore({
    api,
    publicApi,
    setToken,
    loadData,
    t,
    showToast,
    clearToken,
    markManualLogout,
    showLogin,
    telegramSdk,
    getTg: () => tg,
    telegramOAuthClientId,
    currentLang: () => currentLang,
    normalizeLangCode,
    updateLocalData: (updatedLanguage) => {
      if (!data?.user) return;
      data = { ...data, user: { ...data.user, language_code: updatedLanguage } };
    },
  });

  setContext("authStore", authStore);
  setContext("billingStore", billingStore);
  setContext("devicesStore", devicesStore);
  setContext("accountStore", accountStore);

  $: ({ authStatus, authIsError, authBusy, telegramLoginBusy, loginEmailFieldError, loginEmailTooltipOpen, authResendCooldown, email, pendingEmail, emailCode } = $authStore);
  $: ({ paymentModalOpen, paymentStep, selectedTariffKey, selectedPlan, selectedMethod, topupModalOpen, topupKind, deviceTopupModalOpen, changeModalOpen, topupOptions, deviceTopupOptions, changeOptions, selectedTopupPlan, selectedDeviceTopupPlan, selectedChangeTarget, selectedChangeAction, changeConfirmOpen, tariffActionBusy, payBusy } = $billingStore);
  $: ({ devicesData, devicesLoaded, devicesBusy, devicesStatus, devicesIsError, deviceConfirmOpen, deviceToDisconnect, deviceDisconnectBusy } = $devicesStore);
  $: ({ linkEmailOpen, linkEmailBusy, linkTelegramBusy, linkEmailValue, linkEmailPending, linkEmailCode, linkEmailStatus, linkEmailIsError, linkEmailFieldError, linkEmailResendCooldown, languageBusy } = $accountStore);



  $: brandTitle = CFG.title || "/minishop";
  $: brandEmoji = CFG.logoEmoji || "🫥";
  $: accent = CFG.primaryColor || "#00fe7a";
  $: plans = data?.plans?.length ? data.plans : DEV_MOCK.data.plans;
  $: methods = data?.payment_methods?.length ? data.payment_methods : [];
  $: appSettings = data?.settings || DEV_MOCK.data.settings;
  $: trafficMode = Boolean(appSettings?.traffic_mode);
  $: tariffMode = plans.some((plan) => plan?.tariff_key);
  $: tariffCatalog = buildTariffCatalog(plans);
  $: singleTariffMode = tariffMode && tariffCatalog.length === 1;
  $: hasMultipleTariffs = tariffCatalog.length > 1;
  $: selectedTariff = tariffCatalog.find((tariff) => tariff.key === selectedTariffKey) || null;
  $: selectedTariffPlans = tariffMode ? (selectedTariffKey ? plans.filter((plan) => plan?.tariff_key === selectedTariffKey) : []) : plans;
  $: devicesEnabled = Boolean(appSettings?.my_devices_enabled);
  $: subscription = data?.subscription || DEV_MOCK.data.subscription;
  $: hasActiveTariffSubscription = Boolean(tariffMode && subscription?.active && subscription?.tariff_key);
  $: canChangeTariff = Boolean(hasActiveTariffSubscription && hasMultipleTariffs);
  $: currentTariffName = activeTariffName(subscription, plans);
  $: canOpenRegularTopupModal = Boolean(
    hasActiveTariffSubscription &&
      (subscription?.can_topup_regular_traffic ?? subscription?.can_topup_traffic) &&
      Number(subscription?.traffic_limit_bytes || 0) > 0,
  );
  $: canOpenPremiumTopupModal = Boolean(
    hasActiveTariffSubscription &&
      (subscription?.can_topup_premium_traffic ?? subscription?.can_topup_traffic) &&
      Number(subscription?.premium_limit_bytes || 0) > 0,
  );
  $: canOpenTopupModal = Boolean(canOpenRegularTopupModal || canOpenPremiumTopupModal);
  $: canShowTopupButton = Boolean(
    canOpenTopupModal &&
      (trafficPercent(subscription) >= 85 || premiumTrafficPercent(subscription) >= 85),
  );
  $: user = data?.user || {};
  $: isAdmin = Boolean(user?.is_admin);
  $: if (screen === "admin" && !isAdmin) {
    screen = "settings";
    activeTab = "settings";
  }
  $: referral = data?.referral || DEV_MOCK.data.referral;
  $: currentLang = normalizeLangCode(user?.language_code || CFG.language || "ru");
  $: languageOptions = WEBAPP_LANGUAGE_ORDER.map((code) => ({
    value: code,
    label: LANGUAGE_LABELS[code] || code.toUpperCase(),
    flag: LANGUAGE_FLAGS[code] || "🏳️",
  }));
  $: currentLanguageOption = languageOptions.find((option) => option.value === currentLang) || languageOptions[0];
  $: userLanguage = languageName(currentLang);
  $: telegramLinkStatus = user?.telegram_linked ? t("wa_settings_linked") : t("wa_settings_not_linked");
  $: emailLinkStatus = user?.email ? t("wa_settings_linked") : t("wa_settings_email_not_linked");
  $: hasUnlinkedIdentity = !user?.telegram_linked || !user?.email;
  $: referralBonusDetails = Array.isArray(referral?.bonus_details) ? referral.bonus_details : [];
  $: referralWelcomeBonusDays = Math.max(0, Number(referral?.welcome_bonus_days || 0));
  $: referralOneBonusPerReferee = Boolean(referral?.one_bonus_per_referee);
  $: telegramProfileName = telegramName(user);
  $: profileEmail = user?.email || t("wa_settings_email_not_linked");
  $: profileTelegramId = user?.telegram_id ? `TG ID ${user.telegram_id}` : t("wa_tg_id_not_linked");
  $: profileAvatarUrl = user?.telegram_photo_url || emailAvatarUrl || "";
  $: privacyPolicyUrl = String(CFG.privacyPolicyUrl || "").trim();
  $: userAgreementUrl = String(CFG.userAgreementUrl || "").trim();
  $: supportUrl = String(appSettings?.support_url || CFG.supportUrl || "").trim();
  $: telegramLoginBotId = Number(CFG.telegramLoginBotId || 0);
  $: telegramOAuthClientId = Number(CFG.telegramOAuthClientId || telegramLoginBotId || 0);
  $: telegramMiniAppInitData = tg?.initData || readTelegramMiniAppInitDataFromLocation();
  $: telegramMiniAppAuthAvailable = Boolean(telegramMiniAppInitData);
  $: telegramLoginUnavailable =
    (!telegramMiniAppAuthAvailable && !telegramOAuthClientId && telegramSdkStatus !== "loading");
  $: telegramLoginChecking = telegramLoginBusy || (authBusy && authStatus === t("wa_auth_checking_telegram"));
  $: telegramLoginLabel = telegramLoginUnavailable
    ? t("wa_login_telegram_unavailable_button")
    : telegramLoginChecking
      ? t("wa_auth_checking_telegram")
      : t("wa_login_telegram_button");
  $: telegramLoginUnavailableMessage =
    telegramLoginUnavailable && telegramSdkStatus === "unavailable"
        ? t("wa_auth_telegram_unavailable")
        : telegramLoginUnavailable
          ? t("wa_auth_telegram_not_configured")
          : "";
  $: applyFavicon(CFG.logoUrl, brandEmoji);
  $: syncBodyScrollLock(paymentModalOpen || changeModalOpen || changeConfirmOpen || topupModalOpen || deviceTopupModalOpen || linkEmailOpen);
  $: if (!tariffMode && !$billingStore.selectedPlan && plans.length) {
    billingStore.update((s) => ({ ...s, selectedPlan: plans[Math.min(1, plans.length - 1)] }));
  }
  $: if (singleTariffMode && tariffCatalog[0]?.key && selectedTariffKey !== tariffCatalog[0].key) {
    const tariffKey = tariffCatalog[0].key;
    billingStore.update((s) => ({
      ...s,
      selectedTariffKey: tariffKey,
      selectedPlan: plans.find((plan) => plan?.tariff_key === tariffKey) || null,
      paymentStep: s.paymentStep === "tariff" ? "checkout" : s.paymentStep,
    }));
  }
  $: if (tariffMode && selectedTariffKey && !tariffCatalog.some((tariff) => tariff.key === selectedTariffKey)) {
    billingStore.update((s) => ({
      ...s,
      selectedTariffKey: "",
      selectedPlan: null,
      paymentStep: singleTariffMode ? "checkout" : "tariff",
    }));
  }
  $: if (tariffMode && selectedTariffKey && (!selectedPlan || selectedPlan.tariff_key !== selectedTariffKey)) {
    billingStore.update((s) => ({ ...s, selectedPlan: selectedTariffPlans[0] || null }));
  }
  $: if (!$billingStore.selectedMethod && methods.length) {
    billingStore.update((s) => ({ ...s, selectedMethod: methods[0].id }));
  }
  $: {
    const emailKey = normalizedEmail(user?.email);
    if (!emailKey) {
      avatarHashToken = "";
      emailAvatarUrl = "";
    } else if (avatarHashToken !== emailKey) {
      avatarHashToken = emailKey;
      buildGravatarUrl(emailKey).then((url) => {
        if (avatarHashToken === emailKey) emailAvatarUrl = url;
      });
    }
  }

  onMount(() => {
    if (isPreviewBoard) return;
    const onAnyPointerDown = () => {
      if (mode === "login") loginEmailTooltipOpen = false;
    };
    const onPopState = () => {
      const section = sectionFromPath(window.location.pathname);
      if (mode === "app") {
        if (section === "admin" && isAdmin) {
          screen = "admin";
          return;
        }
        const nextSection = section === "devices" && !devicesEnabled ? "home" : section;
        activeTab = nextSection;
        screen = nextSection;
        if (nextSection === "devices") devicesStore.loadDevices(devicesEnabled);
      }
    };
    window.addEventListener("popstate", onPopState);
    window.addEventListener("pointerdown", onAnyPointerDown);
    boot();
    return () => {
      window.removeEventListener("popstate", onPopState);
      window.removeEventListener("pointerdown", onAnyPointerDown);
      stopTelegramLoginWatchdog();
      clearCooldownTimer("auth");
      clearCooldownTimer("link_email");
      clearLanguageClickGuard();
      syncBodyScrollLock(false);
    };
  });


  function syncBodyScrollLock(locked) {
    if (typeof document === "undefined") return;
    if (locked && !scrollLockApplied) {
      document.body.style.overflow = "hidden";
      scrollLockApplied = true;
      return;
    }
    if (!locked && scrollLockApplied) {
      document.body.style.overflow = "";
      scrollLockApplied = false;
    }
  }

  function clearLanguageClickGuard() {
    if (languageClickGuardTimer) {
      window.clearTimeout(languageClickGuardTimer);
      languageClickGuardTimer = null;
    }
    if (languageClickGuardArmTimer) {
      window.clearTimeout(languageClickGuardArmTimer);
      languageClickGuardArmTimer = null;
    }
    languageClickGuard = false;
    languageClickGuardArmed = false;
  }

  function setLanguageMenuOpen(open) {
    languageMenuOpen = Boolean(open);
    clearLanguageClickGuard();
    if (languageMenuOpen) {
      languageClickGuard = true;
      languageClickGuardArmTimer = window.setTimeout(() => {
        languageClickGuardArmed = true;
        languageClickGuardArmTimer = null;
      }, 220);
      return;
    }
    languageClickGuardTimer = window.setTimeout(() => {
      languageClickGuard = false;
      languageClickGuardTimer = null;
    }, 260);
  }

  function resolveTelegramWebApp() {
    return telegramSdk.tg;
  }

  function refreshTelegramWebApp() {
    tg = telegramSdk.refresh();
    telegramMiniAppInitData = telegramSdk.initData;
    return tg;
  }

  function readTelegramMiniAppInitDataFromLocation() {
    return telegramSdk.readInitDataFromLocation();
  }

  function hasTelegramLaunchParams() {
    return telegramSdk.hasLaunchParams();
  }

  function loadTelegramSdk(timeoutMs = TELEGRAM_SDK_BOOT_TIMEOUT_MS) {
    return telegramSdk.load(timeoutMs).then((value) => {
      tg = value;
      telegramMiniAppInitData = telegramSdk.initData;
      return value;
    });
  }

  async function ensureTelegramSdkForAction() {
    tg = await telegramSdk.ensureForAction();
    telegramMiniAppInitData = telegramSdk.initData;
    return tg;
  }

  function createTelegramMiniAppAuthTimeout() {
    return telegramSdk.createMiniAppAuthTimeout();
  }

  function shouldWaitForTelegramSdkBeforeOAuth() {
    return hasTelegramLaunchParams() || !telegramOAuthClientId;
  }

  async function boot() {
    mode = "loading";
    if (hasTelegramLaunchParams()) await loadTelegramSdk(TELEGRAM_SDK_BOOT_TIMEOUT_MS);

    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch {}
    }

    if (MOCK) {
      await loadData();
      return;
    }

    const magicToken = readMagicLoginToken();
    if (magicToken && (await finalizeMagicLogin(magicToken))) return;

    const telegramAuthStatus = readTelegramAuthStatus();
    if (telegramAuthStatus === "success") {
      clearManualLogoutFlag();
      clearAuthQuery();
      try {
        await loadData();
        return;
      } catch {
        clearToken();
      }
    } else if (telegramAuthStatus) {
      clearAuthQuery();
      setAuthStatus(
        telegramAuthStatus === "cancelled" ? t("wa_auth_telegram_cancelled") : t("wa_auth_telegram_not_confirmed"),
        true,
      );
    }

    if (isManuallyLoggedOut()) {
      showLogin();
      return;
    }

    const widgetAuthData = readTelegramLoginWidgetAuthData();
    if (widgetAuthData && (await finalizeTelegramAuth(widgetAuthData, "auth_data"))) return;

    const initData = telegramMiniAppInitData || tg?.initData || readTelegramMiniAppInitDataFromLocation();
    if (initData) {
      try {
        if (await finalizeTelegramAuth(initData, "init_data")) return;
      } catch {}
    }

    if (token || csrfToken) {
      try {
        await loadData();
        return;
      } catch {
        clearToken();
      }
    }

    showLogin();
  }

  async function loadData() {
    const payload = await api("/me");
    if (!payload.ok) throw new Error(payload.error || "load_failed");
    data = payload;
    billingStore.update((s) => ({
      ...s,
      selectedPlan: null,
      selectedTariffKey: "",
      paymentStep: "tariff",
      selectedMethod: payload.payment_methods?.[0]?.id || "",
    }));
    let section = MOCK && query.get("screen") ? normalizeSection(query.get("screen")) : sectionFromPath(window.location.pathname);
    if (section === "admin" && !payload.user?.is_admin) section = "settings";
    if (section === "devices" && !payload.settings?.my_devices_enabled) section = "home";
    activeTab = section === "admin" ? "settings" : section;
    screen = section;
    mode = "app";
    syncSectionPath(
      section,
      true,
      section === "admin" ? adminSectionFromPath(window.location.pathname) : null,
    );
    if (section === "devices" && payload.settings?.my_devices_enabled) {
      await devicesStore.loadDevices(true);
    }
    if (topupModalOpen) await billingStore.loadTopupOptions(topupKind);
    if (deviceTopupModalOpen) await billingStore.loadDeviceTopupOptions();
    if (changeModalOpen) await billingStore.loadTariffChangeOptions();
  }

  function showLogin() {
    mode = "login";
    screen = "login";
    activeTab = "home";
  }

  async function api(path, options = {}) {
    return apiClient.api(path, options);
  }

  async function publicApi(path, payload = {}, options = {}) {
    return apiClient.publicApi(path, payload, options);
  }

  function setToken(nextToken, nextCsrf = "") {
    clearManualLogoutFlag();
    token = nextToken || "";
    csrfToken = nextCsrf || readCookie(CSRF_COOKIE_NAME) || "";
    if (token && !MOCK) persistToken(token);
  }

  function clearToken() {
    token = "";
    csrfToken = "";
    clearStoredToken();
  }

  function markManualLogout() {
    markManualLogoutInStorage(MANUAL_LOGOUT_FLAG_KEY);
  }

  function clearManualLogoutFlag() {
    clearManualLogoutFlagInStorage(MANUAL_LOGOUT_FLAG_KEY);
  }

  function isManuallyLoggedOut() {
    return readManualLogoutFlag(MANUAL_LOGOUT_FLAG_KEY);
  }

  function readReferralParam() {
    return readReferralParamHelper(tg);
  }

  function buildTelegramOAuthStartUrl(purpose = "login") {
    return buildTelegramOAuthStartUrlHelper(purpose, tg);
  }

  function emailError(error, fallback) {
    return emailErrorHelper(error, fallback, t);
  }

  

  

  

  

  

  

  function submitEmailOnEnter(event) {
    if (event.key !== "Enter") return;
    event.preventDefault();
    authStore.requestEmailCode((s) => (screen = s));
  }

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  function openExternalLink(url) {
    if (!url) return;
    if (tg?.openLink) {
      tg.openLink(url);
      return;
    }
    window.location.assign(url);
  }

  function openTelegramInvoice(url) {
    if (!url) return;
    if (tg?.openInvoice) {
      tg.openInvoice(url, (status) => {
        if (status === "paid") {
          showToast(t("wa_payment_success", {}, "Payment successful"));
          loadData();
        } else if (status === "failed") {
          showToast(t("wa_payment_create_failed"));
        }
      });
      return;
    }
    openExternalLink(url);
  }

  function openConnectLink() {
    const url = subscription?.connect_url || subscription?.config_link;
    if (!url) {
      showToast(t("wa_connect_link_unavailable"));
      return;
    }
    openExternalLink(url);
  }

  async function copyText(value, success = t("wa_copied")) {
    if (!value) {
      showToast(t("wa_unavailable"));
      return;
    }
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      const area = document.createElement("textarea");
      area.value = value;
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    showToast(success);
  }

  async function applyPromo() {
    const code = promoCode.trim();
    if (!code) {
      promoFieldError = t("wa_promo_enter");
      return;
    }
    promoFieldError = "";
    promoBusy = true;
    promoStatus = "";
    try {
      const response = await api("/promo/apply", {
        method: "POST",
        body: JSON.stringify({ code }),
      });
      if (!response.ok) throw response;
      promoCode = "";
      promoStatus = response.end_date_text
        ? t("wa_promo_activated_until", { date: response.end_date_text })
        : t("wa_promo_activated");
      promoIsError = false;
      await loadData();
    } catch (error) {
      promoStatus = error?.message || t("wa_promo_activation_failed");
      promoIsError = true;
      promoFieldError = promoStatus;
    } finally {
      promoBusy = false;
    }
  }

  async function activateTrial() {
    if (trialBusy) return;
    trialBusy = true;
    try {
      const response = await api("/trial/activate", {
        method: "POST",
        body: JSON.stringify({}),
      });
      if (!response.ok) throw response;
      showToast(t("wa_trial_activated"));
      await loadData();
    } catch (error) {
      showToast(error?.message || t("wa_trial_activation_failed"));
    } finally {
      trialBusy = false;
    }
  }

  

  

  

  

  

  function showToast(message) {
    toastText = message;
    if (toastTimer) window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
      toastText = "";
    }, 2400);
  }

  function goHome() {
    billingStore.closePaymentModal();
    activeTab = "home";
    screen = "home";
    syncSectionPath("home");
  }

  function goInvite() {
    billingStore.closePaymentModal();
    activeTab = "invite";
    screen = "invite";
    syncSectionPath("invite");
  }

  function goDevices() {
    if (!devicesEnabled) return;
    billingStore.closePaymentModal();
    activeTab = "devices";
    screen = "devices";
    syncSectionPath("devices");
    devicesStore.loadDevices(devicesEnabled);
  }

  function defaultPaymentMethod() {
    return methods[0]?.id || "";
  }

  function openPaymentModal() {
    billingStore.openPaymentModal(tariffMode, singleTariffMode, tariffCatalog, subscription, plans, defaultPaymentMethod());
  }

  function openTopupModal(kind) {
    billingStore.openTopupModal(kind, defaultPaymentMethod());
  }

  function openRegularTopupModal() {
    openTopupModal("regular");
  }

  function openPremiumTopupModal() {
    openTopupModal("premium");
  }

  function openTariffChangeModal() {
    billingStore.openTariffChangeModal(defaultPaymentMethod());
  }

  function openDeviceTopupModal() {
    billingStore.openDeviceTopupModal(defaultPaymentMethod());
  }

  function closeDeviceTopupModal() {
    billingStore.closeDeviceTopupModal();
  }

  function loadDevices(force = false) {
    return devicesStore.loadDevices(devicesEnabled, force);
  }

  function disconnectDevice() {
    return devicesStore.disconnectDevice(devicesEnabled);
  }

  function goSettings() {
    billingStore.closePaymentModal();
    activeTab = "settings";
    screen = "settings";
    syncSectionPath("settings");
  }

  function openAdminPanel() {
    if (!isAdmin) return;
    clearLanguageClickGuard();
    billingStore.closePaymentModal();
    activeTab = "settings";
    screen = "admin";
    syncSectionPath("admin", false, adminSectionFromPath(window.location.pathname));
  }

  function closeAdminPanel() {
    screen = "settings";
    activeTab = "settings";
    syncSectionPath("settings");
  }

  function handleAdminSectionChange(adminSection, adminUserId = null) {
    if (screen !== "admin") return;
    if (window.location.protocol === "file:") return;
    const targetPath = adminSection === "users" && adminUserId
      ? `/admin/users/${adminUserId}`
      : `/admin/${adminSection}`;
    if (window.location.pathname === targetPath) return;
    window.history.pushState(null, "", `${targetPath}${window.location.search}${window.location.hash}`);
  }

  async function handleTariffsSaved() {
    billingStore.update((s) => ({ ...s, topupOptions: null, deviceTopupOptions: null, changeOptions: null }));
    try {
      await loadData();
    } catch {
      // The admin save already succeeded; a later app refresh will pick up the new catalog.
    }
  }

  async function handleSettingsSaved() {
    billingStore.update((s) => ({ ...s, topupOptions: null, deviceTopupOptions: null, changeOptions: null }));
    try {
      await loadData();
    } catch {
      // Settings were saved; the next app refresh will pick up the runtime values.
    }
  }

  

  

  

  

  

  

  

  

  function methodMeta(method) {
    const id = String(method?.id || "").toLowerCase();
    if (id.includes("platega_sbp")) {
      return { title: t("wa_method_platega_sbp_card"), icon: CreditCard };
    }
    if (id.includes("platega_crypto")) {
      return { title: t("wa_method_platega_crypto"), icon: Bitcoin };
    }
    if (id.includes("yookassa") || id.includes("card")) {
      return { title: t("pay_with_yookassa_button"), icon: null };
    }
    if (id.includes("severpay")) {
      return { title: t("pay_with_severpay_button"), icon: null };
    }
    if (id.includes("freekassa")) {
      return { title: t("pay_with_sbp_button"), icon: null };
    }
    if (id.includes("cryptopay")) {
      return { title: t("pay_with_cryptopay_button"), icon: null };
    }
    if (id.includes("stars")) {
      return { title: t("pay_with_stars_button"), icon: null };
    }
    if (id.includes("sbp")) {
      return { title: t("pay_with_sbp_button"), icon: null };
    }
    if (id.includes("crypto")) {
      return { title: t("pay_with_cryptopay_button"), icon: null };
    }
    return { title: t("wa_method_other_title"), icon: null };
  }

  function selectTariff(tariff) {
    billingStore.selectTariff(tariff, plans);
  }

  function continueWithSelectedTariff() {
    billingStore.continueWithSelectedTariff(selectedTariffPlans);
  }

  function backToTariffList() {
    billingStore.backToTariffList(subscription, tariffCatalog);
  }

  function paymentTitle() {
    if (singleTariffMode) {
      return selectedTariff?.billing_model === "traffic" ? t("wa_traffic_packages_title") : t("wa_subscription_title");
    }
    if (tariffMode) return t("wa_tariffs_title");
    return trafficMode ? t("wa_traffic_packages_title") : t("wa_subscription_title");
  }

  function paymentDescription() {
    if (tariffMode) {
      if (singleTariffMode) {
        return selectedTariff?.billing_model === "traffic" ? t("wa_traffic_packages_choose") : t("wa_subscription_choose_period");
      }
      return paymentStep === "checkout" && selectedTariff
        ? t("wa_tariff_choose_period_payment", { tariff: selectedTariff.title })
        : t("wa_tariffs_choose");
    }
    return trafficMode ? t("wa_traffic_packages_choose") : t("wa_subscription_choose_period");
  }

  function primaryPayActionLabel() {
    if (trafficMode || selectedPlan?.sale_mode === "traffic_package") return t("wa_buy_traffic");
    return subscription.active ? t("wa_renew") : t("wa_pay_subscription");
  }

  function changeActionTitle(action) {
    const mode = String(action?.mode || "");
    if (mode === "recalc_days") {
      return t("wa_tariff_change_recalc_days", { days: Number(action?.days_after || 0) });
    }
    if (mode === "convert_days_to_gb") {
      return t("wa_tariff_change_convert_gb", { gb: formatCompactNumber(action?.converted_gb || 0) });
    }
    if (mode === "paid_diff") {
      return t("wa_tariff_change_pay_diff", { price: priceLabel(action) });
    }
    if (mode === "buy_package") {
      return t("wa_tariff_change_buy_package", { gb: formatCompactNumber(action?.traffic_gb || 0), price: priceLabel(action) });
    }
    if (mode === "buy_period") {
      return `${action?.title || ""} · ${priceLabel(action)}`;
    }
    return action?.title || mode;
  }

  function tariffChangeSummary() {
    if (!selectedChangeTarget || !selectedChangeAction) return [];
    const rows = [
      t("wa_tariff_change_confirm_target", { tariff: selectedChangeTarget.title }),
      t("wa_tariff_change_confirm_action", { action: changeActionTitle(selectedChangeAction) }),
    ];
    const mode = String(selectedChangeAction.mode || "");
    if (mode === "recalc_days") {
      rows.push(t("wa_tariff_change_confirm_recalc", { days: Number(selectedChangeAction.days_after || 0) }));
    } else if (mode === "convert_days_to_gb") {
      rows.push(t("wa_tariff_change_confirm_convert", { gb: formatCompactNumber(selectedChangeAction.converted_gb || 0) }));
    } else if (selectedChangeAction.kind === "payment") {
      rows.push(t("wa_tariff_change_confirm_payment", { price: priceLabel(selectedChangeAction) }));
    }
    return rows;
  }

  function topupWarningText() {
    const percent = Number(topupOptions?.traffic_percent || trafficPercent(subscription));
    const levels = topupOptions?.warning_levels?.length ? topupOptions.warning_levels.join(" / ") : "85 / 90 / 95";
    if (percent >= 95) return t("wa_topup_warning_critical", { percent, levels });
    if (percent >= 90) return t("wa_topup_warning_high", { percent, levels });
    if (percent >= 85) return t("wa_topup_warning_medium", { percent, levels });
    return t("wa_topup_warning_levels", { levels });
  }

  function topupModalDescription() {
    if (!topupOptions) return "";
    if (isPremiumTopupContext()) return topupOptions?.tariff_name ? t("wa_topup_for_tariff", { tariff: topupOptions.tariff_name }) : "";
    if (singleTariffMode) return "";
    return topupOptions?.tariff_name ? t("wa_topup_for_tariff", { tariff: topupOptions.tariff_name }) : "";
  }

  function isPremiumTopupContext() {
    if (selectedTopupPlan?.sale_mode === "premium_topup") return true;
    if (topupOptions?.topup_kind) return topupOptions.topup_kind === "premium";
    return topupKind === "premium";
  }

  function topupModalTitle() {
    if (isPremiumTopupContext()) return premiumTitle(topupOptions || subscription);
    return t("wa_topup_traffic");
  }

  function topupCarryoverNotes() {
    const plans = topupOptions?.plans || [];
    if (!plans.length) return [];
    return [
      t(
        "wa_topup_carryover",
        {},
        "Докупленный трафик не сгорает: сначала расходуется месячный лимит, затем докупленный остаток."
      ),
    ];
  }

  function deviceTopupModalDescription() {
    if (!deviceTopupOptions) return "";
    return deviceTopupOptions?.tariff_name ? t("wa_device_topup_for_tariff", { tariff: deviceTopupOptions.tariff_name }) : "";
  }

  function tariffChangeModalDescription() {
    if (!changeOptions) return "";
    return changeOptions?.current ? t("wa_current_tariff", { tariff: changeOptions.current.title }) : "";
  }

  function trialTrafficLabel() {
    const limit = Number(appSettings?.trial_traffic_limit_gb || 0);
    return limit > 0 ? formatTrafficGb(limit) : t("wa_unlimited_traffic");
  }

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

<svelte:head>
  <title>{brandTitle}</title>
</svelte:head>

<Tooltip.Provider>
  {#key currentLang}
    {#if isPreviewBoard}
      <PreviewBoard config={CFG} mockData={DEV_MOCK.data} />
    {:else}
      <div class="app-shell" style={`--accent: ${accent};`}>
      {#if mode === "loading"}
        <div class="loader">
          <BrandMark class="brand-mark-lg" logoUrl={CFG.logoUrl} emoji={brandEmoji} />
          <div>{t("wa_loading")}</div>
        </div>
      {:else if mode === "login"}
        <AuthScreen
          {screen}
          {CFG}
          {brandTitle}
          {brandEmoji}
          bind:email={$authStore.email}
          bind:emailCode={$authStore.emailCode}
          {pendingEmail}
          {authStatus}
          {authIsError}
          {authBusy}
          {authResendCooldown}
          {loginEmailFieldError}
          {loginEmailTooltipOpen}
          {telegramLoginBusy}
          {telegramLoginUnavailable}
          {telegramLoginChecking}
          {telegramLoginLabel}
          {telegramLoginUnavailableMessage}
          {privacyPolicyUrl}
          {userAgreementUrl}
          {t}
          requestEmailCode={() => authStore.requestEmailCode((s) => (screen = s))}
          verifyEmailCode={authStore.verifyEmailCode}
          openTelegramLogin={() => authStore.openTelegramLogin(telegramOAuthClientId, () => telegramMiniAppInitData)}
          {openExternalLink}
          {submitEmailOnEnter}
          onBackToLogin={() => (screen = "login")}
          clearLoginEmailError={() => {
            loginEmailFieldError = "";
            loginEmailTooltipOpen = false;
          }}
        />
    {:else if screen === "admin" && isAdmin}
      <AdminPanel
        api={api}
        onClose={closeAdminPanel}
        onToast={(text) => showToast(text)}
        initialSection={adminSectionFromPath(window.location.pathname)}
        initialUserId={adminUserIdFromPath(window.location.pathname)}
        onSectionChange={handleAdminSectionChange}
        onSettingsSaved={handleSettingsSaved}
        onTariffsSaved={handleTariffsSaved}
        brandTitle={brandTitle}
        logoUrl={CFG.logoUrl}
        logoEmoji={brandEmoji}
        appVersion={CFG.appVersion}
        appRepositoryUrl={CFG.appRepositoryUrl}
        currentLang={currentLang}
        languageOptions={languageOptions}
        languageBusy={languageBusy}
        onLanguageChange={accountStore.updateAccountLanguage}
        t={t}
      />
    {:else}
      <WebAppShell
        {screen}
        {activeTab}
        {CFG}
        {brandTitle}
        {brandEmoji}
        {devicesEnabled}
        {hasUnlinkedIdentity}
        {isAdmin}
        {openAdminPanel}
        {goDevices}
        {goHome}
        {goInvite}
        {goSettings}
        {t}
      >
        {#if screen === "home"}
          <HomeScreen
            {CFG}
            {appSettings}
            {brandEmoji}
            {brandTitle}
            {canChangeTariff}
            {canOpenPremiumTopupModal}
            {canOpenRegularTopupModal}
            {canShowTopupButton}
            {currentTariffName}
            {hasActiveTariffSubscription}
            {hasMultipleTariffs}
            {subscription}
            {termUnitLabel}
            {trafficMode}
            {trialBusy}
            {activateTrial}
            {openConnectLink}
            {openPaymentModal}
            {openRegularTopupModal}
            {openPremiumTopupModal}
            {openTariffChangeModal}
            {primaryPayActionLabel}
            {t}
          />
        {:else if screen === "invite"}
          <InviteScreen
            {referral}
            {referralBonusDetails}
            {referralOneBonusPerReferee}
            {referralWelcomeBonusDays}
            bind:promoCode
            bind:promoFieldError
            {promoBusy}
            {promoIsError}
            {promoStatus}
            {applyPromo}
            clearPromoFieldError={() => (promoFieldError = "")}
            {copyText}
            {t}
          />
        {:else if screen === "devices"}
          <DevicesScreen
            {devicesBusy}
            {devicesData}
            {devicesIsError}
            {devicesLoaded}
            {devicesStatus}
            {subscription}
            {loadDevices}
            openDeviceDisconnectDialog={devicesStore.openDeviceDisconnectDialog}
            {openDeviceTopupModal}
            {t}
          />
        {:else if screen === "settings"}
          <SettingsScreen
            {currentLang}
            {currentLanguageOption}
            {emailLinkStatus}
            {isAdmin}
            {languageBusy}
            {languageClickGuard}
            {languageClickGuardArmed}
            bind:languageMenuOpen
            {languageOptions}
            {linkEmailBusy}
            {linkTelegramBusy}
            {privacyPolicyUrl}
            {profileAvatarUrl}
            {profileEmail}
            {profileTelegramId}
            {supportUrl}
            {telegramProfileName}
            {user}
            {userAgreementUrl}
            {userLanguage}
            linkTelegramAccount={accountStore.linkTelegramAccount}
            logout={accountStore.logout}
            {openAdminPanel}
            {openExternalLink}
            openLinkEmailDialog={accountStore.openLinkEmailDialog}
            {setLanguageMenuOpen}
            {t}
            updateAccountLanguage={accountStore.updateAccountLanguage}
          />
        {/if}
      </WebAppShell>

      <PaymentDialogs
        bind:linkEmailCode={$accountStore.linkEmailCode}
        bind:linkEmailFieldError={$accountStore.linkEmailFieldError}
        bind:linkEmailValue={$accountStore.linkEmailValue}
        bind:paymentModalOpen={$billingStore.paymentModalOpen}
        bind:paymentStep={$billingStore.paymentStep}
        bind:selectedMethod={$billingStore.selectedMethod}
        bind:selectedPlan={$billingStore.selectedPlan}
        bind:selectedTariffKey={$billingStore.selectedTariffKey}
        createPayment={billingStore.createPayment}
        {deviceConfirmOpen}
        {deviceDisconnectBusy}
        {deviceToDisconnect}
        {disconnectDevice}
        {linkEmailBusy}
        {linkEmailIsError}
        {linkEmailOpen}
        {linkEmailPending}
        {linkEmailResendCooldown}
        {linkEmailStatus}
        {hasMultipleTariffs}
        {methods}
        {payBusy}
        {plans}
        {selectedTariff}
        {selectedTariffPlans}
        {singleTariffMode}
        {subscription}
        {tariffCatalog}
        {tariffMode}
        closeDeviceDisconnectDialog={devicesStore.closeDeviceDisconnectDialog}
        closeLinkEmailDialog={accountStore.closeLinkEmailDialog}
        closePaymentModal={billingStore.closePaymentModal}
        {backToTariffList}
        {continueWithSelectedTariff}
        requestLinkEmailCode={accountStore.requestLinkEmailCode}
        {selectTariff}
        {t}
        {termUnitLabel}
        verifyLinkEmailCode={accountStore.verifyLinkEmailCode}
      />

      <TariffDialogs
        bind:changeConfirmOpen={$billingStore.changeConfirmOpen}
        bind:changeModalOpen={$billingStore.changeModalOpen}
        bind:deviceTopupModalOpen={$billingStore.deviceTopupModalOpen}
        bind:selectedChangeAction={$billingStore.selectedChangeAction}
        bind:selectedChangeTarget={$billingStore.selectedChangeTarget}
        bind:selectedDeviceTopupPlan={$billingStore.selectedDeviceTopupPlan}
        bind:selectedMethod={$billingStore.selectedMethod}
        bind:selectedTopupPlan={$billingStore.selectedTopupPlan}
        bind:topupModalOpen={$billingStore.topupModalOpen}
        applyTariffChange={billingStore.applyTariffChange}
        {changeOptions}
        {closeDeviceTopupModal}
        closeTariffChangeConfirm={billingStore.closeTariffChangeConfirm}
        closeTariffChangeModal={billingStore.closeTariffChangeModal}
        closeTopupModal={billingStore.closeTopupModal}
        createDeviceTopupPayment={billingStore.createDeviceTopupPayment}
        createTopupPayment={billingStore.createTopupPayment}
        {deviceTopupOptions}
        {methods}
        openTariffChangeConfirm={billingStore.openTariffChangeConfirm}
        {payBusy}
        {singleTariffMode}
        {subscription}
        {tariffActionBusy}
        {topupKind}
        {topupOptions}
        {trafficMode}
        {t}
        {termUnitLabel}
      />
    {/if}

    {#if toastText}
      <div class="toast" role="status">{toastText}</div>
      {/if}
      </div>
    {/if}
  {/key}
</Tooltip.Provider>
