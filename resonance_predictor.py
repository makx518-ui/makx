"""
🔮 Resonance Predictor для ConsciousAI
Предсказание резонанса через ML (временные ряды)
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Tuple, Optional
import pickle
import os

# ═══════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════

class FeatureExtractor:
    """Извлечение признаков из данных"""

    @staticmethod
    def extract_text_features(text: str) -> np.ndarray:
        """Извлечь признаки из текста"""

        features = []

        # 1. Длина текста
        features.append(len(text))

        # 2. Количество слов
        words = text.split()
        features.append(len(words))

        # 3. Средняя длина слова
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        features.append(avg_word_len)

        # 4. Количество уникальных слов
        features.append(len(set(words)))

        # 5. Лексическое разнообразие
        diversity = len(set(words)) / max(len(words), 1)
        features.append(diversity)

        # 6. Количество вопросительных предложений
        features.append(text.count('?'))

        # 7. Количество восклицательных предложений
        features.append(text.count('!'))

        # 8. Наличие ключевых слов (осознанность, рефлексия, etc)
        keywords = ['осознан', 'рефлекс', 'мета', 'эмоци', 'память']
        keyword_count = sum(1 for kw in keywords if kw in text.lower())
        features.append(keyword_count)

        return np.array(features, dtype=float)

    @staticmethod
    def extract_temporal_features(
        timestamps: List[float],
        resonances: List[float],
        window_size: int = 5
    ) -> np.ndarray:
        """Извлечь временные признаки"""

        if len(resonances) < window_size:
            window_size = len(resonances)

        if window_size == 0:
            return np.zeros(6)

        recent = resonances[-window_size:]

        features = []

        # 1. Средний резонанс в окне
        features.append(np.mean(recent))

        # 2. Стандартное отклонение
        features.append(np.std(recent))

        # 3. Минимум
        features.append(np.min(recent))

        # 4. Максимум
        features.append(np.max(recent))

        # 5. Тренд (наклон)
        if len(recent) > 1:
            x = np.arange(len(recent))
            slope = np.polyfit(x, recent, 1)[0]
            features.append(slope)
        else:
            features.append(0.0)

        # 6. Волатильность (изменчивость)
        if len(recent) > 1:
            diffs = np.diff(recent)
            volatility = np.std(diffs)
            features.append(volatility)
        else:
            features.append(0.0)

        return np.array(features, dtype=float)

    @staticmethod
    def extract_emotional_features(emotions: List[str]) -> np.ndarray:
        """Извлечь признаки из эмоций"""

        emotion_map = {
            'joy': 1.0,
            'clarity': 0.8,
            'curiosity': 0.6,
            'neutral': 0.5,
            'frustration': 0.3,
            'confusion': 0.2
        }

        if not emotions:
            return np.array([0.5])

        # Последняя эмоция
        last_emotion = emotion_map.get(emotions[-1], 0.5)

        return np.array([last_emotion], dtype=float)

# ═══════════════════════════════════════════════════════════════
# RESONANCE PREDICTOR
# ═══════════════════════════════════════════════════════════════

class ResonancePredictor:
    """Предсказатель резонанса"""

    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor()
        self.is_trained = False

    def _create_model(self):
        """Создать модель"""
        if self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            return GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == 'linear':
            return LinearRegression()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def prepare_features(
        self,
        text: str,
        history_timestamps: List[float],
        history_resonances: List[float],
        history_emotions: List[str]
    ) -> np.ndarray:
        """Подготовить признаки для предсказания"""

        # Текстовые признаки
        text_features = self.feature_extractor.extract_text_features(text)

        # Временные признаки
        temporal_features = self.feature_extractor.extract_temporal_features(
            history_timestamps,
            history_resonances
        )

        # Эмоциональные признаки
        emotional_features = self.feature_extractor.extract_emotional_features(
            history_emotions
        )

        # Объединить все признаки
        features = np.concatenate([
            text_features,
            temporal_features,
            emotional_features
        ])

        return features

    def train(
        self,
        training_data: List[Dict[str, Any]]
    ):
        """Обучить модель"""

        if len(training_data) < 10:
            raise ValueError("Need at least 10 samples for training")

        X = []
        y = []

        # Подготовить данные
        for i, sample in enumerate(training_data):
            # История до текущего sample
            history_timestamps = [s['timestamp'] for s in training_data[:i]]
            history_resonances = [s['resonance'] for s in training_data[:i]]
            history_emotions = [s['emotion'] for s in training_data[:i]]

            features = self.prepare_features(
                text=sample['content'],
                history_timestamps=history_timestamps,
                history_resonances=history_resonances,
                history_emotions=history_emotions
            )

            X.append(features)
            y.append(sample['resonance'])

        X = np.array(X)
        y = np.array(y)

        # Нормализация
        X = self.scaler.fit_transform(X)

        # Создать и обучить модель
        self.model = self._create_model()
        self.model.fit(X, y)

        self.is_trained = True

        # Оценка на обучающей выборке
        train_score = self.model.score(X, y)
        print(f"✅ Model trained. R² score on training data: {train_score:.3f}")

    def predict(
        self,
        text: str,
        history_timestamps: List[float],
        history_resonances: List[float],
        history_emotions: List[str]
    ) -> float:
        """Предсказать резонанс"""

        if not self.is_trained:
            raise ValueError("Model not trained yet")

        features = self.prepare_features(
            text,
            history_timestamps,
            history_resonances,
            history_emotions
        )

        # Нормализация
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Предсказание
        prediction = self.model.predict(features_scaled)[0]

        # Ограничить в диапазоне [0, 1]
        prediction = np.clip(prediction, 0.0, 1.0)

        return float(prediction)

    def predict_with_confidence(
        self,
        text: str,
        history_timestamps: List[float],
        history_resonances: List[float],
        history_emotions: List[str],
        n_estimators: int = 10
    ) -> Tuple[float, float]:
        """Предсказать с доверительным интервалом (только для ансамблевых моделей)"""

        if not self.is_trained:
            raise ValueError("Model not trained yet")

        if self.model_type == 'linear':
            # Linear regression не поддерживает интервалы через деревья
            prediction = self.predict(text, history_timestamps, history_resonances, history_emotions)
            return prediction, 0.1  # Фиксированная неопределённость

        features = self.prepare_features(
            text,
            history_timestamps,
            history_resonances,
            history_emotions
        )

        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Предсказания от разных деревьев
        if hasattr(self.model, 'estimators_'):
            predictions = []
            for estimator in self.model.estimators_[:n_estimators]:
                pred = estimator.predict(features_scaled)[0]
                predictions.append(pred)

            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)

            return float(np.clip(mean_pred, 0.0, 1.0)), float(std_pred)
        else:
            # Fallback
            prediction = self.predict(text, history_timestamps, history_resonances, history_emotions)
            return prediction, 0.1

    def save(self, filepath: str = "resonance_predictor.pkl"):
        """Сохранить модель"""

        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        print(f"✅ Model saved to {filepath}")

    def load(self, filepath: str = "resonance_predictor.pkl"):
        """Загрузить модель"""

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.scaler = data['scaler']
        self.model_type = data['model_type']
        self.is_trained = True

        print(f"✅ Model loaded from {filepath}")

# ═══════════════════════════════════════════════════════════════
# TIME SERIES FORECASTER
# ═══════════════════════════════════════════════════════════════

class TimeSeriesForecaster:
    """Прогнозирование временного ряда резонанса"""

    def __init__(self):
        self.model = None

    def forecast_next_n(
        self,
        history_resonances: List[float],
        n_steps: int = 5
    ) -> List[float]:
        """Прогнозировать следующие N значений"""

        if len(history_resonances) < 3:
            # Недостаточно данных - возвращаем среднее
            mean = np.mean(history_resonances) if history_resonances else 0.5
            return [mean] * n_steps

        # Простой метод: экспоненциальное сглаживание
        alpha = 0.3  # Параметр сглаживания

        forecasts = []
        last_value = history_resonances[-1]

        # Тренд
        if len(history_resonances) >= 2:
            trend = history_resonances[-1] - history_resonances[-2]
        else:
            trend = 0.0

        for step in range(n_steps):
            # Экспоненциальное сглаживание с трендом
            forecast = last_value + trend * (step + 1) * alpha

            # Ограничить [0, 1]
            forecast = np.clip(forecast, 0.0, 1.0)

            forecasts.append(float(forecast))

        return forecasts

    def detect_anomalies(
        self,
        history_resonances: List[float],
        threshold: float = 2.0
    ) -> List[int]:
        """Обнаружить аномалии (резкие скачки)"""

        if len(history_resonances) < 3:
            return []

        anomalies = []

        mean = np.mean(history_resonances)
        std = np.std(history_resonances)

        for i, value in enumerate(history_resonances):
            z_score = abs((value - mean) / (std + 1e-8))

            if z_score > threshold:
                anomalies.append(i)

        return anomalies

# ═══════════════════════════════════════════════════════════════
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════

def example():
    """Пример использования"""

    # Создать синтетические данные
    training_data = []

    for i in range(50):
        sample = {
            'content': f"Задача {i}: анализ данных и рефлексия" + " осознанность" * (i % 3),
            'resonance': 0.3 + 0.4 * np.random.random() + (i / 100),
            'emotion': np.random.choice(['joy', 'clarity', 'curiosity', 'frustration']),
            'timestamp': float(i * 100)
        }
        training_data.append(sample)

    # Создать и обучить модель
    predictor = ResonancePredictor(model_type='random_forest')
    predictor.train(training_data)

    # Тестовое предсказание
    test_text = "Как улучшить осознанность через рефлексию и метакогницию?"

    history_timestamps = [s['timestamp'] for s in training_data]
    history_resonances = [s['resonance'] for s in training_data]
    history_emotions = [s['emotion'] for s in training_data]

    prediction = predictor.predict(
        test_text,
        history_timestamps,
        history_resonances,
        history_emotions
    )

    print(f"\n🔮 Predicted resonance: {prediction:.3f}")

    # Предсказание с доверительным интервалом
    pred_mean, pred_std = predictor.predict_with_confidence(
        test_text,
        history_timestamps,
        history_resonances,
        history_emotions
    )

    print(f"🔮 Prediction with confidence: {pred_mean:.3f} ± {pred_std:.3f}")

    # Прогноз временного ряда
    forecaster = TimeSeriesForecaster()
    forecasts = forecaster.forecast_next_n(history_resonances, n_steps=5)

    print(f"\n📈 Next 5 forecasts: {[f'{f:.3f}' for f in forecasts]}")

    # Обнаружение аномалий
    anomalies = forecaster.detect_anomalies(history_resonances)
    print(f"\n⚠️ Anomalies detected at indices: {anomalies[:5]}")

    # Сохранить модель
    predictor.save("example_predictor.pkl")

if __name__ == "__main__":
    example()
