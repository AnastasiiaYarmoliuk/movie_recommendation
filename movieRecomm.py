import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import json
import os


class Movie:
    """Клас для представлення фільму з усіма його атрибутами."""
    
    def __init__(self, movie_id, title, overview, poster_path, 
                 genre_names, release_date, vote_average):
        """
        Ініціалізація об'єкта фільму.
        
        Args:
            movie_id (int): Унікальний ID фільму
            title (str): Назва фільму
            overview (str): Опис фільму
            poster_path (str): Шлях до постеру
            genre_names (list): Список жанрів
            release_date (str): Дата виходу
            vote_average (float): Середня оцінка
        """
        self.movie_id = movie_id
        self.title = title
        self.overview = overview
        self.poster_path = poster_path
        self.genre_names = genre_names
        self.release_date = release_date
        self.vote_average = vote_average
        self.is_saved = False
        self.is_watched = False
    
    def to_dict(self):
        """Перетворення об'єкта фільму в словник для збереження."""
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'overview': self.overview,
            'poster_path': self.poster_path,
            'genre_names': self.genre_names,
            'release_date': self.release_date,
            'vote_average': self.vote_average,
            'is_saved': self.is_saved,
            'is_watched': self.is_watched
        }
    
    @classmethod
    def from_dict(cls, data):
        """Створення об'єкта фільму зі словника."""
        movie = cls(
            data['movie_id'], data['title'], data['overview'],
            data['poster_path'], data['genre_names'],
            data['release_date'], data['vote_average']
        )
        movie.is_saved = data.get('is_saved', False)
        movie.is_watched = data.get('is_watched', False)
        return movie


class MovieDatabase:
    """Клас для роботи з The Movie Database API."""
    
    def __init__(self):
        """Ініціалізація з API ключем."""
        # Використовуємо публічний API ключ для демонстрації
        self.api_key = "your_api_key_here"  # Замініть на ваш API ключ
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        
        # Словник жанрів з їх ID
        self.genres = {
            'Екшн': 28,
            'Пригоди': 12,
            'Комедія': 35,
            'Драма': 18,
            'Фантастика': 878,
            'Жахи': 27,
            'Романтика': 10749,
            'Трилер': 53,
            'Анімація': 16,
            'Документальний': 99
        }
    
    def get_movies_by_genre(self, genre_name):
        """
        Отримання фільмів за жанром.
        
        Args:
            genre_name (str): Назва жанру
            
        Returns:
            list: Список об'єктів Movie
        """
        if genre_name not in self.genres:
            return []
        
        genre_id = self.genres[genre_name]
        url = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'with_genres': genre_id,
            'sort_by': 'popularity.desc',
            'language': 'uk-UA'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            movies = []
            for movie_data in data.get('results', [])[:10]:  # Беремо перші 10 фільмів
                # Отримуємо назви жанрів
                genre_names = self._get_genre_names(movie_data.get('genre_ids', []))
                
                movie = Movie(
                    movie_id=movie_data.get('id'),
                    title=movie_data.get('title', 'Невідома назва'),
                    overview=movie_data.get('overview', 'Опис недоступний'),
                    poster_path=movie_data.get('poster_path'),
                    genre_names=genre_names,
                    release_date=movie_data.get('release_date', ''),
                    vote_average=movie_data.get('vote_average', 0)
                )
                movies.append(movie)
            
            return movies
            
        except requests.exceptions.RequestException as e:
            print(f"Помилка при отриманні фільмів: {e}")
            return self._get_sample_movies(genre_name)
    
    def _get_genre_names(self, genre_ids):
        """Перетворення ID жанрів в їх назви."""
        genre_map = {v: k for k, v in self.genres.items()}
        return [genre_map.get(gid, 'Невідомий') for gid in genre_ids 
                if gid in genre_map]
    
    def _get_sample_movies(self, genre_name):
        """Повертає зразкові фільми, якщо API недоступне."""
        sample_movies = {
            'Екшн': [
                Movie(1, "Джон Вік", "Професійний кілер повертається до справи", 
                      None, ["Екшн"], "2014-10-24", 7.4),
                Movie(2, "Матриця", "Програміст дізнається правду про реальність", 
                      None, ["Екшн", "Фантастика"], "1999-03-31", 8.7)
            ],
            'Комедія': [
                Movie(3, "Один вдома", "Хлопчик захищає дім від грабіжників", 
                      None, ["Комедія"], "1990-11-16", 7.7),
                Movie(4, "Маска", "Банківський клерк знаходить магічну маску", 
                      None, ["Комедія"], "1994-07-29", 6.9)
            ]
        }
        return sample_movies.get(genre_name, [])
    
    def get_movie_trailer(self, movie_id):
        """
        Отримання трейлера фільму.
        
        Args:
            movie_id (int): ID фільму
            
        Returns:
            str: URL трейлера або None
        """
        url = f"{self.base_url}/movie/{movie_id}/videos"
        params = {
            'api_key': self.api_key,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for video in data.get('results', []):
                if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                    return f"https://www.youtube.com/watch?v={video.get('key')}"
            
        except requests.exceptions.RequestException as e:
            print(f"Помилка при отриманні трейлера: {e}")
        
        return None
    
    def get_poster_image(self, poster_path):
        """
        Завантаження постеру фільму.
        
        Args:
            poster_path (str): Шлях до постеру
            
        Returns:
            PIL.Image: Зображення постеру або None
        """
        if not poster_path:
            return None
        
        try:
            url = f"{self.image_base_url}{poster_path}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            image = image.resize((200, 300), Image.Resampling.LANCZOS)
            return image
            
        except (requests.exceptions.RequestException, Exception) as e:
            print(f"Помилка при завантаженні постеру: {e}")
            return None


class MovieRecommendationApp:
    """Головний клас додатку для рекомендацій фільмів."""
    
    def __init__(self):
        """Ініціалізація головного вікна додатку."""
        self.root = tk.Tk()
        self.root.title("Рекомендації фільмів")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Ініціалізація компонентів
        self.movie_db = MovieDatabase()
        self.saved_movies = []
        self.watched_movies = []
        self.current_movies = []
        
        # Завантаження збережених даних
        self.load_data()
        
        # Створення інтерфейсу
        self.create_widgets()
        
        # Прив'язка події закриття вікна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Створення всіх віджетів інтерфейсу."""
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="🎬 Рекомендації фільмів", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack()
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Вкладка "Всі фільми"
        self.all_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(self.all_frame, text="Всі фільми")
        
        # Вкладка "Збережені"
        self.saved_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(self.saved_frame, text=f"Збережені ({len(self.saved_movies)})")
        
        # Вкладка "Переглянуті"
        self.watched_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(self.watched_frame, text=f"Переглянуті ({len(self.watched_movies)})")
        
        # Створення вмісту для кожної вкладки
        self.create_all_movies_tab()
        self.create_saved_movies_tab()
        self.create_watched_movies_tab()
    
    def create_all_movies_tab(self):
        """Створення вкладки з усіма фільмами."""
        # Фрейм для вибору жанру
        genre_frame = tk.Frame(self.all_frame, bg='#34495e')
        genre_frame.pack(pady=20)
        
        genre_label = tk.Label(genre_frame, text="Виберіть жанр:", 
                              font=('Arial', 14), fg='#ecf0f1', bg='#34495e')
        genre_label.pack(side=tk.LEFT, padx=10)
        
        self.genre_var = tk.StringVar()
        genre_combo = ttk.Combobox(genre_frame, textvariable=self.genre_var,
                                  values=list(self.movie_db.genres.keys()),
                                  state="readonly", font=('Arial', 12))
        genre_combo.pack(side=tk.LEFT, padx=10)
        genre_combo.bind('<<ComboboxSelected>>', self.on_genre_selected)
        
        # Фрейм для відображення фільмів
        self.movies_frame = tk.Frame(self.all_frame, bg='#34495e')
        self.movies_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Повідомлення за замовчуванням
        default_label = tk.Label(self.movies_frame, 
                                text="Виберіть жанр для перегляду рекомендацій",
                                font=('Arial', 16), fg='#bdc3c7', bg='#34495e')
        default_label.pack(expand=True)
    
    def create_saved_movies_tab(self):
        """Створення вкладки збережених фільмів."""
        self.saved_canvas = tk.Canvas(self.saved_frame, bg='#34495e')
        saved_scrollbar = ttk.Scrollbar(self.saved_frame, orient="vertical", 
                                       command=self.saved_canvas.yview)
        self.saved_scrollable_frame = tk.Frame(self.saved_canvas, bg='#34495e')
        
        self.saved_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.saved_canvas.configure(scrollregion=self.saved_canvas.bbox("all"))
        )
        
        self.saved_canvas.create_window((0, 0), window=self.saved_scrollable_frame, anchor="nw")
        self.saved_canvas.configure(yscrollcommand=saved_scrollbar.set)
        
        self.saved_canvas.pack(side="left", fill="both", expand=True)
        saved_scrollbar.pack(side="right", fill="y")
        
        self.update_saved_movies_display()
    
    def create_watched_movies_tab(self):
        """Створення вкладки переглянутих фільмів."""
        self.watched_canvas = tk.Canvas(self.watched_frame, bg='#34495e')
        watched_scrollbar = ttk.Scrollbar(self.watched_frame, orient="vertical", 
                                         command=self.watched_canvas.yview)
        self.watched_scrollable_frame = tk.Frame(self.watched_canvas, bg='#34495e')
        
        self.watched_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.watched_canvas.configure(scrollregion=self.watched_canvas.bbox("all"))
        )
        
        self.watched_canvas.create_window((0, 0), window=self.watched_scrollable_frame, anchor="nw")
        self.watched_canvas.configure(yscrollcommand=watched_scrollbar.set)
        
        self.watched_canvas.pack(side="left", fill="both", expand=True)
        watched_scrollbar.pack(side="right", fill="y")
        
        self.update_watched_movies_display()
    
    def on_genre_selected(self, event):
        """Обробка вибору жанру."""
        genre = self.genre_var.get()
        if genre:
            self.load_movies_by_genre(genre)
    
    def load_movies_by_genre(self, genre):
        """Завантаження фільмів за вибраним жанром."""
        # Очищення попередніх результатів
        for widget in self.movies_frame.winfo_children():
            widget.destroy()
        
        # Показ індикатора завантаження
        loading_label = tk.Label(self.movies_frame, text="Завантаження...", 
                                font=('Arial', 16), fg='#f39c12', bg='#34495e')
        loading_label.pack(expand=True)
        self.root.update()
        
        # Отримання фільмів
        movies = self.movie_db.get_movies_by_genre(genre)
        self.current_movies = movies
        
        # Очищення індикатора завантаження
        loading_label.destroy()
        
        if not movies:
            no_movies_label = tk.Label(self.movies_frame, 
                                      text="Фільми не знайдено", 
                                      font=('Arial', 16), fg='#e74c3c', bg='#34495e')
            no_movies_label.pack(expand=True)
            return
        
        # Відображення фільмів
        self.display_movies(movies, self.movies_frame)
    
    def display_movies(self, movies, parent_frame):
        """Відображення списку фільмів."""
        # Створення Canvas для прокрутки
        canvas = tk.Canvas(parent_frame, bg='#34495e')
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Відображення кожного фільму
        for i, movie in enumerate(movies):
            movie_frame = tk.Frame(scrollable_frame, bg='#2c3e50', relief=tk.RAISED, bd=2)
            movie_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Назва фільму
            title_label = tk.Label(movie_frame, text=movie.title, 
                                  font=('Arial', 14, 'bold'), 
                                  fg='#ecf0f1', bg='#2c3e50')
            title_label.pack(anchor=tk.W, padx=10, pady=5)
            
            # Інформація про фільм
            info_text = f"Рік: {movie.release_date[:4] if movie.release_date else 'Невідомо'} | "
            info_text += f"Рейтинг: {movie.vote_average}/10 | "
            info_text += f"Жанри: {', '.join(movie.genre_names)}"
            
            info_label = tk.Label(movie_frame, text=info_text, 
                                 font=('Arial', 10), fg='#bdc3c7', bg='#2c3e50')
            info_label.pack(anchor=tk.W, padx=10)
            
            # Кнопка "Детальніше"
            detail_btn = tk.Button(movie_frame, text="Детальніше", 
                                  font=('Arial', 10),
                                  bg='#3498db', fg='white',
                                  command=lambda m=movie: self.show_movie_details(m))
            detail_btn.pack(anchor=tk.E, padx=10, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_movie_details(self, movie):
        """Відображення детальної інформації про фільм."""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Деталі: {movie.title}")
        detail_window.geometry("600x700")
        detail_window.configure(bg='#2c3e50')
        
        # Основний фрейм з прокруткою
        main_frame = tk.Frame(detail_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Назва фільму
        title_label = tk.Label(main_frame, text=movie.title, 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Інформація про фільм
        info_frame = tk.Frame(main_frame, bg='#2c3e50')
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"Рік випуску: {movie.release_date[:4] if movie.release_date else 'Невідомо'}\n"
        info_text += f"Рейтинг: {movie.vote_average}/10\n"
        info_text += f"Жанри: {', '.join(movie.genre_names)}"
        
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50',
                             justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # Опис фільму
        desc_label = tk.Label(main_frame, text="Опис:", 
                             font=('Arial', 14, 'bold'), 
                             fg='#ecf0f1', bg='#2c3e50')
        desc_label.pack(anchor=tk.W, pady=(20, 5))
        
        desc_text = scrolledtext.ScrolledText(main_frame, height=8, width=60,
                                             font=('Arial', 11), 
                                             bg='#34495e', fg='#ecf0f1',
                                             wrap=tk.WORD)
        desc_text.pack(fill=tk.X, pady=5)
        desc_text.insert(tk.END, movie.overview)
        desc_text.configure(state='disabled')
        
        # Кнопки дій
        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Кнопка трейлера
        trailer_btn = tk.Button(buttons_frame, text="🎥 Дивитись трейлер", 
                               font=('Arial', 12),
                               bg='#e74c3c', fg='white',
                               command=lambda: self.watch_trailer(movie))
        trailer_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка збереження
        save_text = "💾 Видалити зі збережених" if movie.is_saved else "💾 Зберегти"
        save_btn = tk.Button(buttons_frame, text=save_text, 
                            font=('Arial', 12),
                            bg='#27ae60' if not movie.is_saved else '#e67e22', 
                            fg='white',
                            command=lambda: self.toggle_save_movie(movie, save_btn, detail_window))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "переглянуто"
        watched_text = "👁 Видалити з переглянутих" if movie.is_watched else "👁 Позначити як переглянуте"
        watched_btn = tk.Button(buttons_frame, text=watched_text, 
                               font=('Arial', 12),
                               bg='#9b59b6' if not movie.is_watched else '#e67e22', 
                               fg='white',
                               command=lambda: self.toggle_watched_movie(movie, watched_btn, detail_window))
        watched_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка оновлення
        refresh_btn = tk.Button(buttons_frame, text="🔄 Оновити", 
                               font=('Arial', 12),
                               bg='#f39c12', fg='white',
                               command=lambda: self.refresh_movie_info(movie, detail_window))
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Завантаження постеру (якщо доступний)
        if movie.poster_path:
            self.load_poster(movie, main_frame)
    
    def load_poster(self, movie, parent_frame):
        """Завантаження та відображення постеру фільму."""
        try:
            poster_image = self.movie_db.get_poster_image(movie.poster_path)
            if poster_image:
                poster_photo = ImageTk.PhotoImage(poster_image)
                poster_label = tk.Label(parent_frame, image=poster_photo, bg='#2c3e50')
                poster_label.image = poster_photo  # Зберігаємо посилання
                poster_label.pack(pady=10)
        except Exception as e:
            print(f"Помилка завантаження постеру: {e}")
    
    def watch_trailer(self, movie):
        """Відкриття трейлера фільму."""
        trailer_url = self.movie_db.get_movie_trailer(movie.movie_id)
        if trailer_url:
            webbrowser.open(trailer_url)
        else:
            messagebox.showinfo("Інформація", "Трейлер не знайдено")
    
    def toggle_save_movie(self, movie, button, window):
        """Збереження/видалення фільму зі збережених."""
        if movie.is_saved:
            # Видаляємо зі збережених
            self.saved_movies = [m for m in self.saved_movies if m.movie_id != movie.movie_id]
            movie.is_saved = False
            button.configure(text="💾 Зберегти", bg='#27ae60')
        else:
            # Додаємо до збережених
            movie.is_saved = True
            if movie not in self.saved_movies:
                self.saved_movies.append(movie)
            button.configure(text="💾 Видалити зі збережених", bg='#e67e22')
        
        self.update_saved_movies_display()
        self.update_tab_counts()
        self.save_data()
    
    def toggle_watched_movie(self, movie, button, window):
        """Позначення фільму як переглянутого/не переглянутого."""
        if movie.is_watched:
            # Видаляємо з переглянутих
            self.watched_movies = [m for m in self.watched_movies if m.movie_id != movie.movie_id]
            movie.is_watched = False
            button.configure(text="👁 Позначити як переглянуте", bg='#9b59b6')
        else:
            # Додаємо до переглянутих
            movie.is_watched = True
            if movie not in self.watched_movies:
                self.watched_movies.append(movie)
            button.configure(text="👁 Видалити з переглянутих", bg='#e67e22')
        
        self.update_watched_movies_display()
        self.update_tab_counts()
        self.save_data()
    
    def refresh_movie_info(self, movie, window):
        """Оновлення інформації про фільм."""
        messagebox.showinfo("Оновлено", f"Інформація про фільм '{movie.title}' оновлена!")
    
    def update_saved_movies_display(self):
        """Оновлення відображення збережених фільмів."""
        # Очищення попереднього вмісту
        for widget in self.saved_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.saved_movies:
            no_saved_label = tk.Label(self.saved_scrollable_frame, 
                                     text="Немає збережених фільмів", 
                                     font=('Arial', 16), fg='#bdc3c7', bg='#34495e')
            no_saved_label.pack(expand=True, pady=50)
        else:
            for movie in self.saved_movies:
                self.create_movie_card(movie, self.saved_scrollable_frame)
    
    def update_watched_movies_display(self):
        """Оновлення відображення переглянутих фільмів."""
        # Очищення попереднього вмісту
        for widget in self.watched_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.watched_movies:
            no_watched_label = tk.Label(self.watched_scrollable_frame, 
                                       text="Немає переглянутих фільмів", 
                                       font=('Arial', 16), fg='#bdc3c7', bg='#34495e')
            no_watched_label.pack(expand=True, pady=50)
        else:
            for movie in self.watched_movies:
                self.create_movie_card(movie, self.watched_scrollable_frame)
    
    def create_movie_card(self, movie, parent):
        """Створення картки фільму."""
        card_frame = tk.Frame(parent, bg='#2c3e50', relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Назва фільму
        title_label = tk.Label(card_frame, text=movie.title, 
                              font=('Arial', 14, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Інформація про фільм
        info_text = f"Рік: {movie.release_date[:4] if movie.release_date else 'Невідомо'} | "
        info_text += f"Рейтинг: {movie.vote_average}/10"
        
        info_label = tk.Label(card_frame, text=info_text, 
                             font=('Arial', 10), fg='#bdc3c7', bg='#2c3e50')
        info_label.pack(anchor=tk.W, padx=10)
        
        # Кнопка "Детальніше"
        detail_btn = tk.Button(card_frame, text="Детальніше", 
                              font=('Arial', 10),
                              bg='#3498db', fg='white',
                              command=lambda: self.show_movie_details(movie))
        detail_btn.pack(anchor=tk.E, padx=10, pady=5)
    
    def update_tab_counts(self):
        """Оновлення лічильників у назвах вкладок."""
        self.notebook.tab(1, text=f"Збережені ({len(self.saved_movies)})")
        self.notebook.tab(2, text=f"Переглянуті ({len(self.watched_movies)})")
    
    def save_data(self):
        """Збереження даних у файл."""
        data = {
            'saved_movies': [movie.to_dict() for movie in self.saved_movies],
            'watched_movies': [movie.to_dict() for movie in self.watched_movies]
        }
        
        try:
            with open('movie_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка збереження даних: {e}")
    
    def load_data(self):
        """Завантаження збережених даних з файлу."""
        if not os.path.exists('movie_data.json'):
            return
        
        try:
            with open('movie_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.saved_movies = [Movie.from_dict(movie_data) 
                               for movie_data in data.get('saved_movies', [])]
            self.watched_movies = [Movie.from_dict(movie_data) 
                                 for movie_data in data.get('watched_movies', [])]
        except Exception as e:
            print(f"Помилка завантаження даних: {e}")
    
    def on_closing(self):
        """Обробка закриття програми."""
        self.save_data()
        self.root.destroy()
    
    def run(self):
        """Запуск головного циклу програми."""
        self.root.mainloop()


def main():
    """Головна функція запуску програми."""
    try:
        # Перевірка наявності необхідних модулів
        import PIL
        print("Запуск додатку рекомендацій фільмів...")
        
        # Створення та запуск додатку
        app = MovieRecommendationApp()
        app.run()
        
    except ImportError as e:
        print("Помилка: Відсутні необхідні модулі.")
        print("Встановіть необхідні пакети командою:")
        print("pip install pillow requests")
        print(f"Деталі помилки: {e}")
    except Exception as e:
        print(f"Помилка запуску програми: {e}")


if __name__ == "__main__":
    main()