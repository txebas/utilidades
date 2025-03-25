import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import time
import threading  # Import the threading module

class FolderAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Carpetas")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")  # Fondo claro

        # Estilos
        self.style = ttk.Style()
        # Estilo para los botones: azul oscuro y texto negro
        self.style.configure("TButton", padding=6, relief="flat", background="#003366", foreground="black", font=("Arial", 10)) # Azul oscuro: #003366
        self.style.map("TButton", background=[("active", "#002244")]) # Azul más oscuro al pasar el ratón
        self.style.configure("TLabel", background="#f0f0f0", foreground="black") #texto negro
        self.style.configure("Treeview.Heading", background="#4CAF50", foreground="black", font=("Arial", 10, "bold")) #texto negro
        self.style.configure("Treeview", rowheight=25)

        # Frame principal
        self.main_frame = Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=BOTH, expand=1, padx=10, pady=10)

        # Canvas y scrollbar
        self.canvas = Canvas(self.main_frame, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#f0f0f0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame de botones y selección
        self.button_frame = Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=X, pady=5, padx=10)

        self.select_button = ttk.Button(self.button_frame, text="Seleccionar Carpeta", command=self.select_folder)
        self.select_button.pack(side=LEFT, padx=5)

        self.scan_button = ttk.Button(self.button_frame, text="Escanear Carpetas", command=self.start_scan_thread) #cambiado
        self.scan_button.pack(side=LEFT, padx=5)

        self.sort_name_button = ttk.Button(self.button_frame, text="Ordenar por Nombre", command=self.sort_by_name)
        self.sort_name_button.pack(side=LEFT, padx=5)

        self.sort_size_button = ttk.Button(self.button_frame, text="Ordenar por Tamaño", command=self.sort_by_size)
        self.sort_size_button.pack(side=LEFT, padx=5)

        # Etiqueta para mostrar la carpeta seleccionada
        self.folder_label = ttk.Label(self.button_frame, text="Carpeta seleccionada: Ninguna")
        self.folder_label.pack(side=LEFT, padx=10)

        # Treeview para mostrar resultados
        self.tree = ttk.Treeview(self.scrollable_frame, columns=("Ruta", "Tamaño"), show="headings")
        self.tree.heading("Ruta", text="Ruta de la Carpeta")
        self.tree.heading("Tamaño", text="Tamaño (bytes)")
        self.tree.column("Ruta", width=500)
        self.tree.column("Tamaño", width=200)
        self.tree.pack(fill=BOTH, expand=1, padx=10, pady=10)

        # Empaquetar canvas y scrollbar
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

        # Barra de progreso
        self.progress_frame = Frame(self.root, bg="#f0f0f0")
        self.progress_frame.pack(fill=X, padx=10, pady=(0,10))
        self.progress_label = ttk.Label(self.progress_frame, text="Progreso:", style="TLabel")
        self.progress_label.pack(side=LEFT)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side=LEFT, padx=10)

        self.folders = []  # Lista para almacenar la info de las carpetas
        self.selected_folder = None  # Carpeta seleccionada por el usuario

    def get_folder_size(self, folder_path):
        """Calcula el tamaño total de una carpeta en bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"Error al calcular tamaño de {folder_path}: {e}")
        return total_size

    def select_folder(self):
        """Abre un diálogo para seleccionar la carpeta inicial"""
        self.selected_folder = filedialog.askdirectory(
            title="Selecciona una carpeta",
            initialdir=str(Path.home())  # Comienza en el directorio home por defecto
        )
        if self.selected_folder:
            self.folder_label.config(text=f"Carpeta seleccionada: {self.selected_folder}")
        else:
            self.folder_label.config(text="Carpeta seleccionada: Ninguna")

    def scan_folders(self):
        """Escanea las carpetas y subcarpetas de la carpeta seleccionada con barra de progreso"""
        if not self.selected_folder:
            self.folder_label.config(text="Por favor, selecciona una carpeta primero")
            return

        # Limpiar treeview anterior
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.folders = []

        try:
            # Contar total de carpetas para la barra de progreso
            total_folders = sum(len(dirnames) for dirpath, dirnames, _ in os.walk(self.selected_folder))
            self.progress_bar["maximum"] = total_folders
            self.progress_bar["value"] = 0
            self.progress_label.config(text=f"Progreso: 0/{total_folders}")
            self.root.update_idletasks()

            # Escanear con barra de progreso
            scanned_folders = 0
            for dirpath, dirnames, _ in os.walk(self.selected_folder):
                for dirname in dirnames:
                    full_path = os.path.join(dirpath, dirname)
                    size = self.get_folder_size(full_path)
                    self.folders.append((full_path, size))
                    scanned_folders += 1
                    self.progress_bar["value"] = scanned_folders
                    self.progress_label.config(text=f"Progreso: {scanned_folders}/{total_folders}")
                    self.root.update_idletasks()
                    time.sleep(0.01) #pequeño delay para que se vea el progreso

            # Mostrar resultados iniciales
            for folder_path, size in self.folders:
                self.tree.insert("", "end", values=(folder_path, size))

        except Exception as e:
            print(f"Error al escanear: {e}")
        finally:
            self.progress_bar["value"] = 0
            self.progress_label.config(text="Progreso:")
            self.root.update_idletasks()
    
    def start_scan_thread(self):
        """Starts the scan_folders method in a separate thread."""
        thread = threading.Thread(target=self.scan_folders)
        thread.daemon = True  # Allow the program to exit even if the thread is running
        thread.start()

    def sort_by_name(self):
        """Ordena las carpetas por nombre"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        sorted_folders = sorted(self.folders, key=lambda x: x[0])

        for folder_path, size in sorted_folders:
            self.tree.insert("", "end", values=(folder_path, size))

    def sort_by_size(self):
        """Ordena las carpetas por tamaño"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        sorted_folders = sorted(self.folders, key=lambda x: x[1], reverse=True)

        for folder_path, size in sorted_folders:
            self.tree.insert("", "end", values=(folder_path, size))


def main():
    root = Tk()
    app = FolderAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
