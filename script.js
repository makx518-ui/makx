document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');

    // Проверяем, что Telegram WebApp доступен
    if (window.Telegram && window.Telegram.WebApp) {
        // Устанавливаем цвет фона и заголовка
        Telegram.WebApp.setHeaderColor('#6c5ce7');
        Telegram.WebApp.setBackgroundColor('#a8edea');

        // Готовим Mini App к показу
        Telegram.WebApp.ready();

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