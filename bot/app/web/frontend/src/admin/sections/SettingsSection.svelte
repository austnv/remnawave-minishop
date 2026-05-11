<script>
  import { ChevronRight } from "lucide-svelte";
  import { Accordion } from "bits-ui";

  export let groupSectionFields = () => [];
  export let isOverridden = () => false;
  export let renderField = () => {};
  export let sectionTitle = (id) => id;
  export let settingsAllOpen = false;
  export let settingsDirty = {};
  export let settingsLoading = false;
  export let settingsOpenSections = [];
  export let settingsOpenSubsections = {};
  export let settingsSections = [];
  export let toggleAllSections = () => {};
</script>

{#if settingsLoading || !settingsSections.length}
  <div class="admin-empty">{settingsLoading ? "Загрузка…" : "Нет данных"}</div>
{:else}
  <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <p class="admin-muted" style="margin:0;">
      Изменения в админке имеют приоритет над <code>.env</code>. Кнопка «Восстановить» возвращает значение из переменных окружения.
    </p>
    <button type="button" class="admin-btn admin-btn-sm admin-btn-ghost" on:click={toggleAllSections}>
      {settingsAllOpen ? "Свернуть всё" : "Развернуть всё"}
    </button>
  </div>
  <Accordion.Root type="multiple" bind:value={settingsOpenSections} class="admin-accordion">
    {#each settingsSections as section}
      {@const dirtyInSection = section.fields.filter((f) => Boolean(settingsDirty[f.key])).length}
      {@const overriddenInSection = section.fields.filter((f) => isOverridden(f)).length}
      <Accordion.Item value={section.id} class="admin-accordion-item admin-card">
        <Accordion.Header class="admin-accordion-header">
          <Accordion.Trigger class="admin-accordion-trigger">
            <span class="admin-accordion-title">{sectionTitle(section.id)}</span>
            <span class="admin-accordion-meta">
              {section.fields.length} параметров{#if overriddenInSection} · {overriddenInSection} override{/if}{#if dirtyInSection} · {dirtyInSection} изм.{/if}
            </span>
            <ChevronRight size={16} class="admin-accordion-chev" />
          </Accordion.Trigger>
        </Accordion.Header>
        <Accordion.Content class="admin-accordion-content">
          {@const groups = groupSectionFields(section)}
          {@const rootGroup = groups.find((g) => !g.label)}
          {@const labelGroups = groups.filter((g) => g.label)}
          <div class="admin-settings-fields">
            {#if rootGroup}
              {#each rootGroup.fields as field}
                {@render renderField(field)}
              {/each}
            {/if}
            {#if labelGroups.length}
              <Accordion.Root
                type="multiple"
                value={settingsOpenSubsections[section.id] || []}
                onValueChange={(v) => (settingsOpenSubsections = { ...settingsOpenSubsections, [section.id]: v })}
                class="admin-subsection-accordion"
              >
                {#each labelGroups as group}
                  {@const subDirty = group.fields.filter((f) => Boolean(settingsDirty[f.key])).length}
                  {@const subOverridden = group.fields.filter((f) => isOverridden(f)).length}
                  <Accordion.Item value={group.id} class="admin-settings-subsection">
                    <Accordion.Header class="admin-accordion-header">
                      <Accordion.Trigger class="admin-settings-subsection-trigger">
                        <strong>{group.label}</strong>
                        <span class="admin-settings-subsection-meta">
                          {group.fields.length} полей{#if subOverridden} · {subOverridden} override{/if}{#if subDirty} · {subDirty} изм.{/if}
                        </span>
                        <ChevronRight size={14} class="admin-accordion-chev" />
                      </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="admin-accordion-content">
                      <div class="admin-settings-subsection-body">
                        {#each group.fields as field}
                          {@render renderField(field)}
                        {/each}
                      </div>
                    </Accordion.Content>
                  </Accordion.Item>
                {/each}
              </Accordion.Root>
            {/if}
          </div>
        </Accordion.Content>
      </Accordion.Item>
    {/each}
  </Accordion.Root>
{/if}
