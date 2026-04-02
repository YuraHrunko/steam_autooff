import os
# =============================================================================
#  AutoOff — программа для автоматического выключения ПК
#  Два режима: таймер обратного отсчёта и ожидание завершения загрузки Steam
# =============================================================================

import os       # для команды shutdown
import ctypes   # для работы с Windows API (Alt+Tab)
import tkinter as tk
from tkinter import messagebox


# =============================================================================
#  ЦВЕТА ИНТЕРФЕЙСА
# =============================================================================

BG       = "#0f0f0f"   # основной фон (почти чёрный)
BG2      = "#1a1a1a"   # фон шапки и вкладок
BG3      = "#242424"   # фон элементов (спиннеры, прогресс-бар)
ACCENT   = "#c0392b"   # красный — акцент / кнопка отмены
ACCENT_H = "#e74c3c"   # красный светлее — при наведении
TEXT     = "#f0f0f0"   # основной текст
TEXT_DIM = "#666666"   # приглушённый текст (подсказки, статус)
GREEN    = "#27ae60"   # зелёный — кнопка старт
GREEN_H  = "#2ecc71"   # зелёный светлее — при наведении
TAB_ACT  = "#1e1e1e"   # фон активной вкладки


# =============================================================================
#  СТРОКИ ИНТЕРФЕЙСА
#  Хранятся как \uXXXX эскейпы — кодировка файла на диске не важна
# =============================================================================

S_TIMER_TAB      = "\u23f1  \u0422\u0430\u0439\u043c\u0435\u0440"           # ⏱  Таймер
S_STEAM_TAB      = "\U0001F3AE  Steam"                                        # 🎮  Steam
S_TITLE          = "\u23fb  AutoOff"                                          # ⏻  AutoOff
S_CLOSE          = "\u2715"                                                   # ✕
S_START          = "\u0421\u0422\u0410\u0420\u0422"                           # СТАРТ
S_CANCEL         = "\u041e\u0422\u041c\u0415\u041d\u0410"                     # ОТМЕНА
S_HOURS          = "\u0427\u0410\u0421\u042b"                                 # ЧАСЫ
S_MIN            = "\u041c\u0418\u041d"                                       # МИН
S_SEC            = "\u0421\u0415\u041a"                                       # СЕК
S_HINT_TIMER     = "\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0432\u0440\u0435\u043c\u044f \u0438 \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \u0441\u0442\u0430\u0440\u0442"   # Укажите время и нажмите старт
S_RUNNING        = "\u0418\u0434\u0451\u0442 \u043e\u0431\u0440\u0430\u0442\u043d\u044b\u0439 \u043e\u0442\u0441\u0447\u0451\u0442"                                              # Идёт обратный отсчёт
S_SHUTDOWN       = "\u0412\u044b\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435..."                                                                                            # Выключение...
S_CANCELLED      = "\u0422\u0430\u0439\u043c\u0435\u0440 \u043e\u0442\u043c\u0435\u043d\u0451\u043d"                                                                            # Таймер отменён
S_ERR_TITLE      = "\u041e\u0448\u0438\u0431\u043a\u0430"                     # Ошибка
S_ERR_TIME       = "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f"   # Введите корректное время
S_WARN_TITLE     = "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435"         # Внимание
S_WARN_ZERO      = "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0432\u0440\u0435\u043c\u044f \u0431\u043e\u043b\u044c\u0448\u0435 \u043d\u0443\u043b\u044f"  # Введите время больше нуля
S_STEAM_HINT     = "\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u0441\u0442\u0430\u0440\u0442 \u0447\u0442\u043e\u0431\u044b \u043d\u0430\u0447\u0430\u0442\u044c \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433"  # Нажмите старт чтобы начать мониторинг
S_STEAM_DL       = "\u2b07  Steam \u043a\u0430\u0447\u0430\u0435\u0442..."    # ⬇  Steam качает...
S_STEAM_WAIT     = "\u041e\u0436\u0438\u0434\u0430\u0435\u043c \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u043e\u0447\u0435\u0440\u0435\u0434\u0438"   # Ожидаем завершения очереди
S_STEAM_DONE     = "\u2714  \u041e\u0447\u0435\u0440\u0435\u0434\u044c \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430"                                             # ✔  Очередь завершена
S_STEAM_NONE     = "\u23f8  \u0421\u043a\u0430\u0447\u0438\u0432\u0430\u043d\u0438\u0435 \u043d\u0435 \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u043e"        # ⏸  Скачивание не обнаружено
S_STEAM_NOTFOUND = "\u26a0  \u041f\u0430\u043f\u043a\u0430 Steam \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430"                                                  # ⚠  Папка Steam не найдена
S_STEAM_WATCH    = "\u2b07  \u0421\u043b\u0435\u0436\u0443 \u0437\u0430 Steam..."    # ⬇  Слежу за Steam...
S_STEAM_MON_OFF  = "\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u043e\u0442\u043c\u0435\u043d\u0451\u043d"                                               # Мониторинг отменён
S_OFF_IN         = "\u0412\u044b\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0447\u0435\u0440\u0435\u0437 {} \u0441\u0435\u043a..."                                  # Выключение через {} сек...
S_STEAM_DESC     = (
    "\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u0442 \u043f\u0430\u043f\u043a\u0443 steamapps/downloading\n"
    "\u0412\u044b\u043a\u043b\u044e\u0447\u0438\u0442 \u041f\u041a \u0447\u0435\u0440\u0435\u0437 60 \u0441\u0435\u043a "
    "\u043f\u043e\u0441\u043b\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u043e\u0447\u0435\u0440\u0435\u0434\u0438"
)  # "Мониторит папку steamapps/downloading\nВыключит ПК через 60 сек после завершения очереди"
S_NF_TITLE       = "\u041d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e"   # Не найдено
S_NF_MSG         = (
    "\u041f\u0430\u043f\u043a\u0430 Steam \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430.\n"
    "\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0442\u044c \u0432\u0440\u0443\u0447\u043d\u0443\u044e "
    "\u0432 STEAM_PATHS \u0432 \u043a\u043e\u0434\u0435."
)  # "Папка Steam не найдена.\nДобавьте путь вручную в STEAM_PATHS в коде."


# =============================================================================
#  ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ СОСТОЯНИЯ
# =============================================================================

timer_running      = False   # True пока идёт обратный отсчёт
steam_watching     = False   # True пока идёт слежка за Steam
remaining_seconds  = 0       # сколько секунд осталось до выключения
total_seconds      = 0       # сколько секунд было изначально (для прогресс-бара)
after_id           = None    # ID отложенного вызова таймера (чтобы можно было отменить)
steam_after_id     = None    # ID отложенного вызова слежки Steam
current_tab        = "timer" # какая вкладка сейчас активна
steam_idle_seconds = 0       # сколько секунд Steam уже не качает

IDLE_THRESHOLD = 60          # через сколько секунд простоя Steam выключать ПК

# папки, где Steam хранит загружаемые файлы — добавь свой путь если не находит
STEAM_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\downloading",
    r"C:\Program Files\Steam\steamapps\downloading",
    r"D:\Steam\steamapps\downloading",
    r"D:\SteamLibrary\steamapps\downloading",
]


# =============================================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ — STEAM
# =============================================================================

def find_steam_downloading():
    """Ищет папку downloading среди известных путей Steam, возвращает путь или None."""
    for p in STEAM_PATHS:
        if os.path.isdir(p):
            return p
    return None


def is_downloading(path):
    """Возвращает True если в папке есть файлы (значит что-то качается)."""
    try:
        entries = [e for e in os.listdir(path) if not e.startswith(".")]
        return len(entries) > 0
    except Exception:
        return False


# =============================================================================
#  ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК
# =============================================================================

def switch_tab(tab):
    """Переключает вкладку. Блокируется если активно выключение."""
    global current_tab
    # нельзя переключаться пока идёт таймер или слежка
    if timer_running or steam_watching:
        return
    current_tab = tab
    if tab == "timer":
        tab_timer_lbl.config(fg=TEXT, bg=TAB_ACT)
        tab_steam_lbl.config(fg=TEXT_DIM, bg=BG2)
        frame_steam.pack_forget()
        frame_timer_wrap.pack(fill="both", expand=True)
    else:
        tab_steam_lbl.config(fg=TEXT, bg=TAB_ACT)
        tab_timer_lbl.config(fg=TEXT_DIM, bg=BG2)
        frame_timer_wrap.pack_forget()
        frame_steam.pack(fill="both", expand=True)


def lock_tabs():
    """Убирает курсор-руку с вкладок — визуально показывает что они недоступны."""
    tab_timer_lbl.config(cursor="")
    tab_steam_lbl.config(cursor="")


def unlock_tabs():
    """Возвращает курсор-руку на вкладки."""
    tab_timer_lbl.config(cursor="hand2")
    tab_steam_lbl.config(cursor="hand2")


# =============================================================================
#  ЛОГИКА ТАЙМЕРА
# =============================================================================

def update_countdown():
    """Вызывается каждую секунду: обновляет цифры и прогресс-бар."""
    global remaining_seconds, after_id, timer_running
    if not timer_running:
        return
    # разбиваем секунды на часы/минуты/секунды для отображения
    h = remaining_seconds // 3600
    m = (remaining_seconds % 3600) // 60
    s = remaining_seconds % 60
    countdown_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
    # заполняем прогресс-бар пропорционально прошедшему времени
    progress = 1 - (remaining_seconds / total_seconds) if total_seconds > 0 else 1
    canvas_bar.coords(bar_rect, 0, 0, int(progress * 460), 6)
    # время вышло — запускаем выключение
    if remaining_seconds <= 0:
        timer_running = False
        countdown_label.config(text="00:00:00")
        status_label.config(text=S_SHUTDOWN, fg=ACCENT)
        btn_start.config(state="disabled")
        root.after(1500, do_shutdown)
        return
    # уменьшаем счётчик и планируем следующий вызов через 1 секунду
    remaining_seconds -= 1
    after_id = root.after(1000, update_countdown)


def start_timer():
    """Читает значения из спиннеров и запускает таймер."""
    global timer_running, remaining_seconds, total_seconds, after_id
    if timer_running:
        return
    # читаем часы/минуты/секунды из полей ввода
    try:
        h = int(var_h.get())
        m = int(var_m.get())
        s = int(var_s.get())
    except ValueError:
        messagebox.showerror(S_ERR_TITLE, S_ERR_TIME)
        return
    total = h * 3600 + m * 60 + s
    if total <= 0:
        messagebox.showwarning(S_WARN_TITLE, S_WARN_ZERO)
        return
    # сохраняем время и запускаем отсчёт
    total_seconds = total
    remaining_seconds = total
    timer_running = True
    lock_tabs()
    # скрываем поля ввода, показываем большой таймер
    frame_input.pack_forget()
    frame_countdown.pack(pady=10)
    btn_start.config(state="disabled")
    btn_cancel.config(state="normal", bg=ACCENT, fg=TEXT)
    status_label.config(text=S_RUNNING, fg=TEXT_DIM)
    update_countdown()


def cancel_timer():
    """Останавливает таймер и возвращает интерфейс в исходное состояние."""
    global timer_running, after_id
    # отменяем запланированный вызов update_countdown
    if after_id:
        root.after_cancel(after_id)
        after_id = None
    timer_running = False
    unlock_tabs()
    # скрываем таймер, показываем поля ввода обратно
    frame_countdown.pack_forget()
    frame_input.pack(pady=10)
    btn_start.config(state="normal")
    btn_cancel.config(state="disabled", bg=BG3, fg=TEXT_DIM)
    status_label.config(text=S_CANCELLED, fg=GREEN)
    countdown_label.config(text="00:00:00")
    canvas_bar.coords(bar_rect, 0, 0, 0, 6)
    # через 2 секунды возвращаем подсказку
    root.after(2000, lambda: status_label.config(text=S_HINT_TIMER, fg=TEXT_DIM))


# =============================================================================
#  ЛОГИКА СЛЕЖКИ ЗА STEAM
# =============================================================================

def watch_steam():
    """Вызывается каждые 3 секунды: проверяет идёт ли загрузка в Steam."""
    global steam_watching, steam_after_id, steam_idle_seconds
    if not steam_watching:
        return
    dl_path = find_steam_downloading()
    # папка Steam не найдена — показываем предупреждение и проверяем снова через 5 сек
    if dl_path is None:
        steam_status.config(text=S_STEAM_NOTFOUND, fg=ACCENT)
        steam_after_id = root.after(5000, watch_steam)
        return
    if is_downloading(dl_path):
        # что-то качается — сбрасываем счётчик простоя
        steam_idle_seconds = 0
        steam_status.config(text=S_STEAM_DL, fg=GREEN)
        steam_progress_label.config(text=S_STEAM_WAIT)
    else:
        # ничего не качается — увеличиваем счётчик простоя
        steam_idle_seconds += 3
        left = max(0, IDLE_THRESHOLD - steam_idle_seconds)
        if steam_idle_seconds <= 3:
            steam_status.config(text=S_STEAM_NONE, fg=TEXT_DIM)
        else:
            steam_status.config(text=S_STEAM_DONE, fg=GREEN)
        steam_progress_label.config(text=S_OFF_IN.format(left))
        # простой превысил порог — выключаем
        if steam_idle_seconds >= IDLE_THRESHOLD:
            steam_status.config(text=S_SHUTDOWN, fg=ACCENT)
            steam_progress_label.config(text="")
            root.after(1500, do_shutdown)
            return
    # планируем следующую проверку через 3 секунды
    steam_after_id = root.after(3000, watch_steam)


def start_steam_watch():
    """Запускает слежку за папкой загрузок Steam."""
    global steam_watching, steam_idle_seconds
    if steam_watching:
        return
    dl_path = find_steam_downloading()
    if dl_path is None:
        messagebox.showwarning(S_NF_TITLE, S_NF_MSG)
        return
    steam_idle_seconds = 0
    steam_watching = True
    lock_tabs()
    btn_steam_start.config(state="disabled")
    btn_steam_cancel.config(state="normal", bg=ACCENT, fg=TEXT)
    steam_status.config(text=S_STEAM_WATCH, fg=TEXT_DIM)
    steam_progress_label.config(text="")
    watch_steam()


def cancel_steam_watch():
    """Останавливает слежку за Steam."""
    global steam_watching, steam_after_id
    # отменяем запланированный вызов watch_steam
    if steam_after_id:
        root.after_cancel(steam_after_id)
        steam_after_id = None
    steam_watching = False
    unlock_tabs()
    btn_steam_start.config(state="normal")
    btn_steam_cancel.config(state="disabled", bg=BG3, fg=TEXT_DIM)
    steam_status.config(text=S_STEAM_MON_OFF, fg=GREEN)
    steam_progress_label.config(text="")
    root.after(2000, lambda: steam_status.config(text=S_STEAM_HINT, fg=TEXT_DIM))


def do_shutdown():
    """Отправляет команду на выключение ПК и закрывает приложение."""
    os.system("shutdown /s /t 1")
    root.destroy()


# =============================================================================
#  СОЗДАНИЕ ГЛАВНОГО ОКНА
# =============================================================================

root = tk.Tk()
root.title("AutoOff")
root.geometry("520x400")
root.resizable(False, False)
root.configure(bg=BG)
root.eval("tk::PlaceWindow . center")
root.overrideredirect(True)   # убираем системный заголовок Windows


def fix_taskbar():
    """Возвращает окно в Alt+Tab и на панель задач через Windows API.
    Нужно потому что overrideredirect(True) по умолчанию скрывает окно отовсюду."""
    GWL_EXSTYLE      = -20
    WS_EX_APPWINDOW  = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    hwnd  = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    # убираем флаг "скрыть из Alt+Tab", добавляем флаг "показать в панели задач"
    style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(10, root.wm_deiconify)


root.after(10, fix_taskbar)


# =============================================================================
#  ПЕРЕТАСКИВАНИЕ ОКНА (раз нет системного заголовка — делаем своё)
# =============================================================================

def start_drag(event):
    """Запоминаем позицию курсора при нажатии."""
    root._drag_x = event.x
    root._drag_y = event.y


def do_drag(event):
    """При движении мыши смещаем окно на ту же дельту."""
    x = root.winfo_x() + event.x - root._drag_x
    y = root.winfo_y() + event.y - root._drag_y
    root.geometry(f"+{x}+{y}")


def hover(btn, color_in, color_out):
    """Подсветка кнопки при наведении мыши."""
    btn.bind("<Enter>", lambda e: btn.config(bg=color_in))
    btn.bind("<Leave>", lambda e: btn.config(bg=color_out))


# =============================================================================
#  ШАПКА (заголовок + кнопка закрытия)
# =============================================================================

frame_header = tk.Frame(root, bg=BG2, height=50)
frame_header.pack(fill="x")
# шапка тоже участвует в перетаскивании
frame_header.bind("<ButtonPress-1>", start_drag)
frame_header.bind("<B1-Motion>",     do_drag)

tk.Label(frame_header, text=S_TITLE, font=("Segoe UI", 13, "bold"),
         bg=BG2, fg=TEXT, padx=20).pack(side="left", pady=12)

btn_close = tk.Label(frame_header, text=S_CLOSE, font=("Segoe UI", 13),
                     bg=BG2, fg=TEXT_DIM, padx=16, cursor="hand2")
btn_close.pack(side="right", pady=12)
btn_close.bind("<Enter>",    lambda e: btn_close.config(fg=ACCENT))
btn_close.bind("<Leave>",    lambda e: btn_close.config(fg=TEXT_DIM))
btn_close.bind("<Button-1>", lambda e: root.destroy())


# =============================================================================
#  ВКЛАДКИ (Таймер / Steam)
# =============================================================================

frame_tabs = tk.Frame(root, bg=BG2)
frame_tabs.pack(fill="x")

tab_timer_lbl = tk.Label(frame_tabs, text=S_TIMER_TAB,
                          font=("Segoe UI", 10, "bold"),
                          bg=TAB_ACT, fg=TEXT, padx=24, pady=8, cursor="hand2")
tab_timer_lbl.pack(side="left")

tab_steam_lbl = tk.Label(frame_tabs, text=S_STEAM_TAB,
                          font=("Segoe UI", 10, "bold"),
                          bg=BG2, fg=TEXT_DIM, padx=24, pady=8, cursor="hand2")
tab_steam_lbl.pack(side="left")

# тонкий разделитель под вкладками
tk.Frame(root, bg=BG3, height=1).pack(fill="x")

tab_timer_lbl.bind("<Button-1>", lambda e: switch_tab("timer"))
tab_steam_lbl.bind("<Button-1>", lambda e: switch_tab("steam"))


def tab_hover(lbl, active_tab):
    """Hover-эффект для вкладок: светлеет при наведении если вкладка доступна."""
    def enter(e):
        if current_tab != active_tab and not timer_running and not steam_watching:
            lbl.config(fg=TEXT)
    def leave(e):
        if current_tab != active_tab:
            lbl.config(fg=TEXT_DIM)
    lbl.bind("<Enter>", enter)
    lbl.bind("<Leave>", leave)


tab_hover(tab_timer_lbl, "timer")
tab_hover(tab_steam_lbl, "steam")


# =============================================================================
#  ВКЛАДКА: ТАЙМЕР
# =============================================================================

frame_timer_wrap = tk.Frame(root, bg=BG)
frame_timer_wrap.pack(fill="both", expand=True)

# строка статуса вверху вкладки
status_label = tk.Label(frame_timer_wrap, text=S_HINT_TIMER,
                          font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM)
status_label.pack(pady=(18, 0))

# блок с полями ввода часы:минуты:секунды
frame_input = tk.Frame(frame_timer_wrap, bg=BG)
frame_input.pack(pady=10)


def make_spinbox(parent, width=4):
    """Создаёт один спиннер (поле с кнопками ▲▼) в стиле приложения."""
    var = tk.StringVar(value="00")
    sb  = tk.Spinbox(
        parent, from_=0, to=99, textvariable=var, width=width,
        font=("Segoe UI", 28, "bold"),
        bg=BG3, fg=TEXT, buttonbackground=BG3, insertbackground=TEXT,
        relief="flat", bd=0,
        highlightthickness=1, highlightbackground=BG3, highlightcolor=ACCENT,
        justify="center", format="%02.0f",
    )
    return sb, var


def make_sep(parent):
    """Разделитель ':' между спиннерами."""
    return tk.Label(parent, text=":", font=("Segoe UI", 30, "bold"),
                    bg=BG, fg=TEXT_DIM, padx=4)


sb_h, var_h = make_spinbox(frame_input)   # часы
sb_m, var_m = make_spinbox(frame_input)   # минуты
sb_s, var_s = make_spinbox(frame_input)   # секунды

sb_h.grid(row=0, column=0)
make_sep(frame_input).grid(row=0, column=1)
sb_m.grid(row=0, column=2)
make_sep(frame_input).grid(row=0, column=3)
sb_s.grid(row=0, column=4)

# подписи под спиннерами
for col, txt in [(0, S_HOURS), (2, S_MIN), (4, S_SEC)]:
    tk.Label(frame_input, text=txt, font=("Segoe UI", 7),
             bg=BG, fg=TEXT_DIM).grid(row=1, column=col, pady=(4, 0))

# большой таймер обратного отсчёта (скрыт до нажатия СТАРТ)
frame_countdown = tk.Frame(frame_timer_wrap, bg=BG)
countdown_label = tk.Label(frame_countdown, text="00:00:00",
                             font=("Segoe UI", 52, "bold"), bg=BG, fg=TEXT)
countdown_label.pack()

# прогресс-бар заполняется слева направо по мере истечения времени
canvas_bar = tk.Canvas(frame_timer_wrap, width=460, height=6,
                        bg=BG3, highlightthickness=0, bd=0)
canvas_bar.pack(pady=(14, 0))
bar_rect = canvas_bar.create_rectangle(0, 0, 0, 6, fill=ACCENT, outline="")

# кнопки СТАРТ / ОТМЕНА
frame_btns = tk.Frame(frame_timer_wrap, bg=BG)
frame_btns.pack(pady=16)

btn_start = tk.Button(
    frame_btns, text=S_START, font=("Segoe UI", 11, "bold"),
    bg=GREEN, fg=TEXT, activebackground=GREEN_H, activeforeground=TEXT,
    relief="flat", bd=0, padx=36, pady=10, cursor="hand2",
    command=start_timer,
)
btn_start.grid(row=0, column=0, padx=8)
hover(btn_start, GREEN_H, GREEN)

btn_cancel = tk.Button(
    frame_btns, text=S_CANCEL, font=("Segoe UI", 11, "bold"),
    bg=BG3, fg=TEXT_DIM, activebackground=ACCENT_H, activeforeground=TEXT,
    relief="flat", bd=0, padx=36, pady=10, cursor="hand2",
    state="disabled", command=cancel_timer,
)
btn_cancel.grid(row=0, column=1, padx=8)


# =============================================================================
#  ВКЛАДКА: STEAM
# =============================================================================

frame_steam = tk.Frame(root, bg=BG)

tk.Frame(frame_steam, bg=BG, height=20).pack()   # отступ сверху

# основной статус (что сейчас происходит)
steam_status = tk.Label(frame_steam, text=S_STEAM_HINT,
                          font=("Segoe UI", 11), bg=BG, fg=TEXT_DIM)
steam_status.pack(pady=(10, 4))

# вторая строка статуса (обратный отсчёт до выключения)
steam_progress_label = tk.Label(frame_steam, text="",
                                  font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM)
steam_progress_label.pack()

# описание как работает режим
tk.Label(frame_steam, text=S_STEAM_DESC,
         font=("Segoe UI", 8), bg=BG, fg=TEXT_DIM, justify="center",
         ).pack(pady=(16, 0))

# кнопки СТАРТ / ОТМЕНА
frame_steam_btns = tk.Frame(frame_steam, bg=BG)
frame_steam_btns.pack(pady=22)

btn_steam_start = tk.Button(
    frame_steam_btns, text=S_START, font=("Segoe UI", 11, "bold"),
    bg=GREEN, fg=TEXT, activebackground=GREEN_H, activeforeground=TEXT,
    relief="flat", bd=0, padx=36, pady=10, cursor="hand2",
    command=start_steam_watch,
)
btn_steam_start.grid(row=0, column=0, padx=8)
hover(btn_steam_start, GREEN_H, GREEN)

btn_steam_cancel = tk.Button(
    frame_steam_btns, text=S_CANCEL, font=("Segoe UI", 11, "bold"),
    bg=BG3, fg=TEXT_DIM, activebackground=ACCENT_H, activeforeground=TEXT,
    relief="flat", bd=0, padx=36, pady=10, cursor="hand2",
    state="disabled", command=cancel_steam_watch,
)
btn_steam_cancel.grid(row=0, column=1, padx=8)


# =============================================================================
#  ЗАПУСК
# =============================================================================

root.mainloop()
