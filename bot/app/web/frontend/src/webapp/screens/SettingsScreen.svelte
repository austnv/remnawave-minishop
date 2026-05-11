<script>
  import { ArrowRight, Check, CheckCircle2, ChevronsUpDown, FileText, Globe2, Mail, Send, Shield, UserRound } from "lucide-svelte";
  import { Select } from "bits-ui";

  import Button from "../../lib/components/ui/button.svelte";
  import Card from "../../lib/components/ui/card.svelte";

  export let currentLang = "ru";
  export let currentLanguageOption = null;
  export let emailLinkStatus = "";
  export let isAdmin = false;
  export let languageBusy = false;
  export let languageClickGuard = false;
  export let languageClickGuardArmed = false;
  export let languageMenuOpen = false;
  export let languageOptions = [];
  export let linkEmailBusy = false;
  export let linkTelegramBusy = false;
  export let privacyPolicyUrl = "";
  export let profileAvatarUrl = "";
  export let profileEmail = "";
  export let profileTelegramId = "";
  export let supportUrl = "";
  export let telegramProfileName = "";
  export let user = {};
  export let userAgreementUrl = "";
  export let userLanguage = "";

  export let linkTelegramAccount = () => {};
  export let logout = () => {};
  export let openAdminPanel = () => {};
  export let openExternalLink = () => {};
  export let openLinkEmailDialog = () => {};
  export let setLanguageMenuOpen = () => {};
  export let t = (key) => key;
  export let updateAccountLanguage = () => {};
</script>

<main class="content with-nav">
  <Card class="settings-profile">
    <div class="settings-avatar">
      {#if profileAvatarUrl}
        <img src={profileAvatarUrl} alt={t("wa_settings_avatar_alt")} loading="lazy" referrerpolicy="no-referrer" />
      {:else}
        <UserRound size={30} />
      {/if}
    </div>
    <div class="settings-profile-meta">
      <strong>{telegramProfileName}</strong>
      <small>{profileEmail}</small>
      <small>{profileTelegramId}</small>
    </div>
  </Card>
  {#if isAdmin}
    <div class="settings-admin-block">
      <div class="settings-divider" aria-hidden="true"></div>
      <button class="settings-row settings-row-admin" type="button" on:click={openAdminPanel}>
        <Shield size={21} />
        <span>
          <strong>Админ-панель</strong>
          <small>Управление приложением</small>
        </span>
        <ArrowRight size={17} />
      </button>
    </div>
  {/if}
  <div class="settings-links-block">
    <div class="settings-divider" aria-hidden="true"></div>
    {#if user?.telegram_linked}
      <div class="settings-row settings-row-linked">
        <CheckCircle2 size={21} />
        <span>
          <strong>{t("wa_settings_telegram_linked_title")}</strong>
          <small>{profileTelegramId}</small>
        </span>
      </div>
    {:else}
      <Button
        variant="telegram"
        class="wide settings-telegram-link-btn attention-wrap"
        onclick={linkTelegramAccount}
        disabled={linkTelegramBusy}
      >
        <span class="attention-dot" aria-hidden="true"></span>
        <Send size={18} />
        {t("wa_settings_link_telegram_action")}
      </Button>
    {/if}
    {#if user?.email}
      <div class="settings-row settings-row-linked">
        <CheckCircle2 size={21} />
        <span>
          <strong>{t("wa_settings_email_linked_title")}</strong>
          <small>{user?.email}</small>
        </span>
      </div>
    {:else}
      <button class="settings-row attention-wrap" type="button" on:click={openLinkEmailDialog} disabled={linkEmailBusy}>
        <span class="attention-dot" aria-hidden="true"></span>
        <Mail size={21} />
        <span>
          <strong>{t("wa_settings_link_email_action")}</strong>
          <small>{emailLinkStatus}</small>
        </span>
        <ArrowRight size={17} />
      </button>
    {/if}
    <div class="settings-divider" aria-hidden="true"></div>
  </div>
  {#if languageMenuOpen || languageClickGuard}
    <button
      class="language-select-guard"
      class:language-select-guard--armed={languageClickGuardArmed}
      type="button"
      aria-label={t("wa_close")}
      on:pointerdown|preventDefault|stopPropagation={() => languageClickGuardArmed && setLanguageMenuOpen(false)}
      on:click|preventDefault|stopPropagation={() => languageClickGuardArmed && setLanguageMenuOpen(false)}
    ></button>
  {/if}
  <div class="settings-list" class:settings-list--language-open={languageMenuOpen}>
    <div class="settings-row settings-row-language">
      <Globe2 size={21} />
      <Select.Root
        type="single"
        bind:open={languageMenuOpen}
        value={currentLang}
        items={languageOptions}
        disabled={languageBusy}
        onOpenChange={setLanguageMenuOpen}
        onValueChange={updateAccountLanguage}
      >
        <Select.Trigger class="language-select-trigger" aria-label={t("wa_settings_language")}>
          <span class="language-select-copy">
            <strong>{t("wa_settings_language")}</strong>
            <small class="language-select-current">
              <span class="emoji-flag" aria-hidden="true">{currentLanguageOption?.flag || "🏳️"}</span>
              {currentLanguageOption?.label || userLanguage}
            </small>
          </span>
          <ChevronsUpDown size={16} />
        </Select.Trigger>
        <Select.Content class="language-select-content" side="bottom" align="end" sideOffset={6}>
          <Select.Viewport class="language-select-viewport">
            {#each languageOptions as option (option.value)}
              <Select.Item value={option.value} label={option.label} class="language-select-item">
                <span class="language-select-item-main">
                  <span class="emoji-flag" aria-hidden="true">{option.flag}</span>
                  <span>{option.label}</span>
                </span>
                <Check size={15} class="language-select-item-check" />
              </Select.Item>
            {/each}
          </Select.Viewport>
        </Select.Content>
      </Select.Root>
    </div>
    {#if supportUrl}
      <button class="settings-row settings-row-support" type="button" on:click={() => openExternalLink(supportUrl)}>
        <Send size={21} />
        <span><strong>{t("menu_support_button")}</strong></span>
        <ArrowRight size={17} />
      </button>
    {/if}
    {#if userAgreementUrl}
      <button class="settings-row settings-row-policy" type="button" on:click={() => openExternalLink(userAgreementUrl)}>
        <FileText size={21} />
        <span><strong>{t("wa_settings_user_agreement")}</strong></span>
        <ArrowRight size={17} />
      </button>
    {/if}
    {#if privacyPolicyUrl}
      <button class="settings-row settings-row-policy" type="button" on:click={() => openExternalLink(privacyPolicyUrl)}>
        <Shield size={21} />
        <span><strong>{t("wa_settings_privacy_policy")}</strong></span>
        <ArrowRight size={17} />
      </button>
    {/if}
    <button class="settings-row settings-row-logout" type="button" on:click={logout}>
      <UserRound size={21} />
      <span><strong>{t("wa_logout")}</strong><small>{t("wa_end_session")}</small></span>
      <ArrowRight size={17} />
    </button>
  </div>
</main>
