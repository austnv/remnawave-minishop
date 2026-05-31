import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const localePathCandidates = [
  resolve(process.cwd(), "..", "locales", "ru.json"),
  resolve(process.cwd(), "locales", "ru.json"),
];
const localePath =
  localePathCandidates.find((candidate) => existsSync(candidate)) ||
  localePathCandidates[0];
const messages = JSON.parse(readFileSync(localePath, "utf8"));

const sample = {
  amount: "390 RUB",
  brand: "remnawave-minishop",
  code: "483921",
  dashboardUrl: "https://mini.example.com/app",
  endDate: "21.06.2026, 18:00",
  magicUrl: "https://mini.example.com/app/auth/magic/preview",
  minutes: 10,
  premiumTraffic: "25",
  regularTraffic: "100",
  ticketUrl: "https://mini.example.com/app/support/42",
};

const interpolate = (template, values = {}) =>
  String(template || "").replace(/\{([a-zA-Z0-9_]+)\}/g, (match, name) =>
    Object.prototype.hasOwnProperty.call(values, name) ? values[name] : match,
  );

const t = (key, values = {}) => interpolate(messages[key] || key, values);

const escapeHtml = (value) =>
  String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const textWithBreaks = (value) => escapeHtml(value).replace(/\n/g, "<br>");

const stripTags = (value) =>
  String(value || "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]*>/g, "");

const renderRows = (rows = []) => {
  if (!rows.length) return "";
  return `<table class="mail-card__rows" role="presentation" cellpadding="0" cellspacing="0">
    ${rows
      .map(
        ([label, value]) => `<tr>
          <td>${escapeHtml(label)}</td>
          <td>${escapeHtml(value)}</td>
        </tr>`,
      )
      .join("")}
  </table>`;
};

const renderEmailHtml = ({
  subject,
  heading = subject,
  intro,
  rows,
  code,
  message,
  note,
  ctaLabel,
  ctaUrl,
}) => `<div class="mail-card">
  <div class="mail-card__brand">${escapeHtml(sample.brand)}</div>
  <div class="mail-card__panel">
    <p class="mail-card__subject">${escapeHtml(subject)}</p>
    <h2>${escapeHtml(heading)}</h2>
    ${intro ? `<p class="mail-card__intro">${textWithBreaks(intro)}</p>` : ""}
    ${
      code
        ? `<div class="mail-card__code" aria-label="Email code">${escapeHtml(code)}</div>`
        : ""
    }
    ${renderRows(rows)}
    ${
      message
        ? `<div class="mail-card__message">${textWithBreaks(message)}</div>`
        : ""
    }
    ${
      ctaLabel
        ? `<a class="mail-card__cta" href="${escapeHtml(ctaUrl || sample.dashboardUrl)}">${escapeHtml(
            ctaLabel,
          )}</a>`
        : ""
    }
    ${note ? `<p class="mail-card__note">${textWithBreaks(note)}</p>` : ""}
  </div>
  <p class="mail-card__footer">${escapeHtml(t("email_footer_auto", { brand: sample.brand }))}</p>
</div>`;

const preview = (item) => ({
  ...item,
  html: renderEmailHtml(item),
});

const paymentRows = (periodLabel, periodValue, provider = "YooKassa") => [
  [periodLabel, periodValue],
  [t("email_payment_success_row_amount"), sample.amount],
  [t("email_payment_success_row_end_date"), sample.endDate],
  [t("email_payment_success_row_method"), provider],
];

const paymentPreview = ({
  id,
  title,
  introKey,
  periodLabel,
  periodValue,
  textKey,
  values = {},
}) =>
  preview({
    id,
    category: "Платежи",
    title,
    subject: t("email_payment_success_subject"),
    heading: t("email_payment_success_heading"),
    intro: t(introKey, values),
    rows: paymentRows(periodLabel, periodValue),
    message: t(textKey, {
      amount: sample.amount,
      end_date: sample.endDate,
      ...values,
    }),
    note: t("email_payment_success_footer_note"),
    ctaLabel: t("email_payment_success_cta"),
  });

const notificationPreview = ({
  id,
  title,
  subjectKey,
  message,
  ctaKey = "email_user_notification_cta",
}) =>
  preview({
    id,
    category: "Уведомления",
    title,
    subject: t(subjectKey),
    heading: t(subjectKey),
    intro: t("email_user_notification_intro"),
    message,
    ctaLabel: t(ctaKey),
  });

const expiringPreview = ({ id, title, suffix, days }) =>
  preview({
    id,
    category: "Подписка",
    title,
    subject: t(`email_subscription_expiring_subject_${suffix}`, { days }),
    heading: t(`email_subscription_expiring_heading_${suffix}`, { days }),
    intro: t(`email_subscription_expiring_intro_${suffix}`, { days }),
    rows: [
      [t("email_subscription_expiring_row_days_left"), String(days)],
      [t("email_subscription_expiring_row_end_date"), sample.endDate],
    ],
    message: t("email_subscription_expiring_text", {
      heading: t(`email_subscription_expiring_heading_${suffix}`, { days }),
      end_date: sample.endDate,
    }),
    note: t("email_subscription_expiring_note"),
    ctaLabel: t("email_subscription_expiring_cta"),
  });

const lifecycleSubject = (key, values = {}) => t(key, values);

const lifecyclePreview = ({
  id,
  title,
  subject,
  introKey = "email_subscription_lifecycle_intro_direct",
  message,
}) =>
  preview({
    id,
    category: "Подписка",
    title,
    subject,
    heading: subject,
    intro: t(introKey),
    rows: [[t("email_subscription_lifecycle_row_end_date"), sample.endDate]],
    message,
    ctaLabel: t("email_subscription_lifecycle_cta"),
  });

const supportRows = (includeUser = false) => [
  [t("email_support_row_ticket"), "#42"],
  ...(includeUser ? [[t("email_support_row_user"), "alex@example.com"]] : []),
  [t("email_support_row_subject"), "Не работает подключение"],
  [t("email_support_row_tariff"), "Premium"],
  [t("email_support_row_remaining"), "3 д. 4 ч."],
];

export const emailPreviews = [
  preview({
    id: "login-code",
    category: "Доступ",
    title: "Код для входа",
    subject: t("email_login_code_subject", { code: sample.code }),
    heading: t("email_login_code_heading"),
    intro: t("email_login_code_intro"),
    code: sample.code,
    message: [
      stripTags(t("email_login_code_expiry_html", { minutes: sample.minutes })),
      t("email_login_code_security"),
      t("email_login_code_text_magic", { url: sample.magicUrl }),
    ].join("\n\n"),
    ctaLabel: t("email_login_code_magic_cta"),
    ctaUrl: sample.magicUrl,
  }),
  preview({
    id: "set-password-code",
    category: "Доступ",
    title: "Код для создания пароля",
    subject: t("email_set_password_code_subject", { code: sample.code }),
    heading: t("email_set_password_code_heading"),
    intro: t("email_set_password_code_intro"),
    code: sample.code,
    message: [
      stripTags(t("email_set_password_code_expiry_html", { minutes: sample.minutes })),
      t("email_set_password_code_security"),
    ].join("\n\n"),
  }),
  preview({
    id: "account-merged",
    category: "Аккаунт",
    title: "Аккаунты объединены",
    subject: t("email_account_merged_subject"),
    heading: t("email_account_merged_heading"),
    intro: t("email_account_merged_intro"),
    rows: [
      [t("email_account_merged_row_kept"), "#100200300"],
      [t("email_account_merged_row_removed"), "#-42"],
      [t("email_account_merged_row_end_date"), sample.endDate],
    ],
    message: t("email_account_merged_text", {
      primary: "#100200300",
      removed: "#-42",
      end_date: sample.endDate,
    }),
    note: t("email_account_merged_note"),
  }),
  paymentPreview({
    id: "payment-subscription",
    title: "Оплата подписки",
    introKey: "email_payment_success_intro_subscription",
    periodLabel: t("email_payment_success_row_period"),
    periodValue: t("email_payment_success_period_value", { months: 1 }),
    textKey: "email_payment_success_text_subscription",
    values: { months: 1 },
  }),
  paymentPreview({
    id: "payment-traffic",
    title: "Покупка трафика",
    introKey: "email_payment_success_intro_traffic",
    periodLabel: t("email_payment_success_row_traffic"),
    periodValue: t("email_payment_success_traffic_value", {
      traffic_gb: sample.regularTraffic,
    }),
    textKey: "email_payment_success_text_traffic",
    values: { traffic_gb: sample.regularTraffic },
  }),
  paymentPreview({
    id: "payment-premium-traffic",
    title: "Покупка premium-трафика",
    introKey: "email_payment_success_intro_premium_topup",
    periodLabel: t("email_payment_success_row_traffic"),
    periodValue: t("email_payment_success_traffic_value", {
      traffic_gb: sample.premiumTraffic,
    }),
    textKey: "email_payment_success_text_traffic",
    values: { traffic_gb: sample.premiumTraffic },
  }),
  paymentPreview({
    id: "payment-hwid",
    title: "Покупка HWID-устройств",
    introKey: "email_payment_success_intro_hwid",
    periodLabel: t("email_payment_success_row_hwid"),
    periodValue: t("email_payment_success_hwid_value", { count: 2 }),
    textKey: "email_payment_success_text_hwid",
    values: { count: 2 },
  }),
  paymentPreview({
    id: "payment-tariff-upgrade",
    title: "Платное повышение тарифа",
    introKey: "email_payment_success_intro_tariff_upgrade",
    periodLabel: t("email_payment_success_row_operation"),
    periodValue: t("email_payment_success_tariff_upgrade_value"),
    textKey: "email_payment_success_text_tariff_upgrade",
  }),
  notificationPreview({
    id: "payment-failed",
    title: "Неуспешная оплата",
    subjectKey: "email_payment_failed_subject",
    message: "Платёж не был завершён. Можно попробовать ещё раз из личного кабинета.",
  }),
  notificationPreview({
    id: "payment-method-bound",
    title: "Способ оплаты привязан",
    subjectKey: "email_payment_method_bound_subject",
    message: "Автопродление подключено, следующий платёж пройдёт автоматически.",
  }),
  notificationPreview({
    id: "referral-bonus",
    title: "Реферальный бонус",
    subjectKey: "email_referral_bonus_subject",
    message: "Друг активировал подписку, и бонусные дни уже добавлены к вашему аккаунту.",
  }),
  notificationPreview({
    id: "trial-traffic-depleted",
    title: "Трафик пробного периода закончился",
    subjectKey: "email_trial_traffic_depleted_subject",
    message: "Пробный трафик израсходован. Оформите подписку, чтобы продолжить пользоваться сервисом.",
  }),
  notificationPreview({
    id: "regular-traffic-almost",
    title: "Обычный трафик почти закончился",
    subjectKey: "email_traffic_warning_regular_almost_subject",
    ctaKey: "email_traffic_warning_regular_cta",
    message: "Использовано больше 85% трафика тарифа. Можно докупить пакет заранее.",
  }),
  notificationPreview({
    id: "regular-traffic-depleted",
    title: "Обычный трафик закончился",
    subjectKey: "email_traffic_warning_regular_depleted_subject",
    ctaKey: "email_traffic_warning_regular_cta",
    message: "Трафик тарифа израсходован. Докупите пакет, чтобы восстановить доступ.",
  }),
  notificationPreview({
    id: "premium-traffic-almost",
    title: "Premium-трафик почти закончился",
    subjectKey: "email_traffic_warning_premium_almost_subject",
    ctaKey: "email_traffic_warning_premium_cta",
    message: "Premium-трафика осталось мало. Можно докупить пакет до полного расхода.",
  }),
  notificationPreview({
    id: "premium-traffic-depleted",
    title: "Premium-трафик закончился",
    subjectKey: "email_traffic_warning_premium_depleted_subject",
    ctaKey: "email_traffic_warning_premium_cta",
    message: "Premium-трафик израсходован. Докупите пакет, чтобы продолжить использовать premium-маршруты.",
  }),
  expiringPreview({
    id: "subscription-expiring-today",
    title: "Подписка заканчивается сегодня",
    suffix: "today",
    days: 0,
  }),
  expiringPreview({
    id: "subscription-expiring-tomorrow",
    title: "Подписка заканчивается завтра",
    suffix: "tomorrow",
    days: 1,
  }),
  expiringPreview({
    id: "subscription-expiring-days",
    title: "Подписка скоро закончится",
    suffix: "days",
    days: 3,
  }),
  lifecyclePreview({
    id: "lifecycle-before-days",
    title: "Lifecycle: осталось несколько дней",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_before_days", {
      days: 3,
    }),
    message: "Подписка скоро закончится. Продлите её заранее, чтобы доступ не прерывался.",
  }),
  lifecyclePreview({
    id: "lifecycle-before-hours",
    title: "Lifecycle: осталось несколько часов",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_before_hours", {
      hours: 6,
    }),
    message: "До окончания подписки осталось несколько часов.",
  }),
  lifecyclePreview({
    id: "lifecycle-expired",
    title: "Lifecycle: подписка закончилась",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_expired"),
    message: "Подписка закончилась. Продлите доступ в личном кабинете.",
  }),
  lifecyclePreview({
    id: "lifecycle-expired-after",
    title: "Lifecycle: подписка закончилась вчера",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_expired_after"),
    message: "Вчера подписка была отключена. Вы можете восстановить доступ продлением.",
  }),
  lifecyclePreview({
    id: "lifecycle-autorenew",
    title: "Lifecycle: автопродление завтра",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_autorenew"),
    message: "Завтра будет выполнено автопродление подписки.",
  }),
  lifecyclePreview({
    id: "lifecycle-mirrored",
    title: "Lifecycle: копия Telegram-уведомления",
    subject: lifecycleSubject("email_subscription_lifecycle_subject_before_days", {
      days: 2,
    }),
    introKey: "email_subscription_lifecycle_intro_mirrored",
    message: "Это письмо дублирует важное уведомление, отправленное в Telegram.",
  }),
  preview({
    id: "support-new-ticket-admin",
    category: "Поддержка",
    title: "Новый тикет для администратора",
    subject: t("email_support_new_ticket_admin_subject", { ticket_id: 42 }),
    heading: t("email_support_new_ticket_admin_heading", { ticket_id: 42 }),
    intro: t("email_support_new_ticket_admin_intro"),
    rows: supportRows(true),
    message: "Пользователь не может подключиться после продления.",
    ctaLabel: t("email_support_cta_open_ticket"),
    ctaUrl: "https://mini.example.com/app/admin/support/42",
  }),
  preview({
    id: "support-user-reply-admin",
    category: "Поддержка",
    title: "Ответ пользователя для администратора",
    subject: t("email_support_user_reply_admin_subject", { ticket_id: 42 }),
    heading: t("email_support_user_reply_admin_heading", { ticket_id: 42 }),
    intro: t("email_support_user_reply_admin_intro"),
    rows: supportRows(true),
    message: "Проблема повторилась на телефоне и ноутбуке.",
    ctaLabel: t("email_support_cta_open_ticket"),
    ctaUrl: "https://mini.example.com/app/admin/support/42",
  }),
  preview({
    id: "support-admin-reply-user",
    category: "Поддержка",
    title: "Ответ поддержки пользователю",
    subject: t("email_support_admin_reply_user_subject", { ticket_id: 42 }),
    heading: t("email_support_admin_reply_user_heading", { ticket_id: 42 }),
    intro: t("email_support_admin_reply_user_intro"),
    rows: supportRows(false),
    message: "Мы обновили конфигурацию. Попробуйте подключиться ещё раз.",
    ctaLabel: t("email_support_cta_open_mini_app"),
    ctaUrl: sample.ticketUrl,
  }),
  preview({
    id: "support-ticket-closed-user",
    category: "Поддержка",
    title: "Тикет закрыт",
    subject: t("email_support_ticket_closed_user_subject", { ticket_id: 42 }),
    heading: t("email_support_ticket_closed_user_heading", { ticket_id: 42 }),
    intro: t("email_support_ticket_closed_user_intro"),
    rows: supportRows(false),
    message: t("email_support_ticket_closed_user_body"),
    ctaLabel: t("email_support_cta_open_mini_app"),
    ctaUrl: sample.ticketUrl,
  }),
];
