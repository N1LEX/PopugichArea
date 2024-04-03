<h2>Run Project</h2>

> [!IMPORTANT]
> Проект запускается через **docker-compose** </br>
> _./run_project.sh_ - build all project services and run project

<hr>

<h2>Какую задачу бизнеса решает проект</h2>

Топ-менеджмент **UberPopug Inc** столкнулся с проблемой производительности сотрудников. Чтобы повысить производительность, было принято решение выкинуть текущий таск-трекер и написать особый **Awesome Task Exchange System** (aTES), который должен будет увеличить производительность сотрудников на неопределённый процент. Чтобы попуги развивались и изучали новые направления, была придумана инновационная схема ассайна каждой задачи на случайного сотрудника. А для повышения мотивации топ-менеджмент решил сделать корпоративный аккаунтинг в таск-трекере, чтобы по количеству выполненных задач выплачивать сотрудникам зарплату. При этом задачи оцениваются с плавающим коэффициентом (местами отрицательным).

<hr>

<h2>Сервис Аутентификации/Авторизации</h2>

**Popug Roles**: admin, manager, developer, tester, accountant. </br>

   **auth/signup** - зарегистрировать попуга </br>
      
      POST {"username": "popug", "email": "popug@popug.inc", "role": "admin", "password": "12345678"}

   **auth/signin** - авторизоваться </br>

      POST {"username": "popug", "password": "123456"}

<hr>

<h2>Таск Трекер</h2>

    task-tracker/

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/5a71ac87-5446-4360-bcfa-a5a72fb46f64)


    task-tracker/my/

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/780f1e77-f8af-41bb-b8ea-9662f0701571)

  **/task-tracker/assign** - Заассайнить задачи </br>
  Взять все открытые задачи и рандомно заассайнить каждую на любого из сотрудников (кроме менеджера и администратора). Не успел закрыть задачу до реассайна — делай следующую.

**/task-tracker/{id}/complete** - Отметить задачу завершенной. </br>

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/f631d7de-b1ea-4786-9989-fee4a6ed8275)

<hr>

<h2>Аккаунтинг</h2>

    accounting/ - Admin/Manager Dashboard

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/f96f77d8-bd4a-4e1d-aa44-1028627b3246)


    accounting/ - Worker Dashboard


![image](https://github.com/N1LEX/popug-tracker/assets/8479729/ec87b253-ae84-4cc0-abf2-9cd25a872bea)

**close_billing_cycles** - Задача закрытия бизнес цикла сотрудников. </br>
  1. Считать сколько денег сотрудник получил за рабочий день.
  2. Отправлять на почту сумму выплаты.

> [!NOTE]
> Отрицательный баланс переносится на следующий день. </br>
> Единственный способ его погасить - закрыть достаточное количество задач в течение дня.

<hr>

<h2>Аналитика</h2>

> [!NOTE]
> Dashboard, доступный только админам. </br>
> * Показывает сколько заработал топ-менеджмент за сегодня и сколько попугов ушло в минус </br>
> * Показывает самую дорогую задачу за день, месяц или заданный период </br>

    analytics/

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/ed4664f2-1e15-4009-a25c-a02dcb8820ba)

    analytics/most_expensive_task/?start_date=2024-04-01&end_date=2024-04-05

![image](https://github.com/N1LEX/popug-tracker/assets/8479729/fe2445a7-cddf-4006-b36c-8545e507f755)

<hr>

<h2>Сертификат</h2>
https://cert.tough-dev.school/6q5YpBciuWWjxg9yu3A8k3/

<hr>

<h2>Курс Асинхронная Архитектура </h2>
https://tough-dev.school/architecture

<hr>

<h2>Школа Сильных Программистов</h2>
https://tough-dev.school/

<hr>

</br></br>

