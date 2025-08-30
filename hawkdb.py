"""
HawkDB - Sistema de Consulta e Exportação de Dados
==================================================
Sistema otimizado para consulta a bancos de dados MySQL com exportação
em múltiplos formatos (CSV, XLSX, SQL INSERT).

Autor: Refatorado por Engenheiro de Software Sênior
Versão: 2.3 (Ajustes de segurança e persistência)
"""

import mysql.connector
import pandas as pd
import datetime
import threading
import time
import os
import configparser
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from tkinter import (
    Tk, ttk, StringVar, messagebox, filedialog, Text, Label,
    DISABLED, NORMAL, OptionMenu, PhotoImage
)


class DatabaseConnection:
    """Gerencia conexões com banco de dados MySQL."""
    
    def __init__(self):
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursor] = None
        self.is_connected = False
    
    def connect(self, host: str, user: str, password: str, port: int = 3306) -> bool:
        """
        Estabelece conexão com o banco de dados.
        """
        if self.is_connected:
            self.disconnect()
            
        connection_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'connect_timeout': 10,
            'autocommit': True
        }
        
        try:
            self.connection = mysql.connector.connect(**connection_config)
        except mysql.connector.Error:
            connection_config['ssl_disabled'] = True
            self.connection = mysql.connector.connect(**connection_config)
        
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT VERSION()")
        self.cursor.fetchone()
        
        self.is_connected = True
        return True
    
    def disconnect(self) -> None:
        """Encerra a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[List[str], List[Tuple]]:
        """
        Executa uma consulta SQL.
        """
        if not self.is_connected:
            raise RuntimeError("Não conectado ao banco de dados")
            
        self.cursor.execute(query)
        column_names = [col[0] for col in self.cursor.description]
        data = self.cursor.fetchall()
        
        return column_names, data
    
    def get_server_info(self) -> Optional[str]:
        """Retorna informações do servidor."""
        if not self.is_connected:
            return None
            
        self.cursor.execute("SELECT VERSION()")
        version = self.cursor.fetchone()
        return version[0] if version else "Desconhecida"


class DataExporter:
    """Classe responsável pela exportação de dados em diferentes formatos."""
    
    @staticmethod
    def to_csv(data: List[Tuple], columns: List[str], filename: str) -> None:
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(filename, index=False, encoding='utf-8')
    
    @staticmethod
    def to_excel(data: List[Tuple], columns: List[str], filename: str) -> None:
        df = pd.DataFrame(data, columns=columns)
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
    
    @staticmethod
    def to_sql_insert(data: List[Tuple], columns: List[str], filename: str, table_name: str = "<table_name>") -> None:
        columns_str = ', '.join(columns)
        with open(filename, 'w', encoding='utf-8') as f:
            for record in data:
                formatted_values = []
                for value in record:
                    if value is None:
                        formatted_values.append('NULL')
                    elif isinstance(value, str):
                        escaped_value = value.replace("'", "''")
                        formatted_values.append(f"'{escaped_value}'")
                    elif isinstance(value, datetime.datetime):
                        formatted_values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif isinstance(value, datetime.date):
                        formatted_values.append(f"'{value.strftime('%Y-%m-%d')}'")
                    else:
                        formatted_values.append(str(value))
                
                values_str = ', '.join(formatted_values)
                sql_insert = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n"
                f.write(sql_insert)


class ConnectionManager:
    """Gerencia configurações de conexão salvas."""
    
    def __init__(self, config_file: str = 'data/hawkdb_config.ini'): # <-- MUDANÇA AQUI
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self._ensure_config_exists()
    
    def _ensure_config_exists(self) -> None:
        """Cria arquivo de configuração se não existir."""
        # Garante que o diretório pai exista
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self.config['DEFAULT'] = {}
            self.config['Conexao_Exemplo'] = {
                'host': '',
                'user': '',
                'password': ''
            }
            self._save_config()
    
    def _save_config(self) -> None:
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_connections(self) -> List[str]:
        self.config.read(self.config_file, encoding='utf-8')
        return [section for section in self.config.sections() if section != 'DEFAULT']
    
    def save_connection(self, name: str, host: str, user: str, password: str) -> None:
        self.config[name] = {'host': host, 'user': user, 'password': password}
        self._save_config()
    
    def load_connection(self, name: str) -> Optional[Dict[str, str]]:
        self.config.read(self.config_file, encoding='utf-8')
        if name in self.config:
            return dict(self.config[name])
        return None
    
    def delete_connection(self, name: str) -> bool:
        self.config.read(self.config_file, encoding='utf-8')
        if name in self.config:
            self.config.remove_section(name)
            self._save_config()
            return True
        return False


class HawkDBApp:
    """Aplicação principal do HawkDB."""
    
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("HawkDB - Sistema de Consulta e Exportação")
        self.root.geometry("800x600")
        
        self.db_connection = DatabaseConnection()
        self.connection_manager = ConnectionManager()
        self.data_exporter = DataExporter()
        
        self.current_data: List[Tuple] = []
        self.current_columns: List[str] = []
        self.fetch_start_time: Optional[float] = None
        
        self._setup_ui()
        self._load_icon()
    
    def _load_icon(self) -> None:
        try:
            icon_path = Path("hawkdb_icon.png")
            if icon_path.exists():
                icon = PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon)
                self.icon_reference = icon
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")
    
    def _setup_ui(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self._setup_connection_tab()
        self._setup_query_tab()
    
    def _setup_connection_tab(self) -> None:
        self.connection_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.connection_tab, text='Configurar Conexão')
        
        title_frame = ttk.Frame(self.connection_tab)
        title_frame.pack(pady=20)
        ttk.Label(title_frame, text="🦅 HawkDB - Sistema de Consulta e Exportação", font=('Arial', 16, 'bold')).pack()
        
        self._setup_saved_connections_section()
        self._setup_connection_details_section()
        self._setup_connection_buttons()
    
    def _setup_saved_connections_section(self) -> None:
        saved_frame = ttk.LabelFrame(self.connection_tab, text="Conexões Salvas")
        saved_frame.pack(fill='x', padx=20, pady=10)
        
        connections_row = ttk.Frame(saved_frame)
        connections_row.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(connections_row, text="Conexões:").pack(side='left')
        
        self.saved_connections_var = StringVar(value="Selecione uma conexão...")
        self.connections_dropdown = ttk.Combobox(connections_row, textvariable=self.saved_connections_var, state='readonly')
        self.connections_dropdown.pack(side='left', fill='x', expand=True, padx=5)
        self.connections_dropdown.bind('<<ComboboxSelected>>', self._on_connection_selected)
        
        buttons_frame = ttk.Frame(connections_row)
        buttons_frame.pack(side='right', padx=5)
        
        ttk.Button(buttons_frame, text="Carregar", command=self._load_selected_connection).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="Deletar", command=self._delete_connection).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="Limpar", command=self._clear_connection_fields).pack(side='left', padx=2)
        
        self._update_connections_dropdown()
    
    def _setup_connection_details_section(self) -> None:
        details_frame = ttk.LabelFrame(self.connection_tab, text="Detalhes da Conexão")
        details_frame.pack(fill='x', padx=20, pady=10)
        
        fields = [("Host:", "host_var"), ("Usuário:", "user_var"), ("Senha:", "password_var"), ("Nome da Conexão:", "connection_name_var")]
        
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(details_frame, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            var = StringVar()
            setattr(self, var_name, var)
            
            if "senha" in label_text.lower():
                entry = ttk.Entry(details_frame, textvariable=var, show='*', width=40)
                show_btn = ttk.Button(details_frame, text="👁️", width=3, command=lambda e=entry: self._toggle_password_visibility(e))
                show_btn.grid(row=i, column=2, padx=5, pady=5)
            else:
                entry = ttk.Entry(details_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
        
        ttk.Button(details_frame, text="Salvar Conexão", command=self._save_connection).grid(row=len(fields), column=1, pady=10, sticky='e')
        details_frame.grid_columnconfigure(1, weight=1)
    
    def _setup_connection_buttons(self) -> None:
        buttons_frame = ttk.Frame(self.connection_tab)
        buttons_frame.pack(pady=20)
        self.connect_button = ttk.Button(buttons_frame, text="Conectar ao Banco", command=self._connect_database)
        self.connect_button.pack(side='left', padx=10)
        self.disconnect_button = ttk.Button(buttons_frame, text="Desconectar", command=self._disconnect_database, state=DISABLED)
        self.disconnect_button.pack(side='left', padx=10)
    
    def _setup_query_tab(self) -> None:
        self.query_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.query_tab, text='Executar Consultas')
        
        query_frame = ttk.LabelFrame(self.query_tab, text="Consulta SQL")
        query_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.query_text = Text(query_frame, height=8, font=('Consolas', 10))
        self.query_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        actions_frame = ttk.Frame(query_frame)
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        self.execute_button = ttk.Button(actions_frame, text="Executar Consulta", command=self._execute_query)
        self.execute_button.pack(side='left', padx=5)
        
        export_formats = ["CSV", "Excel (XLSX)", "SQL INSERT"]
        self.export_format_var = StringVar(value=export_formats[0])
        ttk.Label(actions_frame, text="Formato:").pack(side='left', padx=(20, 5))
        ttk.Combobox(actions_frame, textvariable=self.export_format_var, values=export_formats, state='readonly', width=15).pack(side='left', padx=5)
        
        self.export_button = ttk.Button(actions_frame, text="Exportar Dados", command=self._export_data)
        self.export_button.pack(side='left', padx=5)
        
        results_frame = ttk.LabelFrame(self.query_tab, text="Último Registro")
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.results_text = Text(results_frame, height=8, state=DISABLED, font=('Consolas', 9))
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.status_label = ttk.Label(self.query_tab, text="Pronto", foreground="green")
        self.status_label.pack(side='right', padx=20, pady=10)
    
    def _toggle_password_visibility(self, entry: ttk.Entry) -> None:
        entry.config(show='' if entry.cget('show') == '*' else '*')
    
    def _update_connections_dropdown(self) -> None:
        connections = self.connection_manager.get_connections()
        self.connections_dropdown['values'] = ["Selecione uma conexão..."] + connections
        self.saved_connections_var.set("Selecione uma conexão...")
    
    def _on_connection_selected(self, event=None) -> None:
        selected = self.saved_connections_var.get()
        if selected != "Selecione uma conexão...":
            self._load_selected_connection()
    
    def _load_selected_connection(self) -> None:
        selected = self.saved_connections_var.get()
        if selected == "Selecione uma conexão...": return
        conn_data = self.connection_manager.load_connection(selected)
        if conn_data:
            self.host_var.set(conn_data['host'])
            self.user_var.set(conn_data['user'])
            self.password_var.set(conn_data['password'])
            self.connection_name_var.set(selected)
    
    def _save_connection(self) -> None:
        name, host, user, password = (self.connection_name_var.get().strip(), self.host_var.get().strip(), 
                                      self.user_var.get().strip(), self.password_var.get().strip())
        if not all([name, host, user]): messagebox.showerror("Erro", "Nome da conexão, host e usuário são obrigatórios."); return
        self.connection_manager.save_connection(name, host, user, password)
        messagebox.showinfo("Sucesso", f"Conexão '{name}' salva com sucesso!")
        self._update_connections_dropdown()
        self.connection_name_var.set("")
    
    def _delete_connection(self) -> None:
        selected = self.saved_connections_var.get()
        if selected == "Selecione uma conexão...": messagebox.showwarning("Aviso", "Selecione uma conexão para deletar."); return
        if messagebox.askyesno("Confirmar", f"Deletar conexão '{selected}'?"):
            if self.connection_manager.delete_connection(selected):
                messagebox.showinfo("Sucesso", "Conexão deletada com sucesso!")
                self._update_connections_dropdown()
                self._clear_connection_fields()
    
    def _clear_connection_fields(self) -> None:
        self.host_var.set(""), self.user_var.set(""), self.password_var.set(""), self.connection_name_var.set("")
        self.saved_connections_var.set("Selecione uma conexão...")
    
    def _parse_host_port(self, host_str: str) -> Tuple[str, int]:
        if ':' in host_str:
            parts = host_str.rsplit(':', 1)
            try: return parts[0].strip(), int(parts[1].strip())
            except (ValueError, IndexError): raise ValueError("Formato inválido. Use: host ou host:porta")
        return host_str.strip(), 3306
    
    def _connect_database(self) -> None:
        host, user, password = self.host_var.get().strip(), self.user_var.get().strip(), self.password_var.get().strip()
        if not all([host, user]): messagebox.showerror("Erro", "Host e usuário são obrigatórios."); return
        try:
            host_name, port = self._parse_host_port(host)
            self.db_connection.connect(host_name, user, password, port)
            server_info = self.db_connection.get_server_info()
            messagebox.showinfo("Conectado", f"Conexão estabelecida!\nServidor: {host_name}:{port}\nVersão MySQL: {server_info}")
            self.connect_button.config(state=DISABLED)
            self.disconnect_button.config(state=NORMAL)
        except (ValueError, mysql.connector.Error) as e:
            self._handle_connection_error(e, host_name, port, user)
    
    def _handle_connection_error(self, error, host, port, user):
        error_code = getattr(error, 'errno', 'N/A')
        error_messages = {2003: "Servidor não encontrado", 1045: "Usuário ou senha incorretos"}
        specific_msg = error_messages.get(error_code, "Erro de conexão")
        full_msg = f"Erro ao conectar:\nHost: {host}:{port}\nUsuário: {user}\nCódigo: {error_code} - {specific_msg}"
        messagebox.showerror("Erro de Conexão", full_msg)
    
    def _disconnect_database(self) -> None:
        self.db_connection.disconnect()
        messagebox.showinfo("Desconectado", "Desconexão realizada com sucesso.")
        self.connect_button.config(state=NORMAL)
        self.disconnect_button.config(state=DISABLED)
    
    def _execute_query(self) -> None:
        if not self.db_connection.is_connected: messagebox.showerror("Erro", "Conecte-se ao banco de dados primeiro."); return
        query = self.query_text.get("1.0", "end-1c").strip()
        if not query: messagebox.showwarning("Aviso", "Digite uma consulta SQL."); return
        
        self._toggle_interface(False)
        self.status_label.config(text="Executando consulta...", foreground="orange")
        self.fetch_start_time = time.time()
        threading.Thread(target=self._execute_query_thread, args=(query,), daemon=True).start()
    
    def _execute_query_thread(self, query: str) -> None:
        try:
            self.current_columns, self.current_data = self.db_connection.execute_query(query)
            elapsed_time = time.time() - self.fetch_start_time
            self.root.after(0, self._query_completed, len(self.current_data), elapsed_time)
        except Exception as e:
            self.root.after(0, self._query_failed, str(e))
    
    def _query_completed(self, record_count: int, elapsed_time: float) -> None:
        self._toggle_interface(True)
        status_msg = f"Concluído. Registros: {record_count}. Tempo: {elapsed_time:.2f}s"
        self.status_label.config(text=status_msg, foreground="green")
        if self.current_data: self._display_last_record()
        messagebox.showinfo("Consulta Concluída", f"Consulta executada com sucesso!\nRegistros encontrados: {record_count}")
    
    def _query_failed(self, error_msg: str) -> None:
        self._toggle_interface(True)
        self.status_label.config(text="Erro na consulta", foreground="red")
        messagebox.showerror("Erro na Consulta", f"Erro ao executar consulta:\n{error_msg}")
    
    def _display_last_record(self) -> None:
        if not self.current_data: return
        last_record = self.current_data[-1]
        self.results_text.config(state=NORMAL)
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", "Último registro encontrado:\n\n")
        for col_name, value in zip(self.current_columns, last_record):
            self.results_text.insert("end", f"{col_name}: {value}\n")
        self.results_text.config(state=DISABLED)
    
    def _export_data(self) -> None:
        if not self.current_data: messagebox.showwarning("Aviso", "Nenhum dado para exportar."); return
        format_selected = self.export_format_var.get()
        format_config = {
            "CSV": {"extension": ".csv", "filetypes": [("CSV Files", "*.csv")]},
            "Excel (XLSX)": {"extension": ".xlsx", "filetypes": [("Excel Files", "*.xlsx")]},
            "SQL INSERT": {"extension": ".sql", "filetypes": [("SQL Files", "*.sql")]}
        }
        config = format_config[format_selected]
        export_path = Path("/app/exports")
        export_path.mkdir(parents=True, exist_ok=True)
        filename = filedialog.asksaveasfilename(initialdir=export_path, defaultextension=config["extension"], filetypes=config["filetypes"])
        if not filename: return
        try:
            export_method = getattr(self.data_exporter, f"to_{format_selected.split(' ')[0].lower()}")
            export_method(self.current_data, self.current_columns, filename)
            messagebox.showinfo("Exportação Concluída", f"Dados exportados com sucesso para:\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Erro ao exportar dados:\n{str(e)}")
    
    def _toggle_interface(self, enabled: bool) -> None:
        state = NORMAL if enabled else DISABLED
        for widget in [self.execute_button, self.export_button, self.query_text, 
                       self.connect_button if not self.db_connection.is_connected else self.disconnect_button]:
            widget.config(state=state)


def main():
    try:
        root = Tk()
        app = HawkDBApp(root)
        
        root.update_idletasks()
        width, height = root.winfo_width(), root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao inicializar HawkDB:\n{str(e)}")
    finally:
        if 'app' in locals() and hasattr(app, 'db_connection') and app.db_connection.is_connected:
            app.db_connection.disconnect()

if __name__ == "__main__":
    main()
