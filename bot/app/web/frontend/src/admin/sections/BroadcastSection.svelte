<script>
  import { Send, ChevronDown, Check } from "lucide-svelte";
  import { getContext } from "svelte";
  import { Label, Select } from "bits-ui";

  export let at;
  export let optionLabel;

  const broadcastStore = getContext("broadcastStore");

  $: ({
    broadcastTarget,
    broadcastText,
    broadcastBusy,
    broadcastResult,
  } = $broadcastStore);

  const BROADCAST_TARGET_OPTIONS = broadcastStore.BROADCAST_TARGET_OPTIONS;
</script>

<div class="admin-card">
  <header class="admin-card-head">
    <h3>{at("broadcast_title", {}, "Рассылка")}</h3>
    <small>{at("broadcast_subtitle", {}, "Доставка через очередь сообщений")}</small>
  </header>
  <div class="admin-card-body">
    <div class="admin-form">
      <Label.Root class="admin-field-label">
        <span>{at("broadcast_label_audience", {}, "Аудитория")}</span>
        <Select.Root type="single" value={broadcastTarget} onValueChange={(value) => broadcastStore.updateField({ broadcastTarget: value })}>
          <Select.Trigger class="admin-select-trigger" aria-label={at("broadcast_label_audience", {}, "Аудитория")}>
            <span>{optionLabel(BROADCAST_TARGET_OPTIONS, broadcastTarget)}</span>
            <ChevronDown size={14} class="admin-select-icon" />
          </Select.Trigger>
          <Select.Portal>
            <Select.Content class="admin-select-content" sideOffset={6}>
              {#each BROADCAST_TARGET_OPTIONS as opt}
                <Select.Item value={opt.value} class="admin-select-item">
                  <span>{opt.label}</span>
                  <Check size={14} class="admin-select-item-check" />
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </Label.Root>
      <Label.Root class="admin-field-label">
        <span>{at("broadcast_label_text", {}, "Текст сообщения")}</span>
        <small>{at("broadcast_hint_text", {}, "Поддерживается HTML-разметка Telegram")}</small>
        <textarea class="admin-textarea" rows="6" value={broadcastText} on:input={(e) => broadcastStore.updateField({ broadcastText: e.target.value })}></textarea>
      </Label.Root>
      <div style="display:flex; gap:8px; align-items:center;">
        <button type="button" class="admin-btn admin-btn-primary" on:click={broadcastStore.runBroadcast} disabled={broadcastBusy || !broadcastText.trim()}>
          <Send size={14} /> {broadcastBusy ? at("btn_sending", {}, "Отправка...") : at("btn_queue", {}, "Поставить в очередь")}
        </button>
        {#if broadcastResult}
          <span class="admin-muted">{at("broadcast_stat_queued", {}, "В очереди")}: {broadcastResult.queued} · {at("broadcast_stat_failed", {}, "Неудач")}: {broadcastResult.failed}</span>
        {/if}
      </div>
    </div>
  </div>
</div>
