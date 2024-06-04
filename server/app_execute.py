import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter
import os
from server.libs.function import receipt_check

FONT_TYPE = "meiryo"
PRIMARY = "blue"
BACK_COLOR = "dark"
FONT_COLOR = "white"
FORM_SIZE = "1440x1080"


class ReadCsvFrame(customtkinter.CTkFrame):
    def __init__(self, master, header_name, placeholder_text, **kwargs):
        super().__init__(master, **kwargs)
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.file_path = None

        self.grid_columnconfigure(0, weight=1)
        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.textbox = customtkinter.CTkEntry(self, placeholder_text=placeholder_text, width=120, font=self.fonts)
        self.textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.button_select = customtkinter.CTkButton(self, command=self.button_select_callback, text="ファイルを選択",
                                                     fg_color="transparent", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), font=self.fonts)
        self.button_select.grid(row=1, column=1, padx=10, pady=(0, 10))

    def button_select_callback(self):
        file_name = self.file_read()
        if file_name or file_name == "":  # ファイル選択がキャンセルされた場合、file_name は空文字列となる
            if file_name:
                self.file_path = file_name  # 新しいファイルパスを設定
                self.textbox.delete(0, tk.END)
                self.textbox.insert(0, file_name)
            else:
                # キャンセルされた場合、テキストボックスは元のパスを表示
                self.textbox.delete(0, tk.END)
                if self.file_path:
                    self.textbox.insert(0, self.file_path)

    @staticmethod
    def file_read():
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")], initialdir=current_dir)
        return file_path


class ReadReceiptCsvFrame(ReadCsvFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, header_name="Ibowから出力したCSVファイルを選択", placeholder_text="ファイルが選択されていません",
                         **kwargs)


class DataDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = ("Arial", 15)
        self.result_df = None

        self.setup_form()

    def setup_form(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="不整合データ", font=("Arial", 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky="nsew")

        self.scroll_y = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
        self.scroll_y.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.tree.xview)
        self.scroll_x.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.tree.configure(xscrollcommand=self.scroll_x.set)

        self.button_download = customtkinter.CTkButton(master=self, command=self.download_csv,
                                                       text="CSV形式でダウンロード",
                                                       font=self.fonts)
        self.button_download.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold", "underline"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

    def display_text(self, text):
        for column in self.tree.get_children():
            self.tree.delete(column)

        self.tree["columns"] = ["message"]
        self.tree.heading("message", text=text)
        self.tree.column("message", width=100)

    def display_dataframe(self, df):
        for column in self.tree.get_children():
            self.tree.delete(column)

        if df is None:
            self.display_text("表示するデータがありません")
            return
        if df.shape[0] == 0:
            self.display_text("不整合データはありません")
            return

        self.tree["columns"] = list(df.columns)
        # スタイルの設定
        style = ttk.Style()
        style.theme_use("default")

        for col in df.columns:
            print(col)
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for index, row in df.iterrows():
            print(row)
            self.tree.insert("", tk.END, values=list(row))

        self.result_df = df


    def download_csv(self):
        if self.result_df is None:
            self.display_text("表示するデータがありません")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSVファイル", "*.csv")])
        if save_path:
            self.result_df.to_csv(save_path, index=False)
            messagebox.showinfo("情報", f"CSVファイルが保存されました: {save_path}")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 15)
        self.geometry(FORM_SIZE)
        self.title("CSV input")
        self.setup_form()

    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.receipt_frame = ReadReceiptCsvFrame(self)
        self.receipt_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")


        self.button_execute = customtkinter.CTkButton(self, text="照合", command=self.button_execute_callback,
                                                      font=self.fonts)
        self.button_execute.grid(row=2, column=0, padx=20, pady=(10, 20))

        self.data_display_frame = DataDisplayFrame(self)
        self.data_display_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

    def button_execute_callback(self):
        self.data_display_frame.display_dataframe(None)
        receipt_file = self.receipt_frame.file_path
        if not receipt_file:
            messagebox.showwarning("エラー", "ファイルが選択されていません")
            return
        try:
            result_df = receipt_check(receipt_file)
            print(result_df)
            self.data_display_frame.display_dataframe(result_df)
        finally:
            result_df = None
            self.receipt_frame.file_path = None
            self.receipt_frame.textbox.delete(0, tk.END)
            self.receipt_frame.textbox.insert(0, "ファイルが選択されていません")



if __name__ == "__main__":
    app = App()
    app.mainloop()
