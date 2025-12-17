"""
Модуль crud.py реализует CRUD-операции(Create, Read, Update, Delete) для сущности
Order (заказ-наряд) в приложении автосервис. Он использует SQLAlchemy ORM и следует
принципу разделения ответственности: логика воздействия с базой данных отделена от
пользовательского интерфейса и конфигурации.
"""


from sqlalchemy.orm import Session
from models import Order


class OrderCRUD:
    @staticmethod
    def create_order(session: Session, customer_name: str, car_info: str, description: str = None) -> Order:
        """
        Создает новый заказ
        - создает объект Order, добавляет его в сессию через session.add(order)
        - session.flush() - отправляет SQL-запрос в БД без коммита, чтобы получить сгенерированный id
        - session.refresh() - синхронизирует объект order c текущим состоянием в БД(в т.ч. подтягивает id)
        """
        order = Order(
            customer_name=customer_name,
            car_info=car_info,
            description=description
        )
        session.add(order)
        session.flush()
        session.refresh(order)
        return order

    @staticmethod
    def get_all_orders(session: Session) -> list[Order]:
        """
        Получает все заказы, отсортированные по убыванию id(новые сверху)
        - .order_by(Order.id.desc()) - сортировка от новых к старым.
        - .all() - возвращает список всех найденных записей
        """
        return session.query(Order).order_by(Order.id.desc()).all()

    @staticmethod
    def get_order_by_id(session: Session, order_id: int) -> Order | None:
        # return session.query(Order).filter(Order.id == order_id).first()
        return session.get(Order, order_id)

    @staticmethod
    def update_order(session: Session, order_id: int, customer_name: str, car_info: str, description: str = None) -> Order | None:
        """
        Обновляет существующий заказ.
        - С начало получает существующий заказ через get_order_by_id
        - Если заказ найден - обновляет все поля (customer_name, car_info, description)
        - Вызывает session.add(order) — не обязательно, так как объект и так отслеживается сессией (если был получен из неё). Это избыточно, но безвредно.
        - session.refresh(order) — обновляет объект из БД (на случай, если триггеры или дефолты изменили данные). В данном случае, скорее всего, не требуется.
        - Возвращает обновлённый объект или None.
        """
        order = OrderCRUD.get_order_by_id(session, order_id)
        if order:
            order.customer_name = customer_name
            order.car_info = car_info
            order.description = description
            session.add(order)
            session.refresh(order)
            return order

    @staticmethod
    def delete_order(session: Session, order_id: int) -> bool:
        """
        Удаляет заказ по id
        Получает заказ через get_order_by_id
        Если найден - удаляет через session.delete(order)
        Возвращает True при успехе, False - если заказ не найден
        """
        order = OrderCRUD.get_order_by_id(session, order_id)
        if order:
            session.delete(order)
            return True
        return False


"""
Важно! Как и в других методах, коммит не выполняется внутри - его делает 
контекстный менеджер. Это правильно.
"""
