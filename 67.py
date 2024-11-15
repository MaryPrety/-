import tkinter as tk
import random
import math
from PIL import Image, ImageTk
import pygame
import time

# Параметры гонки
NUM_PARTICIPANTS = 5
NUM_LAPS = 5
CIRCLE_RADIUS = 300
CIRCLE_CENTER = (400, 400)
CRUMB_INTERVAL = 5  # Интервал между крошками

# Загрузка спрайтов тараканов, грязной кружки и крошек
def load_sprites(path):
    sprite = Image.open(path)
    sprite = sprite.resize((60, 60), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(sprite)

def load_dirty_cup(path):
    sprite = Image.open(path)
    sprite = sprite.resize((80, 80), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(sprite)

def load_crumbs(path):
    sprite = Image.open(path)
    sprite = sprite.resize((20, 20), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(sprite)

# Класс для участника гонки
class Participant:
    def __init__(self, canvas, sprite, trajectory_type, crumbs_sprite, speed):
        self.canvas = canvas
        self.sprite = sprite
        self.crumbs_sprite = crumbs_sprite
        self.angle = random.uniform(0, 2 * math.pi)
        self.trajectory_type = trajectory_type
        self.speed = speed
        self.acceleration = 0.0  # Начальное ускорение
        self.laps = 0
        self.start_time = time.time()  # Время начала движения
        self.item = canvas.create_image(0, 0, image=sprite, anchor=tk.CENTER)
        self.speed_text = canvas.create_text(0, 0, text=f"Speed: {self.speed:.2f}", fill="black", font=("Arial", 14))
        self.crumbs = []
        self.crumb_step = 0
        self.update_position()

    def update_position(self):
        if self.trajectory_type == 1:  # Круг
            x = CIRCLE_CENTER[0] + CIRCLE_RADIUS * math.cos(self.angle)
            y = CIRCLE_CENTER[1] + CIRCLE_RADIUS * math.sin(self.angle)
        elif self.trajectory_type == 2:  # Эллипс
            x = CIRCLE_CENTER[0] + CIRCLE_RADIUS * 0.5 * math.cos(self.angle)
            y = CIRCLE_CENTER[1] + CIRCLE_RADIUS * math.sin(self.angle)
        elif self.trajectory_type == 3:  # Изменение радиуса
            x = CIRCLE_CENTER[0] + (CIRCLE_RADIUS + 50 * math.sin(self.angle * 2)) * math.cos(self.angle)
            y = CIRCLE_CENTER[1] + (CIRCLE_RADIUS + 50 * math.sin(self.angle * 2)) * math.sin(self.angle)
        self.canvas.coords(self.item, x, y)
        self.canvas.coords(self.speed_text, x, y - 30)
        if self.crumb_step % CRUMB_INTERVAL == 0:
            self.crumbs.append(self.canvas.create_image(x, y, image=self.crumbs_sprite, anchor=tk.CENTER))
        self.crumb_step += 1

    def move(self, t):
        self.angle += self.speed / 100
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
            self.laps += 1
            self.clear_crumbs()
            self.change_trajectory()
        self.update_position()
        self.update_speed_and_acceleration(t)
        self.canvas.itemconfig(self.speed_text, text=f"Speed: {self.speed:.2f}")

    def update_speed_and_acceleration(self, t):
        if self.trajectory_type == 1:  # Круг
            self.acceleration = 0.05  # Постоянное ускорение
            self.speed += self.acceleration
        elif self.trajectory_type == 2:  # Эллипс
            if t % 10 == 0:
                self.acceleration = 0.1  # Мгновенное ускорение
                self.speed += self.acceleration
            else:
                self.acceleration = 0.0
        elif self.trajectory_type == 3:  # Изменение радиуса
            if t % 5 == 0:
                self.acceleration = 0.05  # Периодическое ускорение
                self.speed += self.acceleration
            else:
                self.acceleration = 0.0

    def clear_crumbs(self):
        for crumb in self.crumbs:
            self.canvas.delete(crumb)
        self.crumbs = []
        self.crumb_step = 0

    def change_trajectory(self):
        self.trajectory_type = random.choice([1, 2, 3])

# Основная функция для запуска гонки
def start_race():
    sprites = [load_sprites(f"sprite_roach_{i+1}.png") for i in range(NUM_PARTICIPANTS)]
    crumbs_sprites = [load_crumbs(f"crumb_{i+1}.png") for i in range(NUM_PARTICIPANTS)]
    trajectory_types = [random.choice([1, 2, 3]) for _ in range(NUM_PARTICIPANTS)]
    speeds = [random.uniform(0.5, 2.5) for _ in range(NUM_PARTICIPANTS)]  # Уменьшенная начальная скорость
    participants = [Participant(canvas, sprites[i], trajectory_types[i], crumbs_sprites[i], speeds[i]) for i in range(NUM_PARTICIPANTS)]
    race_loop(participants, 0)

def race_loop(participants, t):
    for participant in participants:
        participant.move(t)
        if participant.laps >= NUM_LAPS:
            participants.remove(participant)
            canvas.delete(participant.item)
            canvas.delete(participant.speed_text)
            participant.clear_crumbs()
    if participants:
        canvas.after(50, race_loop, participants, t + 1)
        if t % 10 == 0:
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.1)
    else:
        print("Гонка завершена!")
        pygame.mixer.music.stop()
        if participants:  # Проверка на пустоту списка
            display_results(participants)
        else:
            display_results([])

def display_results(participants):
    # Сортируем участников по скорости (от большей к меньшей)
    participants.sort(key=lambda p: p.speed, reverse=True)
    
    # Формируем текст результатов
    results = "\n".join([f"Таракан {i + 1}: Скорость: {p.speed:.2f}, Траектория: {p.trajectory_type}, Время: {time.time() - p.start_time:.2f} сек"
                         for i, p in enumerate(participants)])
    
    # Выводим результаты на экран
    canvas.create_text(400, 200, text="Результаты гонки", fill="black", font=("Arial", 18, "bold"), justify=tk.CENTER)
    canvas.create_text(400, 250, text=results, fill="black", font=("Arial", 14), justify=tk.CENTER)
    
    # Отображаем лидера
    if participants:
        best_roach = participants[0]
        canvas.create_text(400, 400, text=f"Лидер гонки: Таракан {1}", fill="black", font=("Arial", 16, "bold"))
        canvas.create_image(400, 450, image=best_roach.sprite, anchor=tk.CENTER)
        canvas.create_text(400, 500, text=f"Скорость: {best_roach.speed:.2f}, Траектория: {best_roach.trajectory_type}, "
                                          f"Время: {time.time() - best_roach.start_time:.2f} сек",
                           fill="black", font=("Arial", 14), justify=tk.CENTER)

    # Кнопка повторного запуска гонки
    restart_button = tk.Button(root, text="Повторить гонку", command=restart_race)
    restart_button.place(x=350, y=700)

    # Добавляем управление стрелками для пролистывания участников
    current_index = 0

    def update_display(index):
        canvas.delete("details")
        participant = participants[index]
        canvas.create_image(400, 450, image=participant.sprite, anchor=tk.CENTER, tags="details")
        canvas.create_text(400, 500, text=f"Таракан {index + 1}: Скорость: {participant.speed:.2f}, Траектория: {participant.trajectory_type}, "
                                          f"Время: {time.time() - participant.start_time:.2f} сек",
                           fill="black", font=("Arial", 14), justify=tk.CENTER, tags="details")

    def on_arrow_key(event):
        nonlocal current_index
        if event.keysym == "Up":
            current_index = (current_index - 1) % len(participants)
        elif event.keysym == "Down":
            current_index = (current_index + 1) % len(participants)
        update_display(current_index)

    # Привязываем обработку событий
    root.bind("<Up>", on_arrow_key)
    root.bind("<Down>", on_arrow_key)

    # Отображаем первого участника
    if participants:
        update_display(current_index)

# Функция для повторного запуска гонки
def restart_race():
    canvas.delete("all")
    canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)
    canvas.create_oval(CIRCLE_CENTER[0] - CIRCLE_RADIUS, CIRCLE_CENTER[1] - CIRCLE_RADIUS,
                       CIRCLE_CENTER[0] + CIRCLE_RADIUS, CIRCLE_CENTER[1] + CIRCLE_RADIUS, outline="black")
    canvas.create_image(CIRCLE_CENTER[0] + CIRCLE_RADIUS, CIRCLE_CENTER[1], image=dirty_cup_sprite, anchor=tk.CENTER)
    start_race()

# Создание графического интерфейса
root = tk.Tk()
root.title("Гонка тараканов")

# Загрузка фона
bg_image = Image.open("background.png")
bg_image = bg_image.resize((800, 800), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=800, height=800)
canvas.pack()

# Установка фона
canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)

# Рисуем круг траектории
canvas.create_oval(CIRCLE_CENTER[0] - CIRCLE_RADIUS, CIRCLE_CENTER[1] - CIRCLE_RADIUS,
                   CIRCLE_CENTER[0] + CIRCLE_RADIUS, CIRCLE_CENTER[1] + CIRCLE_RADIUS, outline="black")

# Добавляем спрайт грязной кружки на конец круга
dirty_cup_sprite = load_dirty_cup("dirty_cup.png")
canvas.create_image(CIRCLE_CENTER[0] + CIRCLE_RADIUS, CIRCLE_CENTER[1], image=dirty_cup_sprite, anchor=tk.CENTER)

# Запуск музыки
pygame.mixer.init()
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Запуск гонки
start_race()

root.mainloop()
