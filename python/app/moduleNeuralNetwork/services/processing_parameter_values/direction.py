import numpy as np


# Ключевое слово
class Direction:
    __default_value = 10

    def init_operation(self, text: str) -> list:
        return []

    def generate_lambda_expression(self, operations: list):
        for operation in operations:
            if operation['is_percent']:
                str_operations = f"({str_operations}) * "
            else:
                str_operations += f" {operation['operator'].value} {operation['value']}"

        return eval(f"lambda x: {str_operations}")


# Начальные углы ориентации камеры (в градусах)
yaw = 0  # Поворот вокруг оси Z
pitch = 0  # Поворот вокруг оси Y
roll = 0  # Поворот вокруг оси X

# Изменения углов ориентации камеры (в градусах)
delta_yaw = 1  # Изменение угла yaw
delta_pitch = 0.5  # Изменение угла pitch
delta_roll = 0.1  # Изменение угла roll

# Обновление ориентации камеры в цикле
for step in range(100):  # Пример: 100 шагов движения камеры
    # Обновление углов ориентации камеры
    yaw += delta_yaw
    pitch += delta_pitch
    roll += delta_roll

    # Проверка на переполнение углов
    yaw = yaw % 360
    pitch = pitch % 360
    roll = roll % 360

    print(f"Шаг {step + 1}:")
    print(f"Новые углы ориентации камеры: yaw={yaw}, pitch={pitch}, roll={roll}")

func = lambda x, y, z: (x + 1, y + 1, z + 1)
print(func(4, 4, 4))
