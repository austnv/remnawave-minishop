import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from bot.utils.date_utils import month_start
from config.settings import Settings
from db.dal import subscription_dal
from db.models import Base, Subscription
from .migrator import run_database_migrations

async_engine = None


def init_db_connection(settings: Settings) -> sessionmaker:
    global async_engine

    if async_engine is None:
        logging.info(
            f"Attempting to create SQLAlchemy engine with URL: {settings.DATABASE_URL}"
        )
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
        )

    local_async_session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    logging.info(
        f"SQLAlchemy Async Engine and SessionFactory configured for PostgreSQL."
    )
    return local_async_session_factory


async def get_async_session(session_factory: sessionmaker) -> AsyncSession:

    if session_factory is None:
        raise RuntimeError(
            "AsyncSessionFactory is not provided or initialized.")

    async_session = session_factory()
    try:
        yield async_session
    finally:
        await async_session.close()


async def init_db(settings: Settings, session_factory: sessionmaker):

    global async_engine
    if async_engine is None:

        logging.warning(
            "init_db: async_engine was None, re-initializing via init_db_connection."
        )

        raise RuntimeError(
            "async_engine is not initialized. Call init_db_connection and get session_factory first."
        )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(run_database_migrations)
    logging.info(
        "PostgreSQL database initialized/checked successfully using SQLAlchemy."
    )

    async with session_factory() as session:
        from .dal.panel_sync_dal import get_panel_sync_status, update_panel_sync_status
        from sqlalchemy import text
        try:
            current_status = await get_panel_sync_status(session)
            if current_status is None:
                logging.info("Initializing panel_sync_status record.")
                await update_panel_sync_status(session,
                                               status="never_run",
                                               details="System initialized",
                                               users_processed=0,
                                               subs_synced=0)
                await session.commit()
        except Exception as e_sync_init:
            await session.rollback()
            logging.error(
                f"Failed to initialize PanelSyncStatus: {e_sync_init}",
                exc_info=True)

        if settings.tariffs_config:
            try:
                default_tariff = settings.tariffs_config.default
                default_price = default_tariff.period_price(1, "rub") or default_tariff.min_period_price_rub()
                await session.execute(
                    text(
                        """
                        UPDATE subscriptions AS s
                        SET
                            tariff_key = COALESCE(s.tariff_key, :tariff_key),
                            tier_baseline_bytes = COALESCE(s.tier_baseline_bytes, s.traffic_limit_bytes, :baseline),
                            topup_balance_bytes = COALESCE(s.topup_balance_bytes, 0),
                            period_start_at = COALESCE(
                                s.period_start_at,
                                (
                                    SELECT p.created_at
                                    FROM payments p
                                    WHERE p.user_id = s.user_id
                                      AND p.status = 'succeeded'
                                    ORDER BY p.created_at DESC
                                    LIMIT 1
                                ),
                                s.start_date,
                                NOW()
                            ),
                            effective_monthly_price_rub = COALESCE(
                                s.effective_monthly_price_rub,
                                (
                                    SELECT p.amount / GREATEST(COALESCE(p.subscription_duration_months, 1), 1)
                                    FROM payments p
                                    WHERE p.user_id = s.user_id
                                      AND p.status = 'succeeded'
                                      AND COALESCE(p.subscription_duration_months, 0) > 0
                                    ORDER BY p.created_at DESC
                                    LIMIT 1
                                ),
                                :default_price
                            )
                        WHERE s.is_active = TRUE
                          AND s.tariff_key IS NULL
                        """
                    ),
                    {
                        "tariff_key": default_tariff.key,
                        "baseline": default_tariff.monthly_bytes,
                        "default_price": default_price,
                    },
                )
                month_anchor = month_start()
                active_subs = await session.execute(
                    select(Subscription).where(Subscription.is_active == True)
                )
                for sub in active_subs.scalars().all():
                    tariff_key = sub.tariff_key or default_tariff.key
                    try:
                        tariff = settings.tariffs_config.require(tariff_key)
                    except Exception:
                        continue

                    update_data = {
                        "tariff_key": tariff.key,
                        "topup_balance_bytes": int(sub.topup_balance_bytes or 0),
                    }
                    if tariff.billing_model == "period":
                        baseline_source = (
                            sub.tier_baseline_bytes
                            if sub.tier_baseline_bytes is not None
                            else (sub.traffic_limit_bytes if sub.traffic_limit_bytes is not None else tariff.monthly_bytes)
                        )
                        baseline = int(baseline_source or 0)
                        update_data.update(
                            {
                                "tier_baseline_bytes": baseline,
                                "traffic_limit_bytes": baseline + int(sub.topup_balance_bytes or 0),
                                "period_start_at": month_anchor,
                                "effective_monthly_price_rub": (
                                    sub.effective_monthly_price_rub
                                    if sub.effective_monthly_price_rub is not None
                                    else default_price
                                ),
                            }
                        )
                    else:
                        update_data.update(
                            {
                                "tier_baseline_bytes": 0,
                                "period_start_at": None,
                                "effective_monthly_price_rub": None,
                            }
                        )
                    await subscription_dal.update_subscription(session, sub.subscription_id, update_data)
                await session.commit()
            except Exception:
                await session.rollback()
                logging.exception("Failed to backfill existing subscriptions for tariffs config.")
