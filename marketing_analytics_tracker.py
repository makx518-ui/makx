"""
📊 Marketing Analytics Tracker - Аналитика и A/B тестирование

Возможности:
- Отслеживание метрик (views, likes, shares, comments, clicks)
- A/B тестирование контента
- ROI калькулятор
- Conversion tracking
- Best time to post анализ
- Audience insights
- Competitor analysis
"""

import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Типы метрик"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"


@dataclass
class Metric:
    """Метрика"""
    campaign_id: str
    platform: str
    metric_type: MetricType
    value: float
    timestamp: datetime


@dataclass
class ABTestResult:
    """Результат A/B теста"""
    variant_a_performance: float
    variant_b_performance: float
    winner: str  # "A" или "B"
    confidence: float
    sample_size_a: int
    sample_size_b: int


class MarketingAnalyticsTracker:
    """
    Трекер маркетинговой аналитики

    Собирает, анализирует и визуализирует маркетинговые метрики
    """

    def __init__(self, db_path: str = "marketing_automation.db"):
        self.db_path = db_path
        logger.info("📊 Analytics Tracker инициализирован")

    def track_metric(
        self,
        campaign_id: str,
        platform: str,
        metric_type: MetricType,
        value: float
    ):
        """Записать метрику"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO analytics (campaign_id, platform, metric_type, metric_value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, platform, metric_type.value, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        logger.info(f"📊 Метрика записана: {metric_type.value}={value} для {campaign_id}")

    def get_campaign_metrics(
        self,
        campaign_id: str,
        since: Optional[datetime] = None
    ) -> Dict[str, Dict[MetricType, List[float]]]:
        """Получить метрики кампании"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT platform, metric_type, metric_value, timestamp
            FROM analytics
            WHERE campaign_id = ?
        """
        params = [campaign_id]

        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())

        cursor.execute(query, params)

        metrics = {}
        for row in cursor.fetchall():
            platform, metric_type, value, timestamp = row

            if platform not in metrics:
                metrics[platform] = {}

            metric_enum = MetricType(metric_type)
            if metric_enum not in metrics[platform]:
                metrics[platform][metric_enum] = []

            metrics[platform][metric_enum].append(value)

        conn.close()

        return metrics

    def calculate_roi(
        self,
        campaign_id: str,
        budget: float
    ) -> Dict[str, float]:
        """
        Рассчитать ROI кампании

        ROI = (Revenue - Cost) / Cost * 100%
        """
        metrics = self.get_campaign_metrics(campaign_id)

        total_revenue = 0.0
        total_conversions = 0

        for platform_metrics in metrics.values():
            if MetricType.REVENUE in platform_metrics:
                total_revenue = sum(platform_metrics[MetricType.REVENUE])

            if MetricType.CONVERSIONS in platform_metrics:
                total_conversions = sum(platform_metrics[MetricType.CONVERSIONS])

        roi = ((total_revenue - budget) / budget * 100) if budget > 0 else 0.0

        return {
            "roi_percent": roi,
            "revenue": total_revenue,
            "cost": budget,
            "profit": total_revenue - budget,
            "conversions": total_conversions,
            "cost_per_conversion": budget / total_conversions if total_conversions > 0 else 0
        }

    def run_ab_test(
        self,
        variant_a_metrics: List[float],
        variant_b_metrics: List[float]
    ) -> ABTestResult:
        """
        Провести A/B тест

        Args:
            variant_a_metrics: Метрики варианта A
            variant_b_metrics: Метрики варианта B

        Returns:
            Результат теста
        """
        if not variant_a_metrics or not variant_b_metrics:
            raise ValueError("Both variants must have metrics")

        avg_a = statistics.mean(variant_a_metrics)
        avg_b = statistics.mean(variant_b_metrics)

        # Определить победителя
        winner = "A" if avg_a > avg_b else "B"

        # Упрощённый расчёт уверенности (в реальности - t-test)
        improvement = abs(avg_a - avg_b) / max(avg_a, avg_b) * 100
        confidence = min(improvement * 10, 99.9)  # Простая эвристика

        return ABTestResult(
            variant_a_performance=avg_a,
            variant_b_performance=avg_b,
            winner=winner,
            confidence=confidence,
            sample_size_a=len(variant_a_metrics),
            sample_size_b=len(variant_b_metrics)
        )

    def find_best_posting_time(
        self,
        campaign_id: str,
        platform: str
    ) -> Dict[int, float]:
        """
        Найти лучшее время для постинга

        Returns:
            Словарь {час: средняя_эффективность}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Получить все метрики с временем
        cursor.execute("""
            SELECT metric_type, metric_value, timestamp
            FROM analytics
            WHERE campaign_id = ? AND platform = ?
        """, (campaign_id, platform))

        hour_metrics = {}  # {час: [метрики]}

        for row in cursor.fetchall():
            metric_type, value, timestamp_str = row

            # Важные метрики для определения эффективности
            if metric_type in [MetricType.LIKES.value, MetricType.SHARES.value, MetricType.COMMENTS.value]:
                timestamp = datetime.fromisoformat(timestamp_str)
                hour = timestamp.hour

                if hour not in hour_metrics:
                    hour_metrics[hour] = []

                hour_metrics[hour].append(value)

        conn.close()

        # Рассчитать среднее для каждого часа
        hour_averages = {
            hour: statistics.mean(values)
            for hour, values in hour_metrics.items()
        }

        return hour_averages

    def get_summary_report(self, campaign_id: str) -> Dict[str, Any]:
        """Получить сводный отчёт по кампании"""
        metrics = self.get_campaign_metrics(campaign_id)

        report = {
            "campaign_id": campaign_id,
            "platforms": {},
            "totals": {
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "clicks": 0,
                "conversions": 0
            }
        }

        for platform, platform_metrics in metrics.items():
            report["platforms"][platform] = {}

            for metric_type, values in platform_metrics.items():
                total = sum(values)
                average = statistics.mean(values) if values else 0

                report["platforms"][platform][metric_type.value] = {
                    "total": total,
                    "average": average,
                    "max": max(values) if values else 0,
                    "min": min(values) if values else 0
                }

                # Добавить к общим итогам
                if metric_type.value in report["totals"]:
                    report["totals"][metric_type.value] += total

        return report


# === ДЕМО ===
if __name__ == "__main__":
    print("📊 Демо: Marketing Analytics Tracker")
    print("=" * 80)

    tracker = MarketingAnalyticsTracker()

    # Имитация метрик
    campaign_id = "test_campaign_123"

    # Записать метрики
    print("\n📝 Запись метрик...")
    tracker.track_metric(campaign_id, "twitter", MetricType.VIEWS, 1500)
    tracker.track_metric(campaign_id, "twitter", MetricType.LIKES, 120)
    tracker.track_metric(campaign_id, "twitter", MetricType.SHARES, 45)

    tracker.track_metric(campaign_id, "facebook", MetricType.VIEWS, 2000)
    tracker.track_metric(campaign_id, "facebook", MetricType.LIKES, 180)

    tracker.track_metric(campaign_id, "twitter", MetricType.REVENUE, 500.0)
    tracker.track_metric(campaign_id, "twitter", MetricType.CONVERSIONS, 10)

    # Получить сводку
    print("\n📊 Сводный отчёт:")
    report = tracker.get_summary_report(campaign_id)
    import json
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Рассчитать ROI
    print("\n💰 ROI Анализ:")
    roi = tracker.calculate_roi(campaign_id, budget=200.0)
    print(json.dumps(roi, indent=2))

    # A/B тест
    print("\n🔬 A/B Тестирование:")
    variant_a = [100, 110, 105, 108, 112]  # Метрики варианта A
    variant_b = [95, 98, 100, 97, 99]      # Метрики варианта B

    ab_result = tracker.run_ab_test(variant_a, variant_b)
    print(f"  Победитель: Вариант {ab_result.winner}")
    print(f"  Производительность A: {ab_result.variant_a_performance:.2f}")
    print(f"  Производительность B: {ab_result.variant_b_performance:.2f}")
    print(f"  Уверенность: {ab_result.confidence:.1f}%")

    print("\n✅ Демо завершено!")
