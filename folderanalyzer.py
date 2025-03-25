import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from tqdm import tqdm

class FolderAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Carpetas")
        self.root.geometry("800x600")

        # Frame principal
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=1)

        # Canvas y scrollbar
        self.canvas = Canvas(self.main_frame)
        self.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame de botones y selección
        self.button_frame = Frame(self.root)
        self.button_frame.pack(fill=X, pady=5)

        self.select_button = Button(self.button_frame, text="Seleccionar Carpeta", command=self.select_folder)
        self.select_button.pack(side=LEFT, padx=5)
        
        self.scan_button = Button(self.button_frame, text="Escanear Carpetas", command=self.scan_folders)
        self.scan_button.pack(side=LEFT, padx=5)
        
        self.sort_name_button = Button(self.button_frame, text="Ordenar por Nombre", command=self.sort_by_name)
        self.sort_name_button.pack(side=LEFT, padx=5)
        
        self.sort_size_button = Button(self.button_frame, text="Ordenar por Tamaño", command=self.sort_by_size)
        self.sort_size_button.pack(side=LEFT, padx=5)

        # Etiqueta para mostrar la carpeta seleccionada
        self.folder_label = Label(self.button_frame, text="Carpeta seleccionada: Ninguna")
        self.folder_label.pack(side=LEFT, padx=10)

        # Treeview para mostrar resultados
        self.tree = ttk.Treeview(self.scrollable_frame, columns=("Ruta", "Tamaño"), show="headings")
        self.tree.heading("Ruta", text="Ruta de la Carpeta")
        self.tree.heading("Tamaño", text="Tamaño (bytes)")
        self.tree.column("Ruta", width=500)
        self.tree.column("Tamaño", width=200)
        self.tree.pack(fill=BOTH, expand=1)

        # Empaquetar canvas y scrollbar
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

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
            
            # Escanear con barra de progreso
            with tqdm(total=total_folders, desc="Escaneando carpetas") as pbar:
                for dirpath, dirnames, _ in os.walk(self.selected_folder):
                    for dirname in dirnames:
                        full_path = os.path.join(dirpath, dirname)
                        size = self.get_folder_size(full_path)
                        self.folders.append((full_path, size))
                        pbar.update(1)
                        self.root.update()  # Actualizar la interfaz gráfica
            
            # Mostrar resultados iniciales
            for folder_path, size in self.folders:
                self.tree.insert("", "end", values=(folder_path, size))
                
        except Exception as e:
            print(f"Error al escanear: {e}")

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