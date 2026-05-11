<script>
  import { Check, ChevronDown, ChevronLeft, ChevronRight } from "lucide-svelte";
  import { Label, Select } from "bits-ui";
  import { getContext, onMount } from "svelte";

  export let at = (key) => key;
  export let fmtDateShort = (value) => value;
  export let optionLabel = () => "";
  export let panelStatusBadge = () => ({});
  export let resolvedAvatarUrl = () => "";
  export let userDisplayName = () => "";
  export let userInitials = () => "";
  export let userSecondaryName = () => "";

  const usersStore = getContext("usersStore");

  $: ({
    users,
    usersTotal,
    usersPage,
    usersQuery,
    usersFilter,
    usersPanelStatus,
    usersSort,
    usersLoading,
  } = $usersStore);

  const USERS_PAGE_SIZE = 25;
  $: usersHasMore = users.length === USERS_PAGE_SIZE;

  const USERS_FILTER_OPTIONS = [
    { value: "all", label: at("filter_all", {}, "Все") },
    { value: "active", label: at("filter_not_banned", {}, "Не забанены") },
    { value: "banned", label: at("filter_banned", {}, "Забанены") },
    { value: "tg_linked", label: at("filter_tg_linked", {}, "С Telegram") },
    { value: "no_tg", label: at("filter_no_tg", {}, "Без Telegram") },
    { value: "email_linked", label: at("filter_email_linked", {}, "С email") },
    { value: "no_email", label: at("filter_no_email", {}, "Без email") },
    { value: "panel_linked", label: at("filter_panel_linked", {}, "С панелью") },
  ];

  const USERS_SORT_OPTIONS = [
    { value: "registered_desc", label: at("sort_registered_desc", {}, "Сначала новые") },
    { value: "registered_asc", label: at("sort_registered_asc", {}, "Сначала старые") },
    { value: "name_asc", label: at("sort_name_asc", {}, "Имя ↑") },
    { value: "name_desc", label: at("sort_name_desc", {}, "Имя ↓") },
    { value: "id_asc", label: at("sort_id_asc", {}, "ID ↑") },
    { value: "id_desc", label: at("sort_id_desc", {}, "ID ↓") },
  ];

  const USERS_PANEL_STATUS_OPTIONS = [
    { value: "all", label: at("panel_status_all", {}, "Все статусы") },
    { value: "active", label: at("status_active", {}, "active") },
    { value: "expired", label: at("status_expired", {}, "expired") },
    { value: "limited", label: at("status_limited", {}, "limited") },
  ];

  onMount(() => {
    usersStore.loadUsers();
  });
</script>

<div class="admin-toolbar admin-toolbar-users">
  <div class="admin-toolbar-search">
    <input
      type="search"
      class="input"
      placeholder={at("users_search_placeholder", {}, "ID, @username или email")}
      value={usersQuery}
      on:input={(e) => usersStore.updateState({ usersQuery: e.target.value })}
      on:keydown={(e) => e.key === "Enter" && (usersStore.updateState({ usersPage: 0 }), usersStore.loadUsers())}
    />
    <button type="button" class="admin-btn admin-btn-primary" on:click={() => { usersStore.updateState({ usersPage: 0 }); usersStore.loadUsers(); }}>{at("find", {}, "Найти")}</button>
  </div>

  <div class="admin-toolbar-controls">
    <Label.Root class="admin-toolbar-field">
      <span class="admin-toolbar-field-label">{at("filter", {}, "Фильтр")}</span>
      <Select.Root
        type="single"
        value={usersFilter}
        onValueChange={(value) => { usersStore.updateState({ usersFilter: value, usersPage: 0 }); usersStore.loadUsers(); }}
      >
        <Select.Trigger class="admin-select-trigger admin-toolbar-select" aria-label={at("filter", {}, "Фильтр")}>
          <span>{optionLabel(USERS_FILTER_OPTIONS, usersFilter)}</span>
          <ChevronDown size={14} class="admin-select-icon" />
        </Select.Trigger>
        <Select.Portal>
          <Select.Content class="admin-select-content" sideOffset={6}>
            {#each USERS_FILTER_OPTIONS as opt}
              <Select.Item value={opt.value} class="admin-select-item">
                <span>{opt.label}</span>
                <Check size={14} class="admin-select-item-check" />
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </Label.Root>

    <Label.Root class="admin-toolbar-field">
      <span class="admin-toolbar-field-label">{at("panel_status", {}, "Статус панели")}</span>
      <Select.Root
        type="single"
        value={usersPanelStatus}
        onValueChange={(value) => { usersStore.updateState({ usersPanelStatus: value, usersPage: 0 }); usersStore.loadUsers(); }}
      >
        <Select.Trigger class="admin-select-trigger admin-toolbar-select" aria-label={at("panel_status", {}, "Статус панели")}>
          <span>{optionLabel(USERS_PANEL_STATUS_OPTIONS, usersPanelStatus)}</span>
          <ChevronDown size={14} class="admin-select-icon" />
        </Select.Trigger>
        <Select.Portal>
          <Select.Content class="admin-select-content" sideOffset={6}>
            {#each USERS_PANEL_STATUS_OPTIONS as opt}
              <Select.Item value={opt.value} class="admin-select-item">
                <span>{opt.label}</span>
                <Check size={14} class="admin-select-item-check" />
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </Label.Root>

    <Label.Root class="admin-toolbar-field">
      <span class="admin-toolbar-field-label">{at("sort", {}, "Сортировка")}</span>
      <Select.Root
        type="single"
        value={usersSort}
        onValueChange={(value) => { usersStore.updateState({ usersSort: value, usersPage: 0 }); usersStore.loadUsers(); }}
      >
        <Select.Trigger class="admin-select-trigger admin-toolbar-select" aria-label={at("sort", {}, "Сортировка")}>
          <span>{optionLabel(USERS_SORT_OPTIONS, usersSort)}</span>
          <ChevronDown size={14} class="admin-select-icon" />
        </Select.Trigger>
        <Select.Portal>
          <Select.Content class="admin-select-content" sideOffset={6}>
            {#each USERS_SORT_OPTIONS as opt}
              <Select.Item value={opt.value} class="admin-select-item">
                <span>{opt.label}</span>
                <Check size={14} class="admin-select-item-check" />
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </Label.Root>

    <div class="admin-toolbar-summary">
      <span class="admin-toolbar-field-label">{at("total", {}, "Всего")}</span>
      <strong>{usersTotal}</strong>
    </div>
  </div>
</div>

<div class="admin-table-wrap">
  {#if usersLoading}
    <ul class="admin-user-list admin-user-list-skeleton" aria-hidden="true">
      {#each Array(USERS_PAGE_SIZE) as _, i (i)}
        <li>
          <div class="admin-user-row admin-user-row-skeleton">
            <span class="admin-skeleton admin-skeleton-avatar"></span>
            <span class="admin-user-main">
              <span class="admin-skeleton admin-skeleton-line admin-skeleton-line-strong"></span>
              <span class="admin-skeleton admin-skeleton-line admin-skeleton-line-soft"></span>
            </span>
            <span class="admin-user-side">
              <span class="admin-skeleton admin-skeleton-badge"></span>
              <span class="admin-skeleton admin-skeleton-line admin-skeleton-line-tiny"></span>
            </span>
          </div>
        </li>
      {/each}
    </ul>
  {:else if !users.length}
    <div class="admin-card-body"><span class="admin-muted">{at("users_empty", {}, "Никого не найдено")}</span></div>
  {:else}
    <ul class="admin-user-list">
      {#each users as user}
        {@const avatar = resolvedAvatarUrl(user)}
        {@const badge = panelStatusBadge(user)}
        <li>
          <button type="button" class="admin-user-row" on:click={() => usersStore.openUser(user)}>
            <span class="admin-avatar admin-avatar-sm">
              {#if avatar}
                <img src={avatar} alt="" loading="lazy" referrerpolicy="no-referrer" />
              {:else}
                <span>{userInitials(user)}</span>
              {/if}
            </span>
            <span class="admin-user-main">
              <strong>{userDisplayName(user)}</strong>
              <small>{userSecondaryName(user)}</small>
            </span>
            <span class="admin-user-side">
              <span class="admin-badge admin-badge-{badge.variant}">{badge.label}</span>
              <span class="admin-user-tertiary">{fmtDateShort(user.registration_date)}</span>
            </span>
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<div class="admin-pagination">
  <span class="admin-pagination-meta">{at("page", {}, "Страница")} {usersPage + 1}</span>
  <div class="admin-pagination-buttons">
    <button type="button" class="admin-btn admin-btn-sm" disabled={usersPage === 0} on:click={() => { usersStore.updateState({ usersPage: Math.max(0, usersPage - 1) }); usersStore.loadUsers(); }}>
      <ChevronLeft size={14} /> {at("back", {}, "Назад")}
    </button>
    <button type="button" class="admin-btn admin-btn-sm" disabled={!usersHasMore} on:click={() => { usersStore.updateState({ usersPage: usersPage + 1 }); usersStore.loadUsers(); }}>
      {at("next", {}, "Далее")} <ChevronRight size={14} />
    </button>
  </div>
</div>
