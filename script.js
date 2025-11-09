document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');

    // Проверяем, что Telegram WebApp доступен
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = Telegram.WebApp;

        // Устанавливаем цвет фона и заголовка с проверкой доступности
        if (tg.setHeaderColor) {
            try {
                tg.setHeaderColor('#6c5ce7');
            } catch (e) {
                console.log('setHeaderColor не поддерживается:', e);
            }
        }

        if (tg.setBackgroundColor) {
            try {
                tg.setBackgroundColor('#a8edea');
            } catch (e) {
                console.log('setBackgroundColor не поддерживается:', e);
            }
        }

        // Готовим Mini App к показу
        tg.ready();

        // Обработчик кнопки "Начать"
        startButton.addEventListener('click', () => {
            // Отправляем данные в бота
            Telegram.WebApp.sendData('start');
            // Закрываем Mini App
            Telegram.WebApp.close();
        });
    } else {
        console.error('Telegram WebApp не доступен!');
        startButton.disabled = true;
        startButton.innerText = 'Ошибка: Не в Telegram';
    }
});